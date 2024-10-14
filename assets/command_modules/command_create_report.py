import asyncio
import random
import re
from aiogram.types import Message
from aiogram.filters import Command
from aiogram import F, Router, types
from aiogram.fsm.state import StatesGroup, State  # Классы состояний
from aiogram.fsm.context import FSMContext  # Инструмент управления состояниями
from aiogram.types import CallbackQuery
from aiogram.filters.callback_data import CallbackData
from assets.other_modules.keyboards import main_keyboard, create_template_keyboard, cancel_keyboard, get_user_templ_keyboard
from assets.db_modules.requests import save_user_template, edit_user_template, get_template_data, get_user_templates, get_template_global_score, change_template_global_score
from assets.command_modules.command_get_templates import Choose_templ


router_create_report = Router()

user_templ_crits = {}
user_templ_mnoj = {}
user_templ_name = {}

user_templ_crits_full = {}
user_templ_mnoj_full = {}

user_templ_crits_score = {}
user_templ_mnoj_score = {}

user_templ_crits_comm = {}
user_templ_mnoj_comm = {}

user_templ_global_score_dict = {}

# Сюда складываются в словарь с ключом data значения ответов пользователя по порядку (ответы на вопросы про критерии, множители)
user_report = {}


class Crits(StatesGroup):
    crit_score = State()
    crit_comm = State()


class Mnoj(StatesGroup):
    mnoj_score = State()
    mnoj_comm = State()


class ReportCreating(StatesGroup):
    just_state = State()


@router_create_report.message(F.text == 'Создать отчёт')
async def create_report(message: Message):

    tg_id = message.from_user.id

    #  Очищение состояний
    if tg_id in user_templ_mnoj_full:
        user_templ_mnoj_full.pop(tg_id)
    if tg_id in user_templ_crits_full:
        user_templ_crits_full.pop(tg_id)

    templ_list = await get_user_templates(tg_id)
    await message.answer('• Выберите шаблон для отчета',
                         reply_markup=get_user_templ_keyboard(templ_list, True)
                         )


@router_create_report.callback_query(lambda callback: callback.data.startswith('rep_templ_id_'))
async def start_report(callback: CallbackQuery, state: FSMContext):

    tg_id = callback.from_user.id
    match = re.match(r"^rep_templ_id_(\d+)$", callback.data)
    templ_id = callback.data
    templ_id = templ_id.split('_')
    templ_id = templ_id[3]
    if match:
        user_templ_list = await get_user_templates(tg_id)

        for templ in user_templ_list:
            if int(templ_id) == int(templ[0]):
                chosen_templ = templ
                break

        templ_name_val, templ_crit_val, templ_mnoj_val = await get_template_data(None, chosen_templ[0])
        gl_score = await get_template_global_score(chosen_templ[0])
        user_templ_global_score_dict[tg_id] = (chosen_templ[0], gl_score)
        print(user_templ_global_score_dict[tg_id])

        await state.set_state(Crits.crit_score)

        user_templ_name[tg_id] = templ_name_val
        if templ_mnoj_val:
            user_templ_mnoj[tg_id] = templ_mnoj_val
            if tg_id not in user_templ_mnoj_full:
                user_templ_mnoj_full[tg_id] = templ_mnoj_val.copy()
        if templ_crit_val:
            user_templ_crits[tg_id] = templ_crit_val
            await callback.message.edit_text(f'• Введите количество времени в часах сколько вы потратили за межотчетный'
                                                f' период на критерий "{templ_crit_val[0][0]}".\n'
                                                f'Например: 2.5')
            if tg_id not in user_templ_crits_full:
                user_templ_crits_full[tg_id] = templ_crit_val.copy()

        if templ_crit_val[0][2] == 1:
            await state.set_state(Crits.crit_comm)
        elif templ_crit_val[0][2] == 0:
            # Удаляем критерий из словаря
            user_templ_crits[tg_id].pop(0)
            if user_templ_crits[tg_id]:
                await state.set_state(Crits.crit_score)
            elif not user_templ_crits[tg_id]:
                if user_templ_mnoj[tg_id]:
                    await state.set_state(Mnoj.mnoj_score)
                elif not user_templ_mnoj[tg_id]:
                    await state.set_state(ReportCreating.just_state)

        user_report[tg_id] = {'data': []}


@router_create_report.message(Crits.crit_score)
async def fill_report_crits(message: Message, state: FSMContext):

    tg_id = message.from_user.id
    #  Удаляем критерий из словаря
    crit = user_templ_crits[tg_id][0]

    #  Запись данных в словарь для формирования отчета в конце
    user_report[tg_id]['data'].append(message.text)

    await message.answer(f'• Введите количество времени в часах сколько вы потратили за межотчетный'
                                         f' период на критерий "{crit[0]}".\n'
                                         f'Например: 2.5')

    if crit[2] == 1:
        await state.set_state(Crits.crit_comm)
    elif crit[2] == 0:
        user_templ_crits[tg_id].pop(0)
        if user_templ_crits[tg_id]:
            await state.set_state(Crits.crit_score)
        elif not user_templ_crits[tg_id]:
            if user_templ_mnoj[tg_id]:
                await state.set_state(Mnoj.mnoj_score)
            elif not user_templ_mnoj[tg_id]:
                await state.set_state(ReportCreating.just_state)


@router_create_report.message(Crits.crit_comm)
async def fill_report_crit_comms(message: Message, state: FSMContext):

    tg_id = message.from_user.id
    crit = user_templ_crits[tg_id].pop(0)

    #  Запись данных в словарь для формирования отчета в конце
    user_report[tg_id]['data'].append(message.text)

    await message.answer(f'• Введите ваш комментарий к критерию "{crit[0]}".')

    if user_templ_crits[tg_id]:
        await state.set_state(Crits.crit_score)
    elif not user_templ_crits[tg_id]:
        await state.set_state(Mnoj.mnoj_score)


@router_create_report.message(Mnoj.mnoj_score)
async def fill_report_mnoj(message: Message, state: FSMContext):

    tg_id = message.from_user.id
    # Удаляем множ из словаря
    mnoj = user_templ_mnoj[tg_id][0]

    #  Запись данных в словарь для формирования отчета в конце
    user_report[tg_id]['data'].append(message.text)

    await message.answer(f'Совершали ли вы действия, предусмотренные множителем "{mnoj[0]}"?\n'
                         f'• Отправьте "1", если да.\n'
                         f'• Отправьте "0", если нет.')

    if mnoj[2] == 1:
        await state.set_state(Mnoj.mnoj_comm)
    elif mnoj[2] == 0:
        # Удаляем множ из словаря
        user_templ_mnoj[tg_id].pop(0)
        if user_templ_mnoj[tg_id]:
            await state.set_state(Mnoj.mnoj_score)
        elif not user_templ_mnoj[tg_id]:
            await state.set_state(ReportCreating.just_state)


@router_create_report.message(Mnoj.mnoj_comm)
async def fill_report_mnoj_comms(message: Message, state: FSMContext):

    tg_id = message.from_user.id
    mnoj = user_templ_mnoj[tg_id].pop(0)

    #  Запись данных в словарь для формирования отчета в конце
    user_report[tg_id]['data'].append(message.text)

    await message.answer(f'• Введите ваш комментарий к множителю "{mnoj[0]}".')

    if user_templ_mnoj[tg_id]:
        await state.set_state(Mnoj.mnoj_score)
    elif not user_templ_mnoj[tg_id]:
        await state.set_state(ReportCreating.just_state)


@router_create_report.message(ReportCreating.just_state)
async def report_creating(message: Message, state: FSMContext):

    tg_id = message.from_user.id

    #  Запись данных в словарь для формирования отчета в конце
    user_report[tg_id]['data'].append(message.text)

    need_to_output_mnoj_string = False
    print(f'DEBUG: Словарь user_report с ответами на вопросы отчета по порядку: {user_report[tg_id]}')

    scores_sum_for_today = 0
    user_crits = user_templ_crits_full[tg_id]
    user_mnoj = user_templ_mnoj_full[tg_id]
    user_report_data = user_report[tg_id]['data']

    count_crits = len(user_crits)
    count_mnoj = len(user_mnoj)

    output_crits = []
    output_mnoj = []
    scores_sum_for_today = 0

    # Сбор критериев в шаблон
    if count_crits != 0:
        for crit_num in range(count_crits):

            crit = user_crits[crit_num]

            crit_name = str(crit[0])
            crit_score = float(crit[1])
            crit_comment = int(crit[2])

            scores_sum_for_today += (crit_score * float(user_report_data[0]))

            if crit_comment == 1:
                output_crits.append(
                    f'• {crit_name}:\n'
                    f'{float(user_report_data[0])} hours = {crit_score * float(user_report_data[0])} scores\n'
                    f'Комментарий: "{user_report_data[1]}"'
                )
                user_report_data.pop(0)
                user_report_data.pop(0)
            else:
                output_crits.append(
                    f"• {crit_name}:\n"
                    f"{float(user_report_data[0])} hours = {crit_score * float(user_report_data[0])} scores"
                )
                user_report_data.pop(0)

            print(f'DEBUG: Словарь user_report с ответами на вопросы отчета по порядку: {user_report[tg_id]}')

        # Соединяем все строки с критериями в одну с помощью join
        result_crits = "\n".join(output_crits)

    # Сбор множителей в шаблон
    scores_sum_for_today_with_mnoj = scores_sum_for_today
    if count_mnoj != 0:

        mnoj_score_sum = float(0)

        for mnoj_num in range(count_mnoj):
            mnoj = user_mnoj[mnoj_num]

            mnoj_name = str(mnoj[0])
            mnoj_score = float(mnoj[1])
            mnoj_comment = int(mnoj[2])

            if user_report_data[0] == "1":
                yes_or_no = 'Да'
                get_or_not = 'Не получен'
                if mnoj_comment:
                    output_mnoj.append(
                        f'• {mnoj_name}: {yes_or_no}\n'
                        f'Множитель x{mnoj_score}: {get_or_not}\n'
                        f'Комментарий: "{user_report_data[1]}"'
                    )
                    user_report_data.pop(0)
                    user_report_data.pop(0)
                else:
                    output_mnoj.append(
                        f'• {mnoj_name}: {yes_or_no}\n'
                        f'Множитель x{mnoj_score}: {get_or_not}'
                    )
                    user_report_data.pop(0)
            else:
                yes_or_no = 'Нет'
                get_or_not = 'Получен'
                if mnoj_comment:
                    output_mnoj.append(
                        f'• {mnoj_name}: {yes_or_no}\n'
                        f'Множитель x{mnoj_score}: {get_or_not}\n'
                        f'Комментарий: "{user_report_data[1]}"'
                    )
                    user_report_data.pop(0)
                    user_report_data.pop(0)
                else:
                    output_mnoj.append(
                        f'• {mnoj_name}: {yes_or_no}\n'
                        f'Множитель x{mnoj_score}: {get_or_not}'
                    )
                    user_report_data.pop(0)

            # Применяем множитель только если ответ "Нет"
            if yes_or_no == 'Нет':
                scores_sum_for_today_with_mnoj *= float(mnoj_score) # Применяем множитель к сумме очков
                need_to_output_mnoj_string = True

        print(f'DEBUG: Словарь user_report с ответами на вопросы отчета по порядку: {user_report[tg_id]}')

    # Если есть хотя бы один множитель, соединям их в одну строку
    if count_mnoj != 0:
        result_mnojs = "\n".join(output_mnoj)
    else:
        result_mnojs = None

    def mnoj_string_in_report(need_to_output_mnoj_string, scores_sum_for_today_with_mnoj):
        if need_to_output_mnoj_string:
            return f"• Применение множителя. Итоговая сумма баллов: {float(scores_sum_for_today_with_mnoj)}\n"
        else:
            return ""

    tg_username = message.from_user.first_name
    templ_id = user_templ_global_score_dict[tg_id][0]
    templ_global_score = user_templ_global_score_dict[tg_id][1]

    # Выводим результат с учетом примененных множителей
    if count_mnoj != 0:

        mnoj_string_output = mnoj_string_in_report(need_to_output_mnoj_string, scores_sum_for_today_with_mnoj)

        templ_global_score_with_changes = float(templ_global_score) + float(scores_sum_for_today_with_mnoj)
        result_save_in_db = await change_template_global_score(templ_id, float(templ_global_score_with_changes))

        if result_save_in_db:
            await message.answer(
                f"Отчет: {tg_username}\n"
                f"................................................\n"
                f"Критерии:\n"
                f"\n"
                f"{result_crits}\n"
                f"................................................\n"
                f"Множители:\n"
                f"\n"
                f"{result_mnojs}\n"
                f"................................................\n"
                f"Итог:\n"
                f"\n"
                f"• Сумма баллов за критерии за межотчетный период: {scores_sum_for_today}\n"
                f"{mnoj_string_output}"
                f"• Глобальная сумма баллов: {templ_global_score_with_changes}", reply_markup=main_keyboard()
            )
            await message.answer('Перешлите отчет в группу вашей команды мотивации')
        else:
            await message.answer('Не удалось обновить глобальные очки в шаблоне')

    else:

        templ_global_score_with_changes = float(templ_global_score) + float(scores_sum_for_today)
        result_save_in_db = await change_template_global_score(templ_id, float(templ_global_score_with_changes))

        if result_save_in_db:
            await message.answer(
                f"Отчет: {tg_username}\n"
                f"................................................\n"
                f"Критерии:\n"
                f"\n"
                f"{result_crits}\n"
                f"................................................\n"
                f"Итог:\n"
                f"\n"
                f"• Итоговая сумма баллов за межотчетный период: {scores_sum_for_today}\n"
                f"• Глобальная сумма баллов: {templ_global_score_with_changes}", reply_markup=main_keyboard()
            )
            await message.answer('Перешлите отчет в группу вашей команды мотивации')
        else:
            await message.answer('Не удалось обновить глобальные очки в шаблоне')

    # Очищение всех состояний
    await state.clear()
    try:
        user_templ_crits.pop(tg_id)
    except KeyError:
        pass
    try:
        user_templ_mnoj.pop(tg_id)
    except KeyError:
        pass
    try:
        user_templ_name.pop(tg_id)
    except KeyError:
        pass
    try:
        user_templ_crits_full.pop(tg_id)
    except KeyError:
        pass
    try:
        user_templ_mnoj_full.pop(tg_id)
    except KeyError:
        pass
    try:
        user_templ_crits_score.pop(tg_id)
    except KeyError:
        pass
    try:
        user_templ_mnoj_score.pop(tg_id)
    except KeyError:
        pass
    try:
        user_templ_crits_comm.pop(tg_id)
    except KeyError:
        pass
    try:
        user_templ_mnoj_comm.pop(tg_id)
    except KeyError:
        pass
    try:
        user_templ_global_score_dict.pop(tg_id)
    except KeyError:
        pass
    try:
        user_report.pop(tg_id)
    except KeyError:
        pass











