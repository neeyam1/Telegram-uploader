import os
import time
import asyncio
import hashlib
from datetime import datetime

# Import local modules
from config import (
    TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, DB_FILE, 
    MAX_FILE_SIZE_MB, ROOT_DIRECTORY, EXCLUDED_DIRECTORIES, POLL_INTERVAL
)
from database import Database
from telegram_client import TelegramClient

def get_file_hash(filepath):
    """Calculates SHA256 hash of a file to uniquely identify it."""
    hasher = hashlib.sha256()
    with open(filepath, 'rb') as f:
        buf = f.read(65536)
        while len(buf) > 0:
            hasher.update(buf)
            buf = f.read(65536)
    return hasher.hexdigest()

async def process_recursive(db, telegram):
    """Recursively scans the ROOT_DIRECTORY and uploads new files."""
    if not os.path.exists(ROOT_DIRECTORY):
        print(f"Error: Root directory '{ROOT_DIRECTORY}' does not exist.")
        return

    print(f"Scanning recursively from: {ROOT_DIRECTORY}")
    
    # Supported extensions
    IMAGE_EXTS = {'.jpg', '.jpeg', '.png', '.webp', '.heic'}
    VIDEO_EXTS = {'.mp4', '.mov', '.avi', '.mkv'}
    
    for root, dirs, files in os.walk(ROOT_DIRECTORY):
        # Modify dirs in-place to skip excluded directories
        # This prevents os.walk from even entering them
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRECTORIES and not d.startswith('.')]
        
        # Also check if the full path should be excluded (simple check)
        # e.g. if root contains "Android/data"
        skip_dir = False
        for excluded in EXCLUDED_DIRECTORIES:
            if excluded in root.split(os.sep):
                skip_dir = True
                break
        if skip_dir:
            continue

        for filename in files:
            ext = os.path.splitext(filename)[1].lower()
            if ext not in IMAGE_EXTS and ext not in VIDEO_EXTS:
                continue
                
            filepath = os.path.join(root, filename)
            
            # Unique ID for local files: We use the file hash. 
            try:
                file_hash = get_file_hash(filepath)
            except Exception as e:
                print(f"Error reading {filename}: {e}")
                continue
                
            if db.is_uploaded(file_hash):
                continue
                
            print(f"Found new file: {filename} in {root}")
            
            # Check size
            try:
                file_size_mb = os.path.getsize(filepath) / (1024 * 1024)
                if file_size_mb > MAX_FILE_SIZE_MB:
                    print(f"Skipping {filename}: Size {file_size_mb:.2f}MB exceeds limit.")
                    db.add_uploaded(file_hash, filename + " (SKIPPED_SIZE)")
                    continue
            except OSError:
                continue
                
            # Upload
            success = False
            try:
                if ext in IMAGE_EXTS:
                    success = await telegram.upload_photo(filepath, caption=filename)
                elif ext in VIDEO_EXTS:
                    success = await telegram.upload_video(filepath, caption=filename)
            except Exception as e:
                print(f"Upload failed for {filename}: {e}")
                
            if success:
                print(f"Successfully uploaded {filename}")
                db.add_uploaded(file_hash, filename)
            else:
                print(f"Failed to upload {filename}")
                
            # Rate limit
            await asyncio.sleep(1)

async def main():
    print(f"Starting Recursive Directory Watcher...")
    print(f"Root: {ROOT_DIRECTORY}")
    print(f"Excluded: {EXCLUDED_DIRECTORIES}")
    print(f"Poll Interval: {POLL_INTERVAL} seconds")
    
    db = Database(DB_FILE)
    telegram = TelegramClient(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID)
    
    try:
        while True:
            await process_recursive(db, telegram)
            print(f"Sleeping for {POLL_INTERVAL} seconds...")
            await asyncio.sleep(POLL_INTERVAL)
    except KeyboardInterrupt:
        print("Stopping...")
    finally:
        db.close()

if __name__ == '__main__':
    asyncio.run(main())
