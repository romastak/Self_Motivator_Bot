# import sqlite3
# import random
# import keyboards
# from pyrogram import Client, filters
# import asyncio
#
# user_states = {}  # Хранение состояния пользователей
#
# def create_report_main(client: Client):
#     @client.on_message(filters.text & filters.regex("Создать отчет"))
#     async def create_report(client: Client, message):
#         user_id = message.from_user.id
#         conn = sqlite3.connect('reports.db')
#         cursor = conn.cursor()
#
#         cursor.execute('''SELECT user_template_id, name FROM user_template WHERE user_id = ?''', (user_id,))
#         templates = cursor.fetchall()
#
#         if not templates:
#             await message.reply_text("• У вас нет сохраненных шаблонов.")
#             conn.close()
#             return
#
#         # Запрос выбора шаблона
#         response = "Выберите шаблон для отчета:\n"
#         for idx, template in enumerate(templates):
#             response += f"{idx + 1}. {template[1]}\n"
#         await message.reply_text(response)
#
#         user_states[user_id] = asyncio.Future()
#         selected_template_index = await user_states[user_id]
#
#         try:
#             template_index = int(selected_template_index) - 1
#             template_id = templates[template_index][0]
#         except (ValueError, IndexError):
#             await message.reply_text("• Неверный выбор. Пожалуйста, выберите правильный номер шаблона.")
#             conn.close()
#             return
#
#         # Генерация отчета
#         cursor.execute('''SELECT critery_name, critery_score, critery_comment FROM template_critery
#                           JOIN template_structure ON template_critery.template_structure_id = template_structure.template_structure_id
#                           WHERE template_structure.user_template_id = ?''', (template_id,))
#         criterions = cursor.fetchall()
#
#         cursor.execute('''SELECT mnojitel_name, mnojitel_score, mnojitel_comment FROM template_mnojitel
#                           JOIN template_structure ON template_mnojitel.template_structure_id = template_structure.template_structure_id
#                           WHERE template_structure.user_template_id = ?''', (template_id,))
#         mnojitels = cursor.fetchall()
#
#         report = "Отчет:\n\nКритерии:\n"
#         for crit in criterions:
#             description, score_per_hour, comment_bool = crit
#             report += f"• {description}: {score_per_hour} баллов/час\n"
#             if comment_bool:
#                 report += "  Комментарий: Да\n"
#
#         report += "\nМножители:\n"
#         for mnoj in mnojitels:
#             description, mnoj_score, comment_bool = mnoj
#             report += f"• {description}: x{mnoj_score}\n"
#             if comment_bool:
#                 report += "  Комментарий: Да\n"
#
#         await message.reply_text(report, reply_markup=keyboards.main_keyboard())
#
#         conn.close()
#
#     # Функция для получения ответа от пользователя
#     @client.on_message(filters.private)
#     async def receive_response(client: Client, message):
#         user_id = message.from_user.id
#         if user_id in user_states:
#             user_states[user_id].set_result(message.text)
