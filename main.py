import os
import sys
import time
import requests
import asyncio
from datetime import datetime
from googleapiclient.errors import HttpError

# Import local modules
from config import (
    TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, CREDENTIALS_FILE, 
    TOKEN_FILE, DB_FILE, MAX_FILE_SIZE_MB
)
from auth import get_photos_service
from database import Database
from telegram_client import TelegramClient

def download_file(url, destination):
    """Downloads a file from a URL to a destination path."""
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        with open(destination, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return True
    except Exception as e:
        print(f"Error downloading {url}: {e}")
        return False

def get_media_items(service):
    """Generator that yields media items from Google Photos."""
    next_page_token = None
    while True:
        try:
            results = service.mediaItems().list(
                pageSize=100,
                pageToken=next_page_token
            ).execute()
            
            items = results.get('mediaItems', [])
            for item in items:
                yield item
                
            next_page_token = results.get('nextPageToken')
            if not next_page_token:
                break
        except HttpError as e:
            print(f"Error fetching media items: {e}")
            break

async def main():
    # 1. Initialize
    print("Initializing...")
    db = Database(DB_FILE)
    telegram = TelegramClient(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID)
    
    # 2. Authenticate
    print("Authenticating with Google Photos...")
    try:
        service = get_photos_service(CREDENTIALS_FILE, TOKEN_FILE)
    except Exception as e:
        print(f"Authentication failed: {e}")
        return

    # 3. Process Items
    print("Fetching media items...")
    count = 0
    
    # We fetch all items. The API returns them in reverse chronological order usually (newest first),
    # but we want to process them.
    # Note: The API doesn't guarantee order, but usually it's by creation time.
    # To ensure we don't miss anything, we just iterate.
    # Since we have a DB of uploaded IDs, we can just skip existing ones.
    
    for item in get_media_items(service):
        media_id = item['id']
        filename = item.get('filename', 'unknown')
        mime_type = item.get('mimeType', '')
        
        if db.is_uploaded(media_id):
            # print(f"Skipping {filename} (already uploaded)")
            continue
            
        print(f"Processing new item: {filename}")
        
        # Check metadata for size if available (Google Photos API doesn't always provide size directly in list)
        # We might need to rely on the download stream or just try.
        # However, for videos, we should be careful.
        
        # Construct download URL
        # For videos: baseUrl = video stream. For photos: baseUrl = image.
        # We need to append parameters to get the full size.
        base_url = item['baseUrl']
        download_url = f"{base_url}=d" # =d for download original
        
        # Download to temp file
        temp_file = f"temp_{filename}"
        if download_file(download_url, temp_file):
            file_size_mb = os.path.getsize(temp_file) / (1024 * 1024)
            
            if file_size_mb > MAX_FILE_SIZE_MB:
                print(f"Skipping {filename}: Size {file_size_mb:.2f}MB exceeds limit of {MAX_FILE_SIZE_MB}MB")
                os.remove(temp_file)
                # We mark it as uploaded so we don't try to download it again every time?
                # Maybe better to log it separately. For now, let's NOT mark it, so if the user increases limit later it works.
                # Or maybe we should mark it to avoid wasting bandwidth?
                # Let's mark it but maybe log a warning.
                db.add_uploaded(media_id, filename + " (SKIPPED_SIZE)")
                continue
                
            # Upload to Telegram
            success = False
            if mime_type.startswith('image/'):
                success = await telegram.upload_photo(temp_file, caption=filename)
            elif mime_type.startswith('video/'):
                success = await telegram.upload_video(temp_file, caption=filename)
            else:
                print(f"Unknown media type: {mime_type}")
                
            if success:
                print(f"Successfully uploaded {filename}")
                db.add_uploaded(media_id, filename)
                count += 1
            else:
                print(f"Failed to upload {filename}")
            
            # Cleanup
            if os.path.exists(temp_file):
                os.remove(temp_file)
                
            # Rate limiting to be nice to API
            time.sleep(1)
            
    print(f"Finished. Uploaded {count} new items.")
    db.close()

if __name__ == '__main__':
    asyncio.run(main())
