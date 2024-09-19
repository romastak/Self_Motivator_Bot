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
from keyboards import templ_actions_keyboard, global_score_keyboard
from requests import get_user_templates, delete_user_template, get_template_global_score, make_null_template_global_score
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


@router_cmd_get_user_templ.callback_query(F.data == 'back_to_my_templs')
async def back_to_my_templs(callback: CallbackQuery):
    telegram_id = callback.from_user.id
    user_templ_list = await get_user_templates(telegram_id)

    if user_templ_list != []:
        await callback.message.edit_text(text='Ваши шаблоны:', reply_markup=get_user_templ_keyboard(user_templ_list))
    else:
        await callback.message.edit_text(text='Возникла ошибка при загрузке шаблонов.')


# Обработчик нажатий на кнопки с шаблонами в "Мои шаблоны"
@router_cmd_get_user_templ.callback_query(lambda callback: callback.data.startswith("templ_id_"))
async def choose_templ(callback: CallbackQuery, state: FSMContext):
    telegram_id = callback.from_user.id
    match = re.match(r"^templ_id_(\d+)$", callback.data)
    templ_id = callback.data
    templ_id = templ_id.split('_')
    templ_id = templ_id[2]

    if match:
        user_templ_list = await get_user_templates(telegram_id)

        for templ in user_templ_list:
            if int(templ_id) == int(templ[0]):
                chosen_templ = templ
                break

        await state.update_data(chosen_templ=chosen_templ) # Сохраняем переменную в контексте FSM

        await callback.message.edit_text(
            text=f'Вы выбрали шаблон "{chosen_templ[1]}"',
            parse_mode='Markdown',
            reply_markup=templ_actions_keyboard()
        )


# Обработчик нажатия кнопки "Посмотреть глобальные очки"
@router_cmd_get_user_templ.callback_query(F.data == "look_to_global_score")
async def look_to_global_score(callback: CallbackQuery, state: FSMContext):
    tg_id = callback.from_user.id
    data = await state.get_data()
    chosen_templ = data.get('chosen_templ')
    global_score = await get_template_global_score(chosen_templ[0])
    state.update_data(templ_id=chosen_templ[0])
    await callback.message.edit_text(f'Глобальные очки = {global_score}', reply_markup=global_score_keyboard())


# Обнуляем глобальные очки
@router_cmd_get_user_templ.callback_query(F.data == "make_null_global_score_val")
async def look_to_global_score(callback: CallbackQuery, state: FSMContext):
    tg_id = callback.from_user.id
    data = await state.get_data()
    templ_id = data.get('templ_id')
    await make_null_template_global_score(templ_id)
    await callback.message.edit_text('Глобальные очки шаблона успешно обнулены.')


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
        success = await delete_user_template(tg_id, chosen_templ[0])

        if success:
            await callback.message.answer("Шаблон удален.", reply_markup=main_keyboard())
        else:
            await callback.message.answer("Не удалось удалить шаблон. Возможно, он уже удален.")
    else:
        await callback.message.answer("Не удалось найти выбранный шаблон.")
