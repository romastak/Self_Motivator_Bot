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
    adding = State()


@router_cmd_cr_by_key.message(F.text == 'Создать шаблон по ключу')
async def cmd_cr_by_key(message: Message, state: FSMContext):
    if state:
        await state.clear()
    await message.answer('Введите ключ:')
    await state.set_state(GetTemplByKey.key)


@router_cmd_cr_by_key.message(GetTemplByKey.key)
async def cmd_cr_by_key_done(message: Message, state: FSMContext):
    output_crits = []
    output_mnoj = []
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
        await state.update_data(templ_data=(templ_name_val, templ_crits_val, templ_mnoj_val))
        print(f'DEBUG: имя, критерии, множители: {templ_name_val}, {templ_crits_val}, {templ_mnoj_val}')

        await message.answer(f'Найден шаблон "{templ_name_val}".')

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
                mnoj_name = crit[0]
                mnoj_score = crit[1]
                mnoj_comment = crit[2]

                if crit_comment == 1:
                    mnoj_comment = 'Да'
                else:
                    mnoj_comment = 'Нет'

                output_mnoj.append(f'• "{crit_name}"\n'
                                    f'Значение: "x{crit_score}"\n'
                                    f'Возможность комментирования: "{mnoj_comment}"')

            result_mnojs = "\n".join(output_mnoj)

        if templ_mnoj_val:
            await message.answer(f'Структура шаблона:\n'
                                 f'................................................\n'
                                 f'Критерии:\n'
                                 f'{result_crits}\n'
                                 f'................................................\n'
                                 f'Множители:\n'
                                 f'{result_mnojs}', reply_markup=add_templ_by_key_keyboard())
        else:
            await message.answer(f'Структура шаблона:\n'
                                 f'................................................\n'
                                 f'Критерии:\n'
                                 f'{result_crits}', reply_markup=add_templ_by_key_keyboard())

    else:
        await message.answer('Шаблон не найден.', reply_markup=main_keyboard())


@router_cmd_cr_by_key.callback_query(F.data == 'add_templ_by_key')
async def cmd_add_by_key_done(callback: CallbackQuery, state: FSMContext):
    tg_id = callback.from_user.id
    templ_data = await state.get_data()
    templ_data_clear = templ_data.get('templ_data')
    templ_name_val = templ_data_clear[0]
    templ_crits_val = templ_data_clear[1]
    templ_mnoj_val = templ_data_clear[2]

    result = await add_template_to_user(tg_id, templ_name_val, templ_crits_val, templ_mnoj_val)
    print(f'DEBUG: данные шаблона: {templ_data}')

    if result:
        await callback.message.answer(f'Вам добавлена копия шаблона.', reply_markup=main_keyboard())
    else:
        await callback.message.answer('Не удалось добавить шаблон.', reply_markup=main_keyboard())

    await state.clear()