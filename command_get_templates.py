# import logging
# from aiogram import Bot, Dispatcher, types
# from aiogram.filters import Text
# from aiogram.fsm import FSMContext, State, StatesGroup
# from aiogram.fsm.storage.memory import MemoryStorage
# from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
# from aiogram.utils import executor
# import psycopg2
# from db import get_connection_and_cursor_vars
# import asyncio
#
# # Настройка логирования
# logging.basicConfig(level=logging.INFO)
#
# # Инициализация бота и диспетчера
# bot_token = "7266990703:AAE58wOTTLQsAU05jV0Exh8ODRz29ljqSMM"
# bot = Bot(token=bot_token)
# storage = MemoryStorage()
# dp = Dispatcher(storage=storage)
#
# # Подключение middleware для FSM
# dp.middleware.setup(FSMContextMiddleware(storage))
#
# # Обработчик команды "Просмотреть шаблоны"
# @dp.message(Text(equals="Просмотреть шаблоны"))
# async def list_templates(message: types.Message):
#     telegram_id = message.from_user.id
#     connection, cursor = get_connection_and_cursor_vars()
#
#     # Получаем id пользователя
#     cursor.execute('''SELECT id FROM "user" WHERE telegram_id = %s''', (telegram_id,))
#     user_id = cursor.fetchone()
#
#     if user_id is None:
#         # Обработка случая, когда пользователь не найден
#         await message.reply("Пользователь не найден.")
#         cursor.close()
#         connection.close()
#         return
#
#     user_id = user_id[0]
#
#     # Получаем имена и id шаблонов
#     cursor.execute('''SELECT id, template_name FROM user_template WHERE user_id = %s''', (user_id,))
#     templates = cursor.fetchall()
#
#     if not templates:
#         await message.reply("У вас нет сохраненных шаблонов.")
#     else:
#         keyboard = InlineKeyboardMarkup(
#             inline_keyboard=[
#                 [InlineKeyboardButton(template_name, callback_data=f"template_{template_id}")]
#                 for template_id, template_name in templates
#             ]
#         )
#         await message.reply("Ваши шаблоны:", reply_markup=keyboard)
#
#     connection.close()
#
# # Обработчик выбора шаблона через inline-кнопку
# @dp.callback_query(Text(startswith="template_"))
# async def select_template(callback_query: types.CallbackQuery):
#     template_id = int(callback_query.data.split("_")[1])
#     user_id = callback_query.from_user.id
#     connection, cursor = get_connection_and_cursor_vars()
#
#     # Получаем имя шаблона
#     cursor.execute('''SELECT template_name FROM user_template WHERE id = %s AND user_id = %s''', (template_id, user_id))
#     template = cursor.fetchone()
#
#     if template:
#         template_name = template[0]
#         await open_template_constructor(callback_query.message.chat.id, user_id, template_id, template_name)
#
#     connection.close()
#     await callback_query.answer()
#
# async def open_template_constructor(chat_id, user_id, template_id, template_name):
#     connection, cursor = get_connection_and_cursor_vars()
#
#     # Извлечение структуры шаблона
#     cursor.execute('''SELECT * FROM template_structure WHERE user_template_id = %s''', (template_id,))
#     template_structure = cursor.fetchall()
#
#     cursor.execute('''SELECT * FROM template_criterion WHERE template_structure_id IN
#                       (SELECT id FROM template_structure WHERE user_template_id = %s)''', (template_id,))
#     template_criteries = cursor.fetchall()
#
#     cursor.execute('''SELECT * FROM template_multiplier WHERE template_structure_id IN
#                       (SELECT id FROM template_structure WHERE user_template_id = %s)''', (template_id,))
#     template_multipliers = cursor.fetchall()
#
#     # Закрываем соединение с базой данных
#     connection.close()
#
#     # Здесь ваша логика для инициализации конструктора шаблонов с полученными параметрами
#     user_states = {}
#     # Например, сохраним параметры в словаре состояния пользователя
#     user_states[user_id] = {
#         "template_id": template_id,
#         "template_name": template_name,
#         "structure": template_structure,
#         "criteries": template_criteries,
#         "multipliers": template_multipliers,
#     }
#
#     # Отправьте сообщение пользователю с уведомлением об открытии конструктора шаблонов
#     await bot.send_message(chat_id, f'Конструктор шаблонов "{template_name}" открыт.')
#
#     # Здесь можно вызвать функцию для отображения меню конструктора шаблонов
#
# if __name__ == "__main__":
#     executor.start_polling(dp, skip_updates=True)
