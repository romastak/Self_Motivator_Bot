import tgcrypto
from pyrogram import Client, filters
from pyrogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
import sqlite3
import asyncio

def create_template_keyboard():
    keyboard = ReplyKeyboardMarkup(
        [
            [KeyboardButton("+ Добавить критерий"), KeyboardButton("- Удалить критерий")],
            [KeyboardButton("+ Добавить множитель"), KeyboardButton("- Удалить множитель")],
            [KeyboardButton("+ Добавить условие"), KeyboardButton("- Удалить условие")],
            [KeyboardButton("Протестировать шаблон")],
            [KeyboardButton("Сохранить шаблон")],
            [KeyboardButton("Выйти без сохранения")],
        ],
        resize_keyboard=True  # Уменьшение размера кнопок
    )
    return keyboard

def main_keyboard():
    keyboard = ReplyKeyboardMarkup(
        [
            [KeyboardButton("О системе мотивации"), KeyboardButton("Использование системы на примере")],
            [KeyboardButton("Создать отчёт")],
            [KeyboardButton("Создать шаблон"), KeyboardButton("Просмотреть шаблоны")],
            [KeyboardButton("Получить ключ шаблона"), KeyboardButton("Создать шаблон по ключу")]
        ],
        resize_keyboard=True  # Уменьшение размера кнопок
    )
    return keyboard

def user_templates_keyboard(templates_list):
    keyboard = InlineKeyboardMarkup([templates_list])  # Уменьшение размера кнопок
    return keyboard