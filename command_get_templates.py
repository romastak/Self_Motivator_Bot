import sqlite3
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from db import get_connection_and_cursor_vars


def get_templates(client: Client, connection, cursor):
    @client.on_message(filters.text & filters.regex("Просмотреть шаблоны"))
    async def list_templates(client: Client, message):

        telegram_id = message.from_user.id
        connection, cursor = get_connection_and_cursor_vars()

        # Получаем ид пользователя
        cursor.execute('''SELECT id FROM "user" WHERE telegram_id = %s''', (telegram_id,))
        user_id = cursor.fetchone()[0]

        # Получаем имена и ид шаблонов
        cursor.execute('''SELECT id, template_name FROM user_template WHERE user_id = %s''', (user_id,))
        templates = cursor.fetchall()

        if user_id is None:
            # Обработка случая, когда пользователь не найден
            await message.reply("Пользователь не найден.")
            cursor.close()
            connection.close()
        else:
            if not templates:
                await message.reply_text("У вас нет сохраненных шаблонов.")
            else:
                keyboard = InlineKeyboardMarkup(
                    [
                        [InlineKeyboardButton(template_name, callback_data=f"template_{template_id}")]
                        for template_id, template_name in templates
                    ]
                )
                await message.reply_text("Ваши шаблоны:", reply_markup=keyboard)

        connection.close()

    @client.on_callback_query(filters.regex(r"^template_\d+$"))
    async def select_template(client: Client, callback_query):
        template_id = int(callback_query.data.split("_")[1])
        user_id = callback_query.from_user.id

        conn = sqlite3.connect('reports.db')
        cursor = conn.cursor()

        cursor.execute('''SELECT template_name FROM user_template WHERE user_template_id = ? AND user_id = ?''', (template_id, user_id))
        template = cursor.fetchone()

        if template:
            # Открываем конструктор шаблонов с параметрами выбранного шаблона
            await open_template_constructor(client, user_id, template_id, template[0])

        conn.close()
        await callback_query.answer()

async def open_template_constructor(client, user_id, template_id, template_name):
    # Здесь должна быть ваша логика для открытия конструктора шаблонов
    # Инициализация конструктора шаблонов с параметрами из базы данных
    conn = sqlite3.connect('reports.db')
    cursor = conn.cursor()

    # Пример извлечения параметров шаблона
    cursor.execute('''SELECT * FROM template_structure WHERE user_template_id = ?''', (template_id,))
    template_structure = cursor.fetchall()

    cursor.execute('''SELECT * FROM template_critery WHERE template_structure_id IN 
                      (SELECT template_structure_id FROM template_structure WHERE user_template_id = ?)''', (template_id,))
    template_criteries = cursor.fetchall()

    cursor.execute('''SELECT * FROM template_mnojitel WHERE template_structure_id IN 
                      (SELECT template_structure_id FROM template_structure WHERE user_template_id = ?)''', (template_id,))
    template_mnojitels = cursor.fetchall()

    # Закройте соединение с базой данных
    conn.close()

    # Здесь ваша логика для инициализации конструктора шаблонов с полученными параметрами
    user_states = {}
    # Например, сохраним параметры в словаре состояния пользователя
    user_states[user_id] = {
        "template_id": template_id,
        "template_name": template_name,
        "structure": template_structure,
        "criteries": template_criteries,
        "mnojitels": template_mnojitels,
    }

    # Отправьте сообщение пользователю с уведомлением об открытии конструктора шаблонов
    await client.send_message(user_id, f'Конструктор шаблонов "{template_name}" открыт.')

    # Здесь можно вызвать функцию для отображения меню конструктора шаблонов

