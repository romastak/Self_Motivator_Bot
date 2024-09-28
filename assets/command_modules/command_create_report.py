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
from assets.db_modules.requests import save_user_template, edit_user_template, get_template_data, get_user_templates
from assets.command_modules.command_get_templates import Choose_templ

router_create_report = Router()

user_templ_crits = {}
user_templ_mnoj = {}
user_templ_name = {}

user_templ_crits_score = {}
user_templ_mnoj_score = {}

user_templ_crits_comm = {}
user_templ_mnoj_comm = {}


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

        print(templ_name_val)
        print(templ_crit_val)
        print(templ_mnoj_val)
        await state.set_state(Crits.crit_score)

        user_templ_name[tg_id] = templ_name_val
        if templ_mnoj_val:
            user_templ_mnoj[tg_id] = templ_mnoj_val
        if templ_crit_val:
            user_templ_crits[tg_id] = templ_crit_val
            await callback.message.edit_text(f'• Введите количество времени в часах сколько вы потратили за межотчетный'
                                                f' период на критерий "{templ_crit_val[0][0]}".\n'
                                                f'Например: 2.5')

        if templ_crit_val[0][2] == 1:
            await state.set_state(Crits.crit_comm)
        elif templ_crit_val[0][2] == 0:
            # Удаляем критерий из словаря
            user_templ_crits[tg_id].pop(0)
            print(user_templ_crits)
            if user_templ_crits[tg_id]:
                await state.set_state(Crits.crit_score)
            elif not user_templ_crits[tg_id]:
                if user_templ_mnoj[tg_id]:
                    await state.set_state(Mnoj.mnoj_score)
                elif not user_templ_mnoj[tg_id]:
                    await state.set_state(ReportCreating.just_state)
                print('crits done')


@router_create_report.message(Crits.crit_score)
async def fill_report_crits(message: Message, state: FSMContext):

    tg_id = message.from_user.id
    # Удаляем критерий из словаря
    crit = user_templ_crits[tg_id][0]
    print(user_templ_crits)

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
            print('crits done')


@router_create_report.message(Crits.crit_comm)
async def fill_report_crit_comms(message: Message, state: FSMContext):

    tg_id = message.from_user.id
    crit = user_templ_crits[tg_id].pop(0)
    print(user_templ_crits)

    await message.answer(f'• Введите ваш комментарий к критерию "{crit[0]}".')

    if user_templ_crits[tg_id]:
        await state.set_state(Crits.crit_score)
    elif not user_templ_crits[tg_id]:
        await state.set_state(Mnoj.mnoj_score)
        print('crits done')


@router_create_report.message(Mnoj.mnoj_score)
async def fill_report_mnoj(message: Message, state: FSMContext):

    tg_id = message.from_user.id
    # Удаляем множ из словаря
    mnoj = user_templ_mnoj[tg_id][0]
    print(user_templ_mnoj)

    await message.answer(f'Совершали ли вы действия, предусмотренные множителем "{mnoj[0]}"?\n'
                         f'• Отправьте "1", если да.\n'
                         f'• Отправьте "0", если нет.')

    if mnoj[2] == 1:
        await state.set_state(Mnoj.mnoj_comm)
    elif mnoj[2] == 0:
        # Удаляем множ из словаря
        user_templ_mnoj[tg_id].pop(0)
        print(user_templ_mnoj)
        if user_templ_mnoj[tg_id]:
            await state.set_state(Mnoj.mnoj_score)
        elif not user_templ_mnoj[tg_id]:
            await state.set_state(ReportCreating.just_state)
            print('Mnoj done')


@router_create_report.message(Mnoj.mnoj_comm)
async def fill_report_mnoj_comms(message: Message, state: FSMContext):

    tg_id = message.from_user.id
    mnoj = user_templ_mnoj[tg_id].pop(0)
    print(user_templ_mnoj)

    await message.answer(f'• Введите ваш комментарий к множителю "{mnoj[0]}".')

    if user_templ_mnoj[tg_id]:
        await state.set_state(Mnoj.mnoj_score)
    elif not user_templ_mnoj[tg_id]:
        await state.set_state(ReportCreating.just_state)
        print('Mnoj done')


@router_create_report.message(ReportCreating.just_state)
async def report_creating(message: Message, state: FSMContext):
    tg_id = message.from_user.id
    await message.answer('Отчет закончен. Только я вам его не отдам. У вас дакУментов нету.')








# TODO i need to add comment in filling report and finished filling report with global score changes in db











