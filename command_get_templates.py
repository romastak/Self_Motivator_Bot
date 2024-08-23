import asyncio
import random

from aiogram.types import Message
from aiogram.filters import Command
from aiogram import F, Router
from aiogram.fsm.state import StatesGroup, State # Классы состояний
from aiogram.fsm.context import FSMContext # Инструмент управления состояниями
from aiogram.types import CallbackQuery
from aiogram.filters.callback_data import CallbackData
from keyboards import main_keyboard, create_template_keyboard, cancel_keyboard, delete_crit_keyboard, delete_mnoj_keyboard, get_user_templ
from requests import get_user_templates
import re

from requests import save_user_template

router_cmd_get_user_templ = Router()

@router_cmd_get_user_templ.message(F.text == "Мои шаблоны")
async def get_user_templ(message: Message):
    telegram_id = message.from_user.id
    user_templ_list = await get_user_templates(telegram_id)

    if user_templ_list != []:
        await message.answer(text='Ваши шаблоны:', reply_markup=delete_crit_keyboard(crits_list))
    else:
        await message.answer('У вас нет ни одного шаблона.')

# @router_delete_crit_el.callback_query(lambda callback: re.match(r"^crit_num_\d+$", callback.data))
# async def delete_crit_el(callback: CallbackQuery):
#     telegram_id = callback.from_user.id
#     match = re.match(r"^crit_num_(\d+)$", callback.data)
#
#     if match:
#         crit_num = int(match.group(1))  # Извлекаем номер критерия
#         current_user_templ = user_templates.get(telegram_id)
#         current_user_crits = current_user_templ.get('crit')
#         current_user_mnoj = current_user_templ.get('mnoj')
#
#         if len(current_user_crits) == 1 and current_user_mnoj != []:
#             await callback.message.answer(f"Последний критерий удалить нельзя, так как в шаблоне присутствуют множители.\n"
#                                           f"Для удаления последнего критерия удалите множители.")
#         else:
#             del current_user_crits[crit_num]
#             await callback.message.answer(f"Критерий удален")
#
#     await callback.answer()