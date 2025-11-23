import asyncio
import os
from telegram import Bot
from telegram.error import TelegramError
from telegram.ext import ApplicationBuilder

class TelegramClient:
    def __init__(self, token, chat_id):
        from telegram.request import HTTPXRequest
        # Increase timeout for large file uploads
        request = HTTPXRequest(connection_pool_size=8, connect_timeout=300.0, read_timeout=300.0, write_timeout=300.0)
        self.application = ApplicationBuilder().token(token).request(request).build()
        self.bot = self.application.bot
        self.chat_id = chat_id

    async def upload_photo(self, file_path, caption=None):
        """Uploads a photo to the Telegram chat."""
        try:
            with open(file_path, 'rb') as f:
                await self.bot.send_photo(chat_id=self.chat_id, photo=f, caption=caption)
            return True
        except TelegramError as e:
            print(f"Failed to upload photo {file_path}: {e}")
            return False

    async def upload_video(self, file_path, caption=None):
        """Uploads a video to the Telegram chat."""
        try:
            with open(file_path, 'rb') as f:
                await self.bot.send_video(chat_id=self.chat_id, video=f, caption=caption)
            return True
        except TelegramError as e:
            print(f"Failed to upload video {file_path}: {e}")
            return False

    async def upload_document(self, file_path, caption=None):
        """Uploads a file as a document (for large files)."""
        try:
            with open(file_path, 'rb') as f:
                await self.bot.send_document(chat_id=self.chat_id, document=f, caption=caption)
            return True
        except TelegramError as e:
            print(f"Failed to upload document {file_path}: {e}")
            return False

    async def upload_animation(self, file_path, caption=None):
        """Uploads a GIF/Animation to the Telegram chat."""
        try:
            with open(file_path, 'rb') as f:
                await self.bot.send_animation(chat_id=self.chat_id, animation=f, caption=caption)
            return True
        except TelegramError as e:
            print(f"Failed to upload animation {file_path}: {e}")
            return False

    async def send_message(self, text):
        """Sends a text message to the chat."""
        try:
            await self.bot.send_message(chat_id=self.chat_id, text=text)
        except TelegramError as e:
            print(f"Failed to send message: {e}")
