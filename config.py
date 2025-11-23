# Configuration for Google Photos to Telegram Uploader

# Telegram Settings
# Get these from @BotFather and by adding the bot to your group
TELEGRAM_BOT_TOKEN = "8094153443:AAEGRx0nZv0IgpMGHfTlORvJYY0c7ZQ35a8"
TELEGRAM_CHAT_ID = "-1003390501705"  # Can be integer or string (e.g., "-100123456789")

# Google Photos Settings
# Path to the credentials.json file you downloaded from Google Cloud Console
CREDENTIALS_FILE = "credentials.json"
TOKEN_FILE = "token_new.json"  # This will be generated automatically

# Application Settings
DB_FILE = "history.db"
CHUNK_SIZE = 1024 * 1024  # 1MB chunks for download
MAX_FILE_SIZE_MB = 50     # Telegram bot API limit

# Local Watcher Settings
# Local Watcher Settings
# Root directory to recursively scan
# On Android: "/storage/emulated/0" (Internal Storage)
# On Windows: "C:\\Users\\MCL009\\Pictures\\TelegramUploads_Root"
ROOT_DIRECTORY = "C:\\Users\\MCL009\\Pictures\\TelegramUploads_Root"

# List of directory names or paths to IGNORE
# This is important to avoid scanning system files, app data, or junk.
EXCLUDED_DIRECTORIES = [
    "Android",          # App data (contains thousands of files)
    ".thumbnails",      # Cached thumbnails
    "WhatsApp Stickers",# Junk images
    "cache",            # App caches
    "Telegram",         # Avoid re-uploading things downloaded from Telegram itself (optional)
]

POLL_INTERVAL = 5  # Check for new files every 5 seconds
