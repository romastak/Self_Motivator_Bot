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
from assets.other_modules.keyboards import main_keyboard, create_template_keyboard, cancel_keyboard, delete_crit_keyboard, delete_mnoj_keyboard, get_user_templ_keyboard
from assets.other_modules.keyboards import templ_actions_keyboard, global_score_keyboard, keep_looking_structure_from_my_templs_keyboard
from assets.db_modules.requests import get_user_templates, delete_user_template, get_template_global_score, make_null_template_global_score, change_template_global_score
from assets.db_modules.requests import save_user_template, get_template_data

router_cmd_get_user_templ = Router()

# Класс для машины состояний для изменения глобальных очков
class ChangeGlobalScore(StatesGroup):
    score_val = State()

class Choose_templ(StatesGroup):
    choosen_templ = State()
    templ_name = State()

@router_cmd_get_user_templ.message(F.text == "Мои шаблоны")
async def get_user_templ(message: Message, state: FSMContext):

    await state.clear()

    telegram_id = message.from_user.id
    user_templ_list = await get_user_templates(telegram_id)

    if user_templ_list != []:
        await message.answer(text='Ваши шаблоны:', reply_markup=get_user_templ_keyboard(user_templ_list, False))
    else:
        await message.answer('У вас нет ни одного шаблона.')


# Вернуться назад в список моих шаблонов
@router_cmd_get_user_templ.callback_query(F.data == 'back_to_my_templs')
async def back_to_my_templs(callback: CallbackQuery):
    telegram_id = callback.from_user.id
    user_templ_list = await get_user_templates(telegram_id)

    if user_templ_list != []:
        await callback.message.edit_text(text='Ваши шаблоны:', reply_markup=get_user_templ_keyboard(user_templ_list, False))
    else:
        await callback.message.edit_text(text='Возникла ошибка при загрузке шаблонов.')
        await state.clear()


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
        print(await state.get_data())
        await callback.message.edit_text(
            text=f'Вы выбрали шаблон "{chosen_templ[1]}"',
            parse_mode='Markdown',
            reply_markup=templ_actions_keyboard()
        )


#  Обработчик нажатия кнопки "Посмотреть глобальные очки"
@router_cmd_get_user_templ.callback_query(F.data == "look_to_global_score")
async def look_to_global_score(callback: CallbackQuery, state: FSMContext):
    tg_id = callback.from_user.id
    data = await state.get_data()
    chosen_templ = data.get('chosen_templ')
    global_score = await get_template_global_score(chosen_templ[0])
    await callback.message.edit_text(f'Глобальные очки шаблона "{chosen_templ[1]}" = {global_score}', reply_markup=global_score_keyboard())


#  Смотрим структуру шаблона
@router_cmd_get_user_templ.callback_query(F.data == "look_at_the_struct")
async def look_at_the_struct_func(callback: CallbackQuery, state: FSMContext):
    state_data = await state.get_data()
    templ_data = state_data.get('chosen_templ')
    templ_id = templ_data[0]
    output_crits = []
    output_mnoj = []

    print(f'DEBUG: get data from state: {templ_id}')
    # Извлекаем данные шаблона по ID
    templ_name_val, templ_crits_val, templ_mnoj_val = await get_template_data(key=None, templ_id=templ_id)
    await state.update_data(templ_data=(templ_name_val, templ_crits_val, templ_mnoj_val))
    print(f'DEBUG: имя, критерии, множители: {templ_name_val}, {templ_crits_val}, {templ_mnoj_val}')

    #  Сбор критериев
    for crit in templ_crits_val:
        crit_name = crit[0]
        crit_score = crit[1]
        crit_comment = crit[2]

        if crit_comment == 1:
            crit_comment = 'Да'
        else:
            crit_comment = 'Нет'

        output_crits.append(f'• "{crit_name}"\n'
                            f'Количество очков за час: "{crit_score}"\n'
                            f'Возможность комментирования: "{crit_comment}"')

    result_crits = "\n".join(output_crits)

    #  Сбор множителей
    if templ_mnoj_val:
        for mnoj in templ_mnoj_val:
            mnoj_name = mnoj[0]
            mnoj_score = mnoj[1]
            mnoj_comment = mnoj[2]

            if mnoj_comment == 1:
                mnoj_comment = 'Да'
            else:
                mnoj_comment = 'Нет'

            output_mnoj.append(f'• "{mnoj_name}"\n'
                               f'При ответе "Нет" заработанные очки умножатся на "x{mnoj_score}"\n'
                               f'Возможность комментирования: "{mnoj_comment}"')

        result_mnojs = "\n".join(output_mnoj)

    if templ_mnoj_val:
        await callback.message.edit_text(f'Структура шаблона "{templ_name_val}":\n'
                             f'................................................\n'
                             f'Критерии:\n'
                             f'\n'
                             f'{result_crits}\n'
                             f'................................................\n'
                             f'Множители:\n'
                             f'\n'
                             f'{result_mnojs}', reply_markup=keep_looking_structure_from_my_templs_keyboard())
    else:
        await callback.message.edit_text(f'Структура шаблона "{templ_name_val}":\n'
                             f'................................................\n'
                             f'Критерии:\n'
                             f'\n'
                             f'{result_crits}', reply_markup=keep_looking_structure_from_my_templs_keyboard())


#  Возврат назад в выбранный шаблон из меню глобальных очков
@router_cmd_get_user_templ.callback_query(F.data == "back_to_the_templ")
async def back_to_the_templ(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    chosen_templ = data.get('chosen_templ')

    await callback.message.edit_text(
        text=f'Вы выбрали шаблон "{chosen_templ[1]}"',
        parse_mode='Markdown',
        reply_markup=templ_actions_keyboard()
    )


# Обнуляем глобальные очки
@router_cmd_get_user_templ.callback_query(F.data == "make_null_global_score_val")
async def null_to_global_score(callback: CallbackQuery, state: FSMContext):
    tg_id = callback.from_user.id
    data = await state.get_data()
    chosen_templ = data.get('chosen_templ')
    print(chosen_templ[0])
    await make_null_template_global_score(chosen_templ[0])
    await callback.message.edit_text(f'Значение глобальных очков шаблона "{chosen_templ[1]}" успешно обнулено.')
    await state.clear()


# Изменяем глобальные очки
@router_cmd_get_user_templ.callback_query(F.data == "change_global_score_val")
async def change_to_global_score(callback: CallbackQuery, state: FSMContext):
    await state.set_state(ChangeGlobalScore.score_val)
    await callback.message.edit_text(f'• Введите новое значение:')

@router_cmd_get_user_templ.message(ChangeGlobalScore.score_val)
async def look_to_global_score(message: Message, state: FSMContext):
    await state.update_data(score_val=message.text)
    tg_id = message.from_user.id
    data = await state.get_data()
    chosen_templ, score_val = data.get('chosen_templ'), data.get('score_val')
    success = await change_template_global_score(chosen_templ[0], float(score_val))
    if success:
        await message.answer(f'Значение глобальных очков шаблона "{chosen_templ[1]}" успешно изменено на "{score_val}".', reply_markup=main_keyboard())
        await state.clear()


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
            await callback.message.edit_text(f'Шаблон "{chosen_templ[1]}" успешно удален.')
        else:
            await callback.message.edit_text('Не удалось удалить шаблон. Возможно, он уже удален.')
    else:
        await callback.message.edit_text('Не удалось найти выбранный шаблон.')
    await state.clear()
