import asyncio
import os
from telegram import Bot
from telegram.error import TelegramError

class TelegramClient:
    def __init__(self, token, chat_id):
        from telegram.request import HTTPXRequest
        self.bot = Bot(token=token, request=HTTPXRequest(connect_timeout=30, read_timeout=30))
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
