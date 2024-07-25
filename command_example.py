import tgcrypto
from pyrogram import Client, idle, filters
from pyrogram.types import ReplyKeyboardMarkup, KeyboardButton, BotCommand
from pyrogram.errors import FloodWait
import asyncio

def example_main(client, message):
    @client.on_message(filters.text & filters.regex("Использование системы на примере"))
    def example(client, message):
        # Отправка сообщения о системе мотивации
        message.reply_text(
            "Здесь будет описан пример"
        )