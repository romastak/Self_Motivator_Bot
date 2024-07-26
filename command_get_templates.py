import sqlite3
import keyboards
from pyrogram import Client, filters

def get_templates(client: Client, message):
    @client.on_message(filters.text & filters.regex("Просмотреть шаблоны"))
    async def list_templates(client: Client, message):
        user_id = message.from_user.id
        conn = sqlite3.connect('reports.db')
        cursor = conn.cursor()

        cursor.execute('''SELECT name FROM user_template WHERE user_id = ?''', (user_id,))
        templates = cursor.fetchall()

        if not templates:
            await message.reply_text("• У вас нет сохраненных шаблонов.")
        else:
            response = "Ваши шаблоны:\n"
            for template in templates:
                response += f"• {template[0]}\n"
            await message.reply_text(response, reply_markup=keyboards.main_keyboard())

        conn.close()
