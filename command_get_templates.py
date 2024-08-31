import asyncio
import random

from aiogram.types import Message
from aiogram.filters import Command
from aiogram import F, Router
from aiogram.fsm.state import StatesGroup, State # Классы состояний
from aiogram.fsm.context import FSMContext # Инструмент управления состояниями
from aiogram.types import CallbackQuery
from aiogram.filters.callback_data import CallbackData
from keyboards import main_keyboard, create_template_keyboard, cancel_keyboard, delete_crit_keyboard, delete_mnoj_keyboard, get_user_templ_keyboard
from keyboards import templ_actions_keyboard
from requests import get_user_templates, delete_user_template
import re

from requests import save_user_template

router_cmd_get_user_templ = Router()


class Choose_templ(StatesGroup):
    choosen_templ = State()
    templ_name = State()


@router_cmd_get_user_templ.message(F.text == "Мои шаблоны")
async def get_user_templ(message: Message):
    telegram_id = message.from_user.id
    user_templ_list = await get_user_templates(telegram_id)

    if user_templ_list != []:
        await message.answer(text='Ваши шаблоны:', reply_markup=get_user_templ_keyboard(user_templ_list))
    else:
        await message.answer('У вас нет ни одного шаблона.')


# Обработчик нажатий на кнопки с шаблонами
@router_cmd_get_user_templ.callback_query(lambda callback: callback.data.startswith("templ_num_"))
async def choose_templ(callback: CallbackQuery, state: FSMContext):
    telegram_id = callback.from_user.id
    match = re.match(r"^templ_num_(\d+)$", callback.data)

    if match:
        template_num = int(match.group(1))
        user_templ_list = await get_user_templates(telegram_id)
        chosen_templ = user_templ_list[template_num]
        await state.update_data(chosen_templ=chosen_templ) # Сохраняем переменную в контексте FSM

        await callback.message.edit_text(
            text=f'Вы выбрали шаблон: "{chosen_templ}"',
            parse_mode='Markdown',
            reply_markup=templ_actions_keyboard()
        )


# Обработчик нажатия кнопки "Отредактировать шаблон"
@router_cmd_get_user_templ.callback_query(F.data == "edit_templ")
async def edit_template(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Функция находится в разработке")


# Обработчик нажатия кнопки "Удалить шаблон"
@router_cmd_get_user_templ.callback_query(F.data == "delete_templ")
async def delete_template(callback: CallbackQuery, state: FSMContext):
    tg_id = callback.from_user.id
    data = await state.get_data()
    chosen_templ = data.get('chosen_templ')

    if chosen_templ:
        # Удаляем шаблон
        success = await delete_user_template(tg_id, chosen_templ)

        if success:
            await callback.message.answer("Шаблон удален.", reply_markup=main_keyboard())
        else:
            await callback.message.answer("Не удалось удалить шаблон. Возможно, он уже удален.")
    else:
        await callback.message.answer("Не удалось найти выбранный шаблон.")
