import tgcrypto
from pyrogram import Client, idle, filters
from pyrogram.types import ReplyKeyboardMarkup, KeyboardButton, BotCommand
from pyrogram.errors import FloodWait
import asyncio

def about_main(client, message):
    @client.on_message(filters.text & filters.regex("О системе мотивации"))
    def about(client, message):
        # Отправка сообщения о системе мотивации
        message.reply_text(
            "Наша система мотивации разработана для того, чтобы помочь вам достигать своих целей. "
            "Используйте наш бот для создания отчетов и шаблонов, чтобы отслеживать ваш прогресс и оставаться на верном пути."
        )