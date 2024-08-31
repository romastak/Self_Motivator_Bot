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
from requests import get_user_templates, get_templ_key, get_all_templ_keys
import re

router_cmd_cr_by_key = Router()

class GetTemplByKey(StatesGroup):
    key = State()

@router_cmd_cr_by_key.message(F.text == 'Создать шаблон по ключу')
async def cmd_cr_by_key(message: Message, state: FSMContext):
    if state:
        await state.clear()
    await message.answer('Введите ключ:')
    state.set_state(GetTemplByKey.key)

@router_cmd_cr_by_key.message(GetTemplByKey.key)
async def cmd_cr_by_key_done(message: Message, state: FSMContext):
    await state.update_data(key=message.text)
    data = await state.get_data()
    key = data['key']
    templ_keys = await get_all_templ_keys()

    if key in templ_keys:
        # Извлекаем данные шаблона по ключу
        templ_name_val, templ_crits_val, templ_mnoj_val = await get_template_data_by_key(key)

        if template_data:
            # Добавляем шаблон пользователю в базу данных
            telegram_id = message.from_user.id
            success = await add_template_to_user(telegram_id, templ_name_val, templ_crits_val, templ_mnoj_val)

            if success:
                await message.answer('Шаблон успешно создан и добавлен в ваш список!')
            else:
                await message.answer('Произошла ошибка при добавлении шаблона.')
        else:
            await message.answer('Произошла ошибка при получении данных шаблона.')
    else:
        await message.answer('Шаблон с таким ключом не найден.')

    await state.clear()
