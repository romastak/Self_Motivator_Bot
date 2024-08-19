import asyncio
import random

from aiogram.types import Message
from aiogram.filters import Command
from aiogram import F, Router
from keyboards import main_keyboard, create_template_keyboard
from aiogram.fsm.state import StatesGroup, State # Классы состояний
from aiogram.fsm.context import FSMContext # Инструмент управления состояниями


router_cmd_cr_templ = Router()

user_templates = {}

# Классы FSMContext
class Add_crit(StatesGroup): # Наследуемый класс состояний
    name = State()
    score = State()
    comment = State()

class Add_mnoj(StatesGroup):
    name = State()
    score = State()
    comment = State()

# class Add_usl(StatesGroup):
#     name = State()
#     score = State()
#     comment = State()



@router_cmd_cr_templ.message(F.text == "Создать шаблон")
async def cmd_cr_templ(message: Message):

    # Очистка переменных
    telegram_id = message.from_user.id
    if telegram_id in user_templates:
        user_templates.pop(telegram_id)

    await message.answer(
        "Вы вошли в конструктор шаблонов.",
        reply_markup=create_template_keyboard()
    )



@router_cmd_cr_templ.message(F.text == "+ Добавить критерий") # Запускается функция по команде
async def add_crit_one(message: Message, state: FSMContext):

    if state:
        await state.clear()

    await state.set_state(Add_crit.name) # Установить состояние машины
    await message.answer(
        f"Введите новый критерий.\n"
        f"• Например: Изучение Python"
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
    await state.update_data(score=message.text)
    await state.set_state(Add_crit.comment)
    await message.answer(
        f"Нужна ли будет возможность комментирования критерия?\n"
        f"Отправьте:\n"
        f"• 1 - если нужна\n"
        f"• 0 - если не нужна.\n"
    )

@router_cmd_cr_templ.message(Add_crit.comment)
async def add_crit_end(message: Message, state: FSMContext):
    await state.update_data(comment=message.text)
    data = await state.get_data() # возврат словаря с данными пользователя из машины состояний
    telegram_id = message.from_user.id

    # Если для пользователя еще не создан словарь, создаем его
    if telegram_id not in user_templates:
        user_templates[telegram_id] = {"crit": [], "mnoj": []}

    # Добавляем новый критерий в список критериев пользователя
    user_templates[telegram_id]["crit"].append(data)

    await state.clear()
    await message.answer(f"Критерий < {data['name']} > успешно добавлен в шаблон.")
    print(user_templates)  # Для проверки в консоли



@router_cmd_cr_templ.message(F.text == "+ Добавить множитель")
async def add_mnoj_one(message: Message, state: FSMContext):

    if state:
        await state.clear()

    telegram_id = message.from_user.id

    if telegram_id not in user_templates:
        await message.answer("• Сначала добавьте хотя бы один критерий или условие.")
    else:
        await state.set_state(Add_mnoj.name)
        await message.answer(
            f'Добавьте новый множитель на который можно ответить "Да" или "Нет".\n'
            f'• Например: Курили ли вы?'
        )

@router_cmd_cr_templ.message(Add_mnoj.name)
async def add_mnoj_two(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(Add_mnoj.score)
    await message.answer(
        f"Введите число, на которое будут умножаться все "
        f"заработанные баллы за межотчетный период "
        f'при ответе "Нет".\n'
        f"• Например: 2\n"
        f"• (Также можно ввести например 0.5, тогда "
        f"все баллы будут делиться на 2)."
    )

@router_cmd_cr_templ.message(Add_mnoj.score)
async def add_mnoj_three(message: Message, state: FSMContext):
    await state.update_data(score=message.text)
    await state.set_state(Add_mnoj.comment)
    await message.answer(
        f"Нужна ли будет возможность комментирования множителя?\n"
        f"Отправьте:\n"
        f"• 1 - если нужна\n"
        f"• 0 - если не нужна.\n"
    )

@router_cmd_cr_templ.message(Add_mnoj.comment)
async def add_mnoj_end(message: Message, state: FSMContext):
    await state.update_data(comment=message.text)
    data = await state.get_data()
    telegram_id = message.from_user.id

    # Если для пользователя еще не создан словарь, создаем его
    if telegram_id not in user_templates:
        user_templates[telegram_id] = {"crit": [], "mnoj": []}

    # Добавляем новый критерий в список критериев пользователя
    user_templates[telegram_id]["mnoj"].append(data)

    await state.clear()
    await message.answer(f"Множитель < {data['name']} > успешно добавлен в шаблон.")
    print(user_templates)  # Для проверки в консоли



@router_cmd_cr_templ.message(F.text == "Протестировать шаблон")
async def cmd_test_templ(message: Message):

    username = message.from_user.first_name
    telegram_id = message.from_user.id

    if not telegram_id in user_templates:
        await message.answer(f"• Тестирование недоступно так как шаблон пуст.\n"
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
                        f"\n"
                    )
                else:
                    output_crits.append(
                        f"• {crit_name}:\n"
                        f"{random_hours} hours = {crit_score * random_hours} scores"
                        f"\n"
                    )

                scores_sum_for_today += (crit_score * random_hours)

            # Соединяем все строки с критериями в одну с помощью join
            result_crits = "\n".join(output_crits)

        # Сбор множителей в шаблон
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
                        f"\n"
                    )
                else:
                    output_mnoj.append(
                        f"• {mnoj_name}: {yes_or_no}\n"
                        f"Множитель x{mnoj_score}: {get_or_not}"
                        f"\n"
                    )

                mnoj_score_sum += mnoj_score

        # Если "Нет", то выводим итоговую строку с примененным множителем за сегодня
        def get_mnoj_or_not_func(yes_or_no):
                if yes_or_no == "Да":
                    return ""
                else:
                    return "• Применение множителя. Итоговая сумма баллов: " + str(scores_sum_for_today * mnoj_score_sum) + "\n"

        # Если есть хотя бы один множитель
        if int(count_mnoj):
            result_mnojs = "\n".join(output_mnoj)
        else:
            result_mnojs = None

        if result_mnojs != None:
            get_mnoj_or_not = get_mnoj_or_not_func(yes_or_no)
            random_hours = float(random_hours_func('global_score'))

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
                f"{get_mnoj_or_not}"
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



@router_cmd_cr_templ.message(F.text == "Выйти без сохранения")
async def cmd_exit(message: Message):
    await message.answer("Вы вышли из конструктора шаблонов.", reply_markup=main_keyboard())

    telegram_id = message.from_user.id
    if telegram_id in user_templates:
        user_templates.pop(telegram_id)




#
# async def on_start(message: types.Message, state: FSMContext):
#     await message.answer("Добро пожаловать! Вы вошли в конструктор шаблонов.", reply_markup=keyboards.create_template_keyboard())
#
# async def create_template(message: types.Message):
#     await message.answer("Введите новый критерий.", reply_markup=types.ReplyKeyboardRemove())
#     await TemplateCreation.waiting_for_criterion_name.set()
#
# async def process_criterion_name(message: types.Message, state: FSMContext):
#     await state.update_data(criterion_name=message.text)
#     await message.answer("Обозначьте количество получаемых баллов за 1 час деятельности по этому критерию.")
#     await TemplateCreation.waiting_for_criterion_score.set()
#
# async def process_criterion_score(message: types.Message, state: FSMContext):
#     try:
#         score = float(message.text)
#         await state.update_data(criterion_score=score)
#     except ValueError:
#         await message.answer("Пожалуйста, введите корректное число.")
#         return
#     await message.answer("Нужна ли будет возможность комментирования критерия?\nОтправьте:\n• 1 - если нужна\n• 0 - если не нужна.")
#     await TemplateCreation.waiting_for_criterion_comment.set()
#
# async def process_criterion_comment(message: types.Message, state: FSMContext):
#     need_comment = message.text.strip() == "1"
#     user_data = await state.get_data()
#
#     user_id = message.from_user.id
#     user_criterion_dict[user_id] = {
#         "criterion_name": user_data['criterion_name'],
#         "criterion_score": user_data['criterion_score'],
#         "criterion_comment": need_comment
#     }
#
#     await message.answer(f'Критерий "{user_data["criterion_name"]}" добавлен в шаблон.',
#                          reply_markup=keyboards.create_template_keyboard())
#     await state.finish()
#
# async def add_multiplier(message: types.Message):
#     if not user_criterion_dict:
#         await message.answer("Сначала добавьте хотя бы один критерий.")
#     else:
#         await message.answer("Введите новый множитель на который можно ответить 'Да' или 'Нет'.")
#         await TemplateCreation.waiting_for_multiplier_name.set()
#
# async def process_multiplier_name(message: types.Message, state: FSMContext):
#     await state.update_data(multiplier_name=message.text)
#     await message.answer("Введите число, на которое будут умножаться все заработанные баллы.")
#     await TemplateCreation.waiting_for_multiplier_score.set()
#
# async def process_multiplier_score(message: types.Message, state: FSMContext):
#     try:
#         score = float(message.text)
#         await state.update_data(multiplier_score=score)
#     except ValueError:
#         await message.answer("Пожалуйста, введите корректное число.")
#         return
#     await message.answer("Нужна ли будет возможность комментирования множителя?\nОтправьте:\n• 1 - если нужна\n• 0 - если не нужна.")
#     await TemplateCreation.waiting_for_multiplier_comment.set()
#
# async def process_multiplier_comment(message: types.Message, state: FSMContext):
#     need_comment = message.text.strip() == "1"
#     user_data = await state.get_data()
#
#     user_id = message.from_user.id
#     user_mnojitel_dict[user_id] = {
#         "multiplier_name": user_data['multiplier_name'],
#         "multiplier_score": user_data['multiplier_score'],
#         "multiplier_comment": need_comment
#     }
#
#     await message.answer(f'Множитель "{user_data["multiplier_name"]}" добавлен в шаблон.',
#                          reply_markup=keyboards.create_template_keyboard())
#     await state.finish()
#
# async def test_template(message: types.Message):
#     user_id = message.from_user.id
#     if not user_criterion_dict:
#         await message.answer("Тестирование недоступно, так как шаблон пуст. Добавьте хотя бы один критерий.")
#         return
#
#     scores_sum = 0
#     output_criterions = []
#
#     for criterion in user_criterion_dict[user_id].values():
#         criterion_name = criterion["criterion_name"]
#         criterion_score = criterion["criterion_score"]
#         random_hours = random.randint(1, 10)
#         score = criterion_score * random_hours
#         scores_sum += score
#
#         if criterion["criterion_comment"]:
#             output_criterions.append(f"• {criterion_name}:\n{random_hours} hours = {score} scores\nКомментарий: Сегодня я потратил на это {random_hours} часов.")
#         else:
#             output_criterions.append(f"• {criterion_name}:\n{random_hours} hours = {score} scores")
#
#     result_criterions = "\n".join(output_criterions)
#     await message.answer(f"Отчет:\n\nКритерии:\n{result_criterions}\n\nСумма баллов за критерии: {scores_sum}")
#
# async def save_template(message: types.Message, state: FSMContext):
#     user_id = message.from_user.id
#     if not user_criterion_dict:
#         await message.answer("Ваш шаблон пуст. Добавьте хотя бы один критерий или условие.")
#     else:
#         await message.answer("Введите название для вашего шаблона:")
#         await TemplateCreation.waiting_for_template_name.set()
#
# async def process_template_name(message: types.Message, state: FSMContext):
#     template_name = message.text
#     user_id = message.from_user.id
#
#     save_template_to_db(user_id, template_name)
#
#     user_criterion_dict[user_id] = {}
#     user_mnojitel_dict[user_id] = {}
#
#     await message.answer(f"Шаблон '{template_name}' успешно сохранен.", reply_markup=keyboards.main_keyboard())
#     await state.finish()
#
# def save_template_to_db(telegram_id, template_name):
#     connection, cursor = get_connection_and_cursor_vars()
#
#     cursor.execute('SELECT id FROM "user" WHERE telegram_id = %s', (telegram_id,))
#     user_id = cursor.fetchone()[0]
#     cursor.execute('''INSERT INTO user_template (user_id, template_name, key_for_generating)
#                       VALUES (%s, %s, %s) RETURNING id''',
#                    (user_id, template_name, str(random.randint(1, 1000000000000000))))
#     user_template_id = cursor.fetchone()[0]
#
#     for criterion in user_criterion_dict[telegram_id].values():
#         cursor.execute('''INSERT INTO template_criterion (user_template_id, criterion_name, criterion_score, criterion_comment)
#                           VALUES (%s, %s, %s, %s)''',
#                        (user_template_id, criterion["criterion_name"], criterion["criterion_score"], int(criterion["criterion_comment"])))
#
#     for multiplier in user_mnojitel_dict[telegram_id].values():
#         cursor.execute('''INSERT INTO template_multiplier (user_template_id, multiplier_name, multiplier_score, multiplier_comment)
#                           VALUES (%s, %s, %s, %s)''',
#                        (user_template_id, multiplier["multiplier_name"], multiplier["multiplier_score"], int(multiplier["multiplier_comment"])))
#
#     connection.commit()
#     connection.close()
