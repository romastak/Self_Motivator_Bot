import asyncio
import random

from aiogram.types import Message
from aiogram.filters import Command
from aiogram import F, Router
from aiogram.fsm.state import StatesGroup, State # Классы состояний
from aiogram.fsm.context import FSMContext # Инструмент управления состояниями
from aiogram.types import CallbackQuery
from aiogram.filters.callback_data import CallbackData
from keyboards import get_templ_key_keyboard
from requests import get_user_templates, get_templ_key
import re

router_cmd_get_key = Router()

@router_cmd_get_key.message(F.text == "Получить ключ шаблона")
async def get_user_templ(message: Message):
    telegram_id = message.from_user.id
    user_templ_list = await get_user_templates(telegram_id)

    if user_templ_list != []:
        await message.answer(text='• Выберите шаблон, для получения его ключа:', reply_markup=get_templ_key_keyboard(user_templ_list))
    else:
        await message.answer('У вас нет ни одного шаблона.')


@router_cmd_get_key.callback_query(lambda callback: callback.data.startswith("templ_key_"))
async def get_user_templ_done(callback: CallbackQuery):
    telegram_id = callback.from_user.id
    match = re.match(r"^templ_key_(\d+)$", callback.data)

    if match:
        template_num = int(match.group(1))
        user_templ_list = await get_user_templates(telegram_id)
        chosen_templ = user_templ_list[template_num]
        key = await get_templ_key(telegram_id, chosen_templ)

        await callback.message.edit_text(f'• Ключ получен! Скопируйте и отправьте ключ пользователю, чтобы он смог получить '
                                         f'ваш шаблон с помощью команды "Создать шаблон по ключу"')
        await callback.message.answer(key)
