import tgcrypto
from pyrogram import Client, idle, filters
from pyrogram.types import ReplyKeyboardMarkup, KeyboardButton, BotCommand
from pyrogram.errors import FloodWait
import asyncio
import sqlite3

def create_report_main(client, message):
    @client.on_message(filters.text & filters.regex("Создать отчёт"))
    async def create_report(client, message):
        user_id = message.from_user.id
        templates = get_templates(user_id)
        answers = {}

        if not templates:
            await message.reply_text("У вас нет шаблонов отчётов. Пожалуйста, создайте шаблон сначала.")
            return

        for template in templates:
            question, response_type = template
            answer = await ask_question(user_id, question)
            if response_type == 'number':
                answer = float(answer)
            elif response_type == 'boolean':
                answer = bool(int(answer))
            answers[question] = answer

        # Вычисления и формирование отчета
        # Это пример, вы можете адаптировать его под свои нужды
        count_scores = (answers.get('Введите количество времени в часах сколько вы сегодня потратили на изучение IT', 0) * 2) + \
                       (answers.get('Введите количество времени в часах сколько вы сегодня потратили на саморазвитие и личностное развитие', 0)) + \
                       (answers.get('Введите количество времени в часах сколько вы сегодня потратили на занятия спортом', 0))

        if answers.get('Курили ли вы сегодня? Отправьте 1, если да. Отправьте 0, если нет.', False):
            count_scores *= 1.5

        report = f"Отчет за {datetime.date.today()}\n"
        for question, answer in answers.items():
            report += f"{question}: {answer}\n"

        report += f"\nСумма баллов за сегодня: {count_scores}\n"

        await client.send_message(user_id, report)
        await client.send_message(user_id, 'Перешлите отчет в основную группу')


