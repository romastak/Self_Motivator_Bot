import asyncio
import random
import re
from aiogram.types import Message
from aiogram.filters import Command
from aiogram import F, Router
from aiogram.fsm.state import StatesGroup, State # Классы состояний
from aiogram.fsm.context import FSMContext # Инструмент управления состояниями
from aiogram.types import CallbackQuery
from aiogram.filters.callback_data import CallbackData
from assets.db_modules.requests import get_user_templates, get_templ_key, get_all_templ_keys, get_template_data, add_template_to_user
from assets.other_modules.keyboards import main_keyboard, add_templ_by_key_keyboard


router_cmd_cr_by_key = Router()


class GetTemplByKey(StatesGroup):
    key = State()


@router_cmd_cr_by_key.message(F.text == 'Создать шаблон по ключу')
async def cmd_cr_by_key(message: Message, state: FSMContext):
    if state:
        await state.clear()
    await message.answer('Введите ключ:')
    await state.set_state(GetTemplByKey.key)


@router_cmd_cr_by_key.message(GetTemplByKey.key)
async def cmd_cr_by_key_done(message: Message, state: FSMContext):
    telegram_id = message.from_user.id
    await state.update_data(key=message.text)
    data = await state.get_data()
    key = data['key']
    templ_keys = await get_all_templ_keys()
    print('тест')
    print(templ_keys)
    key = str(key)

    if key in templ_keys:
        # Извлекаем данные шаблона по ключу
        templ_name_val, templ_crits_val, templ_mnoj_val = await get_template_data(key=key, templ_id=None)
        print(templ_name_val, templ_crits_val, templ_mnoj_val)
        result = await add_template_to_user(telegram_id, templ_name_val, templ_crits_val, templ_mnoj_val)

        if result:
            await message.answer(f'Найден шаблон "{templ_name_val}".\n'
                                 f'Вам добавлена копия шаблона.', reply_markup=main_keyboard())
    else:
        await message.answer('Шаблон не найден.', reply_markup=main_keyboard())

    await state.clear()
