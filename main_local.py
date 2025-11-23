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
    GIF_EXTS = {'.gif'}
    
    for root, dirs, files in os.walk(ROOT_DIRECTORY):
        # Modify dirs in-place to skip excluded directories
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRECTORIES and not d.startswith('.')]
        
        skip_dir = False
        for excluded in EXCLUDED_DIRECTORIES:
            if excluded in root.split(os.sep):
                skip_dir = True
                break
        if skip_dir:
            continue

        for filename in files:
            # Ignore junk files (macOS/Android metadata)
            if filename.startswith('._'):
                continue

            ext = os.path.splitext(filename)[1].lower()
            if ext not in IMAGE_EXTS and ext not in VIDEO_EXTS and ext not in GIF_EXTS:
                continue
                
            filepath = os.path.join(root, filename)
            
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
                if ext in GIF_EXTS:
                     success = await telegram.upload_animation(filepath)
                elif ext in IMAGE_EXTS:
                    # Telegram Photo limit is ~10MB. 
                    if file_size_mb > 9.5: 
                        print(f"Compressing {filename} (size {file_size_mb:.2f}MB > 10MB)...")
                        try:
                            from PIL import Image
                            with Image.open(filepath) as img:
                                # Convert to RGB (in case of RGBA/P)
                                if img.mode in ("RGBA", "P"):
                                    img = img.convert("RGB")
                                
                                # Save to temp file with compression
                                temp_path = filepath + ".compressed.jpg"
                                # Reduce quality until fit? For now just hardcode a reasonable compression
                                img.save(temp_path, "JPEG", quality=85, optimize=True)
                                
                                # Check if it helped
                                temp_size = os.path.getsize(temp_path) / (1024 * 1024)
                                if temp_size < 10:
                                    print(f"Compressed to {temp_size:.2f}MB. Uploading as photo...")
                                    success = await telegram.upload_photo(temp_path)
                                else:
                                    print(f"Still too big ({temp_size:.2f}MB). Uploading as document.")
                                    success = await telegram.upload_document(filepath)
                                
                                # Cleanup
                                if os.path.exists(temp_path):
                                    os.remove(temp_path)
                        except ImportError:
                            print("Pillow not installed. Uploading as document.")
                            success = await telegram.upload_document(filepath)
                        except Exception as e:
                            print(f"Compression failed: {e}. Uploading as document.")
                            success = await telegram.upload_document(filepath)
                    else:
                        success = await telegram.upload_photo(filepath) 
                elif ext in VIDEO_EXTS:
                    success = await telegram.upload_video(filepath) 
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
