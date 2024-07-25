import tgcrypto
from pyrogram import Client, idle, filters
from pyrogram.types import ReplyKeyboardMarkup, KeyboardButton, BotCommand
from pyrogram.errors import FloodWait
import asyncio
import sqlite3

def get_templates(user_id):
    conn = sqlite3.connect('reports.db')
    cursor = conn.cursor()
    cursor.execute('SELECT question, response_type FROM templates WHERE user_id = ?', (user_id,))
    templates = cursor.fetchall()
    conn.close()
    return templates