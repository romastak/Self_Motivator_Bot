import asyncio
import random
import re
from aiogram.types import Message
from aiogram.filters import Command
from aiogram import F, Router, types
from aiogram.fsm.state import StatesGroup, State # Классы состояний
from aiogram.fsm.context import FSMContext # Инструмент управления состояниями
from aiogram.types import CallbackQuery
from aiogram.filters.callback_data import CallbackData
from assets.other_modules.keyboards import main_keyboard, create_template_keyboard, cancel_keyboard, delete_crit_keyboard, delete_mnoj_keyboard
from assets.db_modules.requests import save_user_template, edit_user_template, get_template_data
from assets.command_modules.command_get_templates import Choose_templ


router_cmd_cr_templ = Router()
router_cmd_save_templ = Router()
router_cancel = Router()
router_cmd_delete_crit = Router()
router_delete_crit_el = Router()
router_cmd_delete_mnoj = Router()
router_delete_mnoj_el = Router()

user_templates = {}
is_editing = {}
id_edit_templ = {}


# Классы FSMContext
class Add_crit(StatesGroup): # Наследуемый класс состояний
    name = State()
    score = State()
    comment = State()

class Add_mnoj(StatesGroup):
    name = State()
    score = State()
    what_answer = State()
    comment = State()

class Add_usl(StatesGroup):
    name = State()
    score_if_yes = State()
    score_if_no = State()
    comment = State()

class SaveTemplate(StatesGroup):
    waiting_for_template_name = State()

class CritDelete(StatesGroup):
    which_crit_to_delete = State()


@router_cmd_cr_templ.callback_query(F.data == "edit_templ")
@router_cmd_cr_templ.message(F.text == "Создать шаблон")
async def cmd_cr_templ(event: types.Message | types.CallbackQuery, state: FSMContext):

    # Очистка переменных
    telegram_id = event.from_user.id
    if telegram_id in user_templates:
        user_templates.pop(telegram_id)

    if isinstance(event, types.Message):
        await event.answer(
            "Вы вошли в конструктор шаблонов.",
            reply_markup=create_template_keyboard()
        )

        await state.clear()

        is_editing[telegram_id] = False

    elif isinstance(event, types.CallbackQuery):
        data = await state.get_data()
        chosen_templ = data.get('chosen_templ')[0]
        chosen_templ_name = data.get('chosen_templ')[1]
        await state.update_data(chosen_templ_name=chosen_templ_name)
        id_edit_templ[telegram_id] = chosen_templ
        print(chosen_templ)
        templ_name_val, templ_crit_val, templ_mnoj_val = await get_template_data(key=None, templ_id=chosen_templ)
        # Если для пользователя еще не создан словарь, создаем его
        if telegram_id not in user_templates:
            user_templates[telegram_id] = {"crit": [], "mnoj": [], "usl": []}

        # Записываем данные из БД в user_templates в нужном формате
        print(templ_crit_val, templ_mnoj_val)
        if templ_crit_val:
            index = 0
            for crit in templ_crit_val:
                one_crit_dict = {}
                one_crit_dict['name'] = crit[0]
                one_crit_dict['score'] = crit[1]
                one_crit_dict['comment'] = crit[2]

                crits_list = user_templates[telegram_id]['crit']
                crits_list.append(one_crit_dict)
                index += 1

        if templ_mnoj_val:
            index = 0
            for mnoj in templ_mnoj_val:
                one_mnoj_dict = {}
                one_mnoj_dict['name'] = mnoj[0]
                one_mnoj_dict['score'] = mnoj[1]
                one_mnoj_dict['what_answer'] = mnoj[2]
                one_mnoj_dict['comment'] = mnoj[3]

                crits_list = user_templates[telegram_id]['mnoj']
                crits_list.append(one_mnoj_dict)
                index += 1

        is_editing[telegram_id] = True

        await event.message.answer(
            f'Вы вошли в конструктор шаблона "{templ_name_val}".',
            reply_markup=create_template_keyboard()
        )


@router_cmd_cr_templ.message(F.text == "+ Добавить критерий") # Запускается функция по команде
async def add_crit_one(message: Message, state: FSMContext):

    if state:
        await state.clear()

    await state.set_state(Add_crit.name) # Установить состояние машины
    await message.answer(
        f"• Введите новый критерий.\n"
        f"Например: Изучение Python",
        reply_markup=cancel_keyboard()
    )

# Здесь определяется роутер, эта функция запустится если состояние машины будет = name,
# этим и определяется последовательность

@router_cmd_cr_templ.message(Add_crit.name)
async def add_crit_two(message: Message, state: FSMContext):
    await state.update_data(name=message.text) # Сохранение информации
    await state.set_state(Add_crit.score)
    await message.answer(
        f"Обозначьте количество получаемых баллов за 1 час "
        f"деятельности по этому критерию.\n"
        f"• Например: 1.5\n"
        f"• (Также можно ввести отрицательное число, тогда "
        f"баллы за этот критерий будут вычитаться)"
    )


@router_cmd_cr_templ.message(Add_crit.score)
async def add_crit_three(message: Message, state: FSMContext):
    await state.update_data(score=float(message.text))
    await state.set_state(Add_crit.comment)
    await message.answer(
        f"Нужна ли будет возможность комментирования критерия?\n"
        f"Отправьте:\n"
        f"• 1 - если нужна\n"
        f"• 0 - если не нужна.\n"
    )


@router_cmd_cr_templ.message(Add_crit.comment)
async def add_crit_end(message: Message, state: FSMContext):
    await state.update_data(comment=int(message.text))
    data = await state.get_data() # возврат словаря с данными пользователя из машины состояний
    telegram_id = message.from_user.id

    # Если для пользователя еще не создан словарь, создаем его
    if telegram_id not in user_templates:
        user_templates[telegram_id] = {"crit": [], "mnoj": [], "usl": []}

    # Добавляем новый критерий в список критериев пользователя
    user_templates[telegram_id]["crit"].append(data)

    await state.clear()
    await message.answer(f'Критерий "{data["""name"""]}" успешно добавлен в шаблон.', reply_markup=create_template_keyboard())
    print(user_templates)  # Для проверки в консоли


@router_cmd_cr_templ.message(F.text == "+ Добавить множитель")
async def add_mnoj_one(message: Message, state: FSMContext):

    if state:
        await state.clear()

    telegram_id = message.from_user.id

    user_crits = user_templates.get(telegram_id)
    print(f'DEBUG: {user_crits}')
    user_crits_dict = user_crits.get('crit')

    if telegram_id not in user_templates:
        await message.answer("• Сначала добавьте хотя бы один критерий или условие.")
    else:
        if not user_crits_dict:
            await message.answer("• Сначала добавьте хотя бы один критерий или условие.")
        else:
            await state.set_state(Add_mnoj.name)
            await message.answer(
                f'• Добавьте новый множитель на который можно ответить "Да" или "Нет".\n'
                f'(Например: Курили ли вы?)',
                reply_markup=cancel_keyboard()
            )


@router_cmd_cr_templ.message(Add_mnoj.name)
async def add_mnoj_two(message: Message, state: FSMContext):
    tg_id = message.from_user.id
    await state.update_data(name=message.text)
    await state.set_state(Add_mnoj.what_answer)
    await message.answer(
        f'При каком ответе на ваш вопрос будут применяться множитель и начисляться очки?.\n'
        f'• Отправьте:\n'
        f'• 1 - если это ответ "Да"\n'
        f'• 0 - если это ответ "Нет"\n',
        reply_markup=cancel_keyboard()
    )


@router_cmd_cr_templ.message(Add_mnoj.what_answer)
async def add_mnoj_three(message: Message, state: FSMContext):
    await state.update_data(what_answer=int(message.text))
    await state.set_state(Add_mnoj.score)
    data = await state.get_data()
    answer = data.get('what_answer')
    yes_or_no = None

    if answer == 1:
        yes_or_no = 'Да'
    elif answer == 0:
        yes_or_no = 'Нет'

    await message.answer(
        f"• Введите число, на которое будут умножаться все "
        f"заработанные баллы за межотчетный период "
        f'при ответе "{yes_or_no}".\n'
        f"• Например: 2\n"
        f"• (Также можно ввести например 0.5, тогда "
        f"все баллы будут делиться на 2)."
    )

@router_cmd_cr_templ.message(Add_mnoj.score)
async def add_mnoj_four(message: Message, state: FSMContext):
    await state.update_data(score=float(message.text))
    await state.set_state(Add_mnoj.comment)
    await message.answer(
        f"Нужна ли будет возможность комментирования множителя?\n"
        f"Отправьте:\n"
        f"• 1 - если нужна\n"
        f"• 0 - если не нужна.\n"
    )

@router_cmd_cr_templ.message(Add_mnoj.comment)
async def add_mnoj_end(message: Message, state: FSMContext):
    await state.update_data(comment=int(message.text))
    data = await state.get_data()
    telegram_id = message.from_user.id

    # Если для пользователя еще не создан словарь, создаем его
    if telegram_id not in user_templates:
        user_templates[telegram_id] = {"crit": [], "mnoj": [], "usl": []}

    # Добавляем новый множитель в список множителей пользователя
    user_templates[telegram_id]["mnoj"].append(data)

    await state.clear()
    await message.answer(f'Множитель "{data["""name"""]}" успешно добавлен в шаблон.', reply_markup=create_template_keyboard())
    print(user_templates)  # Для проверки в консоли


@router_cmd_cr_templ.message(F.text == "+ Добавить условие")
async def add_usl_one(message: Message, state: FSMContext):

    if state:
        await state.clear()

    await state.set_state(Add_usl.name) # Установить состояние машины
    await message.answer(
        f'• Введите новое условие.\n'
        f'Например: Прокрастинировал сегодня?',
        reply_markup=cancel_keyboard()
    )


@router_cmd_cr_templ.message(Add_usl.name)
async def add_usl_one(message: Message, state: FSMContext):

    await state.update_data(name=message.text)
    await state.set_state(Add_usl.score_if_yes) # Установить состояние машины
    await message.answer(
        f'• Введите количество получаемых очков при ответе "Да".\n'
        f'Например: 2.5\n'
        f'(Можно ввести отрицательное число, тогда '
        f'введенные баллы будут вычитаться).\n'
        f'(Можно отправить "0", тогда очки не будут меняться)',
        reply_markup=cancel_keyboard()
    )


@router_cmd_cr_templ.message(Add_usl.score_if_yes)
async def add_usl_one(message: Message, state: FSMContext):

    await state.update_data(score_if_yes=message.text)
    await state.set_state(Add_usl.score_if_no) # Установить состояние машины
    await message.answer(
        f'• Введите количество получаемых очков при ответе "Нет".\n'
        f'Например: 2.5\n'
        f'(Можно ввести отрицательное число, тогда '
        f'введенные баллы будут вычитаться).\n'
        f'(Можно отправить "0", тогда очки не будут меняться)',
        reply_markup=cancel_keyboard()
    )


@router_cmd_cr_templ.message(Add_usl.score_if_no)
async def add_usl_one(message: Message, state: FSMContext):

    await state.update_data(score_if_no=message.text)
    await state.set_state(Add_usl.comment) # Установить состояние машины
    await message.answer(
        f"Нужна ли будет возможность комментирования условия?\n"
        f"Отправьте:\n"
        f"• 1 - если нужна\n"
        f"• 0 - если не нужна.\n"
    )


@router_cmd_cr_templ.message(Add_usl.comment)
async def add_mnoj_end(message: Message, state: FSMContext):
    await state.update_data(comment=int(message.text))
    data = await state.get_data()
    telegram_id = message.from_user.id

    # Если для пользователя еще не создан словарь, создаем его
    if telegram_id not in user_templates:
        user_templates[telegram_id] = {"crit": [], "mnoj": [], "usl": []}

    # Добавляем новое условие в список множителей пользователя
    user_templates[telegram_id]["usl"].append(data)

    await state.clear()
    await message.answer(f'Условие "{data["""name"""]}" успешно добавлено в шаблон.', reply_markup=create_template_keyboard())
    print(user_templates)  # Для проверки в консоли


@router_cmd_cr_templ.message(F.text == "Посмотреть структуру шаблона")
async def cmd_test_templ(message: Message, state: FSMContext):

    ig_id = message.from_user.id

    if not ig_id in user_templates:
        await message.answer(f"Просмотр структуры недоступен так как шаблон пуст.\n"
                             f"• Добавьте хотя бы один критерий или условие.")
    else:
        current_user_templ = user_templates.get(ig_id)
        templ_crits_val_dict = current_user_templ.get('crit')
        templ_mnoj_val_dict = current_user_templ.get('mnoj')
        templ_usl_val_dict = current_user_templ.get('usl')

        if not templ_crits_val_dict and not templ_usl_val_dict:
            await message.answer(f"Просмотр структуры недоступен так как шаблон пуст.\n"
                                 f"• Добавьте хотя бы один критерий или условие.")
        else:
            templ_data = await state.get_data()
            templ_name = templ_data.get('chosen_templ_name')
            if templ_name == None:
                templ_name = 'Новый шаблон'

            templ_crits_val = []
            templ_mnoj_val = []
            templ_usl_val = []

            output_crits = []
            output_mnoj = []
            output_usl = []

            for one_crit in templ_crits_val_dict:
                print(one_crit)
                crit_name = one_crit.get('name')
                crit_score = one_crit.get('score')
                crit_comment = one_crit.get('comment')
                crit_tuple = (crit_name, crit_score, crit_comment)
                templ_crits_val.append(crit_tuple)

            for one_mnoj in templ_mnoj_val_dict:
                mnoj_name = one_mnoj.get('name')
                mnoj_score = one_mnoj.get('score')
                mnoj_answer = one_mnoj.get('what_answer')
                mnoj_comment = one_mnoj.get('comment')
                mnoj_tuple = (mnoj_name, mnoj_score, mnoj_answer, mnoj_comment)
                templ_mnoj_val.append(mnoj_tuple)

            for one_usl in templ_usl_val_dict:
                usl_name = one_usl.get('name')
                usl_score_if_yes = one_usl.get('score_if_yes')
                usl_score_if_no = one_usl.get('score_if_no')
                usl_comment = one_usl.get('comment')
                usl_tuple = (usl_name, usl_score_if_yes, usl_score_if_no, usl_comment)
                templ_usl_val.append(usl_tuple)

            print(f'DEBUG: crits: {templ_crits_val}\n'
                  f'DEBUG: mnoj: {templ_mnoj_val}\n'
                  f'DEBUG: usl: {templ_usl_val}')

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
                    mnoj_what_answer = mnoj[2]
                    mnoj_comment = mnoj[3]

                    mnoj_answer_word = None

                    if mnoj_what_answer == 1:
                        mnoj_answer_word = 'Да'
                    else:
                        mnoj_answer_word = 'Нет'

                    if mnoj_comment == 1:
                        mnoj_comment = 'Да'
                    else:
                        mnoj_comment = 'Нет'

                    output_mnoj.append(f'• "{mnoj_name}"\n'
                                       f'При ответе "{mnoj_answer_word}" заработанные очки умножатся на "x{mnoj_score}"\n'
                                       f'Возможность комментирования: "{mnoj_comment}"')

                result_mnojs = "\n".join(output_mnoj)

            if templ_mnoj_val:
                await message.answer(f'Структура шаблона "{templ_name}":\n'
                                                 f'................................................\n'
                                                 f'Критерии:\n'
                                                 f'\n'
                                                 f'{result_crits}\n'
                                                 f'................................................\n'
                                                 f'Множители:\n'
                                                 f'\n'
                                                 f'{result_mnojs}')
            else:
                await message.answer(f'Структура шаблона "{templ_name}":\n'
                                                 f'................................................\n'
                                                 f'Критерии:\n'
                                                 f'\n'
                                                 f'{result_crits}')

                #  Сбор условий
                if templ_usl_val:
                    for usl in templ_usl_val:
                        usl_name = usl[0]
                        usl_score_if_yes = usl[1]
                        usl_score_if_no = usl[2]
                        usl_comment = usl[3]

                        usl_comment_word = None

                        score_val = None

                        if usl_comment == 1:
                            usl_comment_word = 'Да'
                        else:
                            usl_comment_word = 'Нет'

                        if float(usl_score_if_yes) < 0:
                            final_val_yes = f'уменьшатся на {usl_score_if_yes}'
                        elif float(usl_score_if_yes) > 0:
                            final_val_yes = f'увеличатся на {usl_score_if_yes}'
                        elif float(usl_score_if_yes) == 0:
                            final_val_yes = 'не изменятся.'

                        if float(usl_score_if_no) < 0:
                            final_val_no = f'уменьшатся на {usl_score_if_no}'
                        elif float(usl_score_if_no) > 0:
                            final_val_no = f'увеличатся на {usl_score_if_no}'
                        elif float(usl_score_if_no) == 0:
                            final_val_no = 'не изменятся.'

                        output_usl.append(f'• "{usl_name}"\n'
                                           f'При ответе "Да" заработанные очки {final_val_yes}\n'
                                           f'При ответе "Нет" заработанные очки {final_val_no}\n'
                                           f'Возможность комментирования: "{usl_comment_word}"')

                    result_usls = "\n".join(output_usl)

                if result_usls and not templ_mnoj_val and not templ_crits_val:
                    await message.answer(f'Структура шаблона "{templ_name}":\n'
                                         f'................................................\n'
                                         f'Условия:\n'
                                         f'\n'
                                         f'{result_usls}')

                elif result_usls and templ_mnoj_val and not templ_crits_val:
                    await message.answer(f'Структура шаблона "{templ_name}":\n'
                                         f'................................................\n'
                                         f'Условия:\n'
                                         f'\n'
                                         f'{result_usls}\n'
                                         f'................................................\n'
                                         f'Множители:\n'
                                         f'\n'
                                         f'{result_mnojs}')

                elif result_usls and not templ_mnoj_val and templ_crits_val:
                    await message.answer(f'Структура шаблона "{templ_name}":\n'
                                         f'................................................\n'
                                         f'Критерии:\n'
                                         f'\n'
                                         f'{result_crits}\n'
                                         f'................................................\n'
                                         f'Условия:\n'
                                         f'\n'
                                         f'{result_usls}\n'
                                         f'................................................\n'
                                         )

                elif result_usls and templ_mnoj_val and templ_crits_val:
                    await message.answer(f'Структура шаблона "{templ_name}":\n'
                                         f'................................................\n'
                                         f'Критерии:\n'
                                         f'\n'
                                         f'{result_crits}\n'
                                         f'................................................\n'
                                         f'Условия:\n'
                                         f'\n'
                                         f'{result_usls}\n'
                                         f'................................................\n'
                                         f'Множители:\n'
                                         f'\n'
                                         f'{result_mnojs}'
                                         )

                elif not result_usls and templ_mnoj_val and templ_crits_val:
                    await message.answer(f'Структура шаблона "{templ_name}":\n'
                                         f'................................................\n'
                                         f'Критерии:\n'
                                         f'\n'
                                         f'{result_crits}\n'
                                         f'................................................\n'
                                         f'Множители:\n'
                                         f'\n'
                                         f'{result_mnojs}'
                                         )

                elif result_usls and templ_mnoj_val and templ_crits_val:
                    await message.answer(f'Структура шаблона "{templ_name}":\n'
                                         f'................................................\n'
                                         f'Критерии:\n'
                                         f'\n'
                                         f'{result_crits}\n'
                                         f'................................................\n'
                                         f'Условия:\n'
                                         f'\n'
                                         f'{result_usls}\n'
                                         f'................................................\n'
                                         f'Множители:\n'
                                         f'\n'
                                         f'{result_mnojs}'
                                         )

                elif result_usls and templ_crits_val and not templ_mnoj_val:
                    await message.answer(f'Структура шаблона "{templ_name}":\n'
                                         f'................................................\n'
                                         f'Критерии:\n'
                                         f'\n'
                                         f'{result_crits}\n'
                                         )

                elif not result_usls and templ_mnoj_val and templ_crits_val:
                    await message.answer(f'Структура шаблона "{templ_name}":\n'
                                         f'................................................\n'
                                         f'Критерии:\n'
                                         f'\n'
                                         f'{result_crits}\n'
                                         f'................................................\n'
                                         f'Множители:\n'
                                         f'\n'
                                         f'{result_mnojs}'
                                         )

                elif templ_mnoj_val:
                    await message.answer(f'Структура шаблона "{templ_name}":\n'
                                         f'................................................\n'
                                         f'Критерии:\n'
                                         f'\n'
                                         f'{result_crits}\n'
                                         f'................................................\n'
                                         f'Множители:\n'
                                         f'\n'
                                         f'{result_mnojs}')
                else:
                    await message.answer(f'Структура шаблона "{templ_name}":\n'
                                         f'................................................\n'
                                         f'Критерии:\n'
                                         f'\n'
                                         f'{result_crits}')

@router_cmd_cr_templ.message(F.text == "Протестировать шаблон случайными значениями")
async def cmd_test_templ(message: Message):

    username = message.from_user.first_name
    telegram_id = message.from_user.id
    need_to_output_mnoj_string = False

    if not telegram_id in user_templates:
        await message.answer(f"Тестирование недоступно так как шаблон пуст.\n"
                             f"• Добавьте хотя бы один критерий или условие.")
    else:
        current_user_templ = user_templates.get(telegram_id)
        current_user_crits = current_user_templ.get('crit')
        current_user_mnoj = current_user_templ.get('mnoj')
        if current_user_crits == []:
            await message.answer(f"Тестирование недоступно так как шаблон пуст.\n"
                                 f"• Добавьте хотя бы один критерий или условие.")
        else:
            def random_hours_func(what_elem):
                if what_elem == "crit":
                    random_hours = random.randint(1, 10)
                if what_elem == "global_score":
                    random_hours = random.randint(20, 200)
                return float(random_hours)

            def random_mnojitel_get_or_not():
                rand_int = random.randint(1, 2)
                if rand_int == 1:
                    return "Нет", "Получен", "не занимался"
                else:
                    return "Да", "Не получен", "занимался"

            current_user_template = user_templates.get(telegram_id, {})
            crit_list = current_user_template.get('crit', [])
            mnoj_list = current_user_template.get('mnoj', [])

            count_crits = len(crit_list)
            count_mnoj = len(mnoj_list)

            print("Crit:", crit_list, count_crits)
            print("Mnoj:", mnoj_list, count_mnoj)

            output_crits = []
            output_mnoj = []
            scores_sum_for_today = 0

            # Сбор критериев в шаблон
            if count_crits != 0:
                for crit_num in range(count_crits):
                    random_hours = random_hours_func("crit")
                    crit = crit_list[crit_num]

                    crit_name = str(crit.get('name'))
                    crit_score = float(crit.get('score'))
                    crit_comment = int(crit.get('comment'))

                    if crit_comment == 1:
                        output_crits.append(
                            f"• {crit_name}:\n"
                            f"{random_hours} hours = {crit_score * random_hours} scores\n"
                            f"Комментарий: Сегодня я потратил на это {random_hours} hours."
                        )
                    else:
                        output_crits.append(
                            f"• {crit_name}:\n"
                            f"{random_hours} hours = {crit_score * random_hours} scores"
                        )

                    scores_sum_for_today += (crit_score * random_hours)

                # Соединяем все строки с критериями в одну с помощью join
                result_crits = "\n".join(output_crits)

            # Сбор множителей в шаблон
            applied_mnoj = 1
            if count_mnoj != 0:
                mnoj_score_sum = float(0)

                for mnoj_num in range(count_mnoj):
                    mnoj = mnoj_list[mnoj_num]
                    yes_or_no, get_or_not, do_or_not = random_mnojitel_get_or_not()

                    mnoj_name = str(mnoj.get('name'))
                    mnoj_score = float(mnoj.get('score'))
                    mnoj_comment = int(mnoj.get('comment'))

                    if mnoj_comment == 1:
                        output_mnoj.append(
                            f"• {mnoj_name}: {yes_or_no}\n"
                            f"Множитель x{mnoj_score}: {get_or_not}\n"
                            f"Комментарий: Сегодня я {do_or_not} этим."
                        )
                    else:
                        output_mnoj.append(
                            f"• {mnoj_name}: {yes_or_no}\n"
                            f"Множитель x{mnoj_score}: {get_or_not}"
                        )

                    # Применяем множитель только если ответ "Нет"
                    if yes_or_no == "Нет":
                        applied_mnoj *= mnoj_score  # Умножаем текущий множитель на итоговый
                        need_to_output_mnoj_string = True

            # Если есть хотя бы один множитель
            if count_mnoj != 0:
                result_mnojs = "\n".join(output_mnoj)
            else:
                result_mnojs = None

            def mnoj_string_in_report(need_to_output_mnoj_string, final_score):
                if need_to_output_mnoj_string:
                    return f"• Применение множителя. Итоговая сумма баллов: {final_score}\n"
                else:
                    return ""

            # Выводим результат с учетом примененных множителей
            if result_mnojs != None:
                random_hours = float(random_hours_func('global_score'))
                final_score = scores_sum_for_today * applied_mnoj

                await message.answer(
                    f"Отчет: {username}\n"
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
                    f"{mnoj_string_in_report(need_to_output_mnoj_string, final_score)}"
                    f"• Глобальная сумма баллов: {random_hours + scores_sum_for_today * mnoj_score}"
                )

            else:
                random_hours = float(random_hours_func('global_score'))

                await message.answer(
                    f"Отчет: {username}\n"
                    f"................................................\n"
                    f"Критерии:\n"
                    f"\n"
                    f"{result_crits}\n"
                    f"................................................\n"
                    f"Итог:\n"
                    f"\n"
                    f"• Итоговая сумма баллов за межотчетный период: {scores_sum_for_today}\n"
                    f"• Глобальная сумма баллов: {random_hours + scores_sum_for_today}"
                )

            scores_sum_for_today = 0


@router_cmd_delete_crit.message(F.text == "- Удалить критерий")
async def cmd_delete_crit(message: Message):
    telegram_id = message.from_user.id

    if telegram_id in user_templates:
        current_user_templ = user_templates.get(telegram_id)
        current_user_crits = current_user_templ.get('crit')

        if current_user_crits != []:
            print('крит есть')
            print(current_user_crits)
            crits_list = []
            for crit_name in current_user_crits:
                clear_crit_name = crit_name.get('name')
                crits_list.append(clear_crit_name)
            await message.answer(text='Выберите критерий для удаления:', reply_markup=delete_crit_keyboard(crits_list))

        else:
            await message.answer('Вы не добавили ни одного критерия')

    else:
        await message.answer('Вы не добавили ни одного критерия')

@router_delete_crit_el.callback_query(lambda callback: re.match(r"^crit_num_\d+$", callback.data))
async def delete_crit_el(callback: CallbackQuery):
    telegram_id = callback.from_user.id
    match = re.match(r"^crit_num_(\d+)$", callback.data)

    if match:
        crit_num = int(match.group(1))  # Извлекаем номер критерия
        current_user_templ = user_templates.get(telegram_id)
        current_user_crits = current_user_templ.get('crit')
        current_user_mnoj = current_user_templ.get('mnoj')

        if len(current_user_crits) == 1 and current_user_mnoj != []:
            await callback.message.answer(f"Последний критерий удалить нельзя, так как в шаблоне присутствуют множители.\n"
                                          f"Для удаления последнего критерия удалите множители.")
        else:
            print(f'DEBUG: {user_templates} 1')
            del user_templates[telegram_id]['crit'][crit_num]
            print(f'DEBUG: {current_user_templ} 2')
            await callback.message.answer(f"Критерий удален")

    await callback.answer()


@router_cmd_delete_mnoj.message(F.text == "- Удалить множитель")
async def cmd_delete_mnoj(message: Message):
    telegram_id = message.from_user.id

    if telegram_id in user_templates:
        current_user_templ = user_templates.get(telegram_id)
        current_user_mnoj = current_user_templ.get('mnoj')

        if current_user_mnoj != []:
            print('множ есть')
            print(current_user_mnoj)
            mnoj_list = []
            for mnoj_name in current_user_mnoj:
                clear_mnoj_name = mnoj_name.get('name')
                mnoj_list.append(clear_mnoj_name)
            await message.answer(text='Выберите множитель для удаления:', reply_markup=delete_mnoj_keyboard(mnoj_list))

        else:
            await message.answer('Вы не добавили ни одного множителя')

    else:
        await message.answer('Вы не добавили ни одного множителя')

@router_delete_mnoj_el.callback_query(lambda callback: re.match(r"^mnoj_num_\d+$", callback.data))
async def delete_mnoj_el(callback: CallbackQuery):
    telegram_id = callback.from_user.id
    match = re.match(r"^mnoj_num_(\d+)$", callback.data)

    if match:
        mnoj_num = int(match.group(1))  # Извлекаем номер критерия
        current_user_templ = user_templates.get(telegram_id)
        current_user_mnoj = current_user_templ.get('mnoj')
        del current_user_mnoj[mnoj_num]
        await callback.message.answer(f"Множитель удален")

    await callback.answer()


@router_cmd_cr_templ.message(F.text == "- Удалить условие")
async def add_usl_one(message: Message):
    await message.answer("Функция находится в разработке")


@router_cmd_cr_templ.message(F.text == "Выйти без сохранения")
async def cmd_exit(message: Message):
    await message.answer("Вы вышли из конструктора шаблонов.", reply_markup=main_keyboard())

    telegram_id = message.from_user.id
    if telegram_id in user_templates:
        user_templates.pop(telegram_id)


@router_cancel.message(F.text == "Отмена")
async def cmd_cancel(message: Message, state: FSMContext):
    telegram_id = message.from_user.id

    await state.clear()
    await message.answer("Создание отменено", reply_markup=create_template_keyboard())


@router_cmd_save_templ.message(F.text == "Сохранить шаблон")
async def cmd_save_templ(message: Message, state: FSMContext):
    telegram_id = message.from_user.id
    print(user_templates.get(telegram_id))
    current_user_templ = user_templates.get(telegram_id)

    if current_user_templ:
        # Переходим в состояние ожидания имени шаблона
        if is_editing[telegram_id] == False:
            await message.answer("• Введите название шаблона.")
        elif is_editing[telegram_id] == True:
            await message.answer("• Введите новое название шаблона.")

        await state.set_state(SaveTemplate.waiting_for_template_name)
    else:
        await message.answer("Шаблон пуст.")

@router_cmd_save_templ.message(SaveTemplate.waiting_for_template_name)
async def get_template_name(message: Message, state: FSMContext):
    template_name = message.text  # Получаем имя шаблона от пользователя
    telegram_id = message.from_user.id
    key_for_generating = str(random.randint(1000000000, 9999999999))
    current_user_templ = user_templates.get(telegram_id)

    if not is_editing[telegram_id]:
        await save_user_template(
            telegram_id=telegram_id,
            username=message.from_user.first_name,
            template_name=template_name,
            key_for_generating=key_for_generating,
            crits=current_user_templ['crit'],
            mnojs=current_user_templ['mnoj']
        )

        await message.answer(f'Ваш шаблон "{template_name}" успешно сохранен!', reply_markup=main_keyboard())
        await state.clear()
        if telegram_id in user_templates:
            user_templates.pop(telegram_id)

    elif is_editing[telegram_id]:
        chosen_templ_id = id_edit_templ[telegram_id]

        await edit_user_template(
            telegram_id=telegram_id,
            username=message.from_user.first_name,
            template_name=template_name,
            crits=current_user_templ['crit'],
            mnojs=current_user_templ['mnoj'],
            chosen_templ_id=chosen_templ_id
        )

        await message.answer(f'Ваш шаблон "{template_name}" успешно отредактирован!', reply_markup=main_keyboard())
        await state.clear()
        if telegram_id in user_templates:
            user_templates.pop(telegram_id)

        id_edit_templ.pop(telegram_id)
