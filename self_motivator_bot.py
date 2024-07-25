import tgcrypto
from pyrogram import Client, idle, filters
from pyrogram.types import ReplyKeyboardMarkup, KeyboardButton, BotCommand
from pyrogram.errors import FloodWait
import asyncio
import db, command_about, command_example, command_create_report, command_create_template, command_get_templates, keyboards
import sqlite3

bot_token = "7266990703:AAE58wOTTLQsAU05jV0Exh8ODRz29ljqSMM"
api_id = "27421113"
api_hash = "d29afa242526c14a7870e1a65c2b79d8"
app_name = "self_motivator_bot"

# Создание объекта клиента
client = Client(name=app_name, api_id=api_id, api_hash=api_hash, bot_token=bot_token)

# Словарь для хранения состояний пользователей
user_states = {}

@client.on_message(filters.command("start"))
def start(client, message):
    # Отправка приветственного сообщения с клавиатурой
    message.reply_text(
        f"Добро пожаловать, {message.from_user.first_name}!\n"
        f"Наша уникальная система мотивации предоставит вам возможность реализовать свои амбиции в полной мере.\n"
        f"Чтобы узнать подробнее нажмите на кнопку <<О системе мотивации>>.",
        reply_markup=keyboards.main_keyboard()
    )

# Просто определяем переменную
message = 0
user_id = 0

db.create_db()

command_about.about_main(client, message)

command_example.example_main(client, message)

command_create_report.create_report_main(client, message)

question = None
response_type = None
add_template_func = command_create_template.add_template(user_id, question, response_type)
command_create_template.create_template_main(client, message, add_template_func)

command_get_templates.get_templates(user_id)

# Запускаем клиент
client.start()

# Входим в режим прослушивания сообщений
idle()
