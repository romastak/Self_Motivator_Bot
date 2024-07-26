import tgcrypto
from pyrogram import Client, filters
from pyrogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
import sqlite3
import asyncio
import keyboards
import random

user_states = {}  # Хранение состояния пользователей

user_criterion_dict = {}
user_mnojitel_dict = {}

criterion_num = 0
mnojitel_num = 0

once_crit_is_exist = False
once_mnoj_is_exist = False

def add_template(user_id, question, response_type):
    conn = sqlite3.connect('reports.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO templates (user_id, question, response_type) VALUES (?, ?, ?)', (user_id, question, response_type))
    conn.commit()
    conn.close()

def comment_in_report(need_comment):
    if int(need_comment):
        need_comment = True
    else:
        need_comment = False
    return need_comment

def create_template_main(client, message, add_template):
    global user_states, criterion_num, user_criterion_dict, once_crit_is_exist, once_mnoj_is_exist

    @client.on_message(filters.text & filters.regex("Создать шаблон"))
    async def create_template(client, message):
        user_id = message.from_user.id

        answers = {}

        # Проверка наличия пользователя в базе данных
        conn = sqlite3.connect('reports.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        user = cursor.fetchone()
        if not user:
            cursor.execute('INSERT INTO users (user_id, name) VALUES (?, ?)', (user_id, message.from_user.first_name))
            conn.commit()
        conn.close()

        keyboard = keyboards.create_template_keyboard()
        await message.reply_text("Конструктор шаблона:", reply_markup=keyboard)

    # Функция для добавления критерия в шаблон
    @client.on_message(filters.text & filters.regex("Добавить критерий"))
    async def add_criterion(client, message):
        global criterion_num, once_crit_is_exist
        user_id = message.from_user.id
        criterion = await ask_question(client, user_id, f"Введите новый критерий\n"
                                                        f"• Например: Изучение Python")
        criterion_scores = await ask_question(client, user_id, f"Обозначьте количество получаемых баллов за 1 час"
                                                               f" деятельности по этому критерию\n"
                                                               f"• Например: 1.5\n"
                                                               f"• (Также можно ввести отрицательное число, тогда"
                                                               f" баллы за этот критерий будут вычитаться)")
        criterion_scores = float(criterion_scores)
        need_comment = await ask_question(client, user_id, f"Нужна ли будет возможность комментирования критерия?\n"
                                                           f"Отправьте:\n"
                                                           f"• 1 - если нужна\n"
                                                           f"• 0 - если не нужна.\n")

        need_comment_var = comment_in_report(need_comment)

        criterion_num += 1
        user_criterion_dict["criterion_" + str(criterion_num)] = [criterion, criterion_scores, need_comment_var]
        await client.send_message(user_id, f'Критерий "{criterion}" добавлен в шаблон.')
        once_crit_is_exist = True
        print(user_criterion_dict)

    # Функция для добавления множителя в шаблон
    @client.on_message(filters.text & filters.regex("Добавить множитель"))
    async def add_criterion(client, message):
        global mnojitel_num, once_mnoj_is_exist
        user_id = message.from_user.id
        mnojitel = await ask_question(client, user_id, f"Введите новый множитель на который можно ответить Да"
                                                       f" или Нет\n"
                                                       f"• Например: Курили ли вы?")
        mnojitel_scores = await ask_question(client, user_id, f"Введите число, на которое будут умножаться все"
                                                              f" заработанные баллы за период одного отчета"
                                                              f" при ответе 'Нет'\n"
                                                              f"• Например: 2\n"
                                                              f"• (Также можно ввести например 0.5, тогда"
                                                              f" все баллы будут делиться на 2)"
                                             )
        mnojitel_scores = float(mnojitel_scores)

        need_comment = await ask_question(client, user_id, f"Нужна ли будет возможность комментирования множителя?\n"
                                                           f"Отправьте:\n"
                                                           f"• 1 - если нужна\n"
                                                           f"• 0 - если не нужна.\n")

        need_comment_var = comment_in_report(need_comment)

        mnojitel_num += 1
        user_mnojitel_dict["mnojitel_" + str(mnojitel_num)] = [mnojitel, mnojitel_scores, need_comment_var]
        await client.send_message(user_id, f'Множитель "{mnojitel}" добавлен в шаблон.')
        once_mnoj_is_exist = True
        print(user_mnojitel_dict)

    @client.on_message(filters.text & filters.regex("Протестировать шаблон"))
    async def add_criterion(client, message):
        global criterion_num, mnojitel_num

        output_criterions = []
        output_mnojitels = []

        def random_hours_func():
            random_hours = random.randint(1, 10)
            return random_hours

        def random_mnojitel_get_or_not():
            rand_int = random.randint(1,2)
            if rand_int == 1:
                return "Получен", "не занимался", "Нет"
            else:
                return "Не получен", "занимался", "Да"

        # Количество критериев
        print(criterion_num)
        for crit_num in range(criterion_num):
            random_hours = random_hours_func()
            criterion = user_criterion_dict.get(f'criterion_{crit_num + 1}')
            if criterion:
                description, score_per_hour, comment_bool = criterion
                if comment_bool:
                    output_criterions.append(
                        f"• {description}:\n"
                        f"{random_hours} hours = {score_per_hour * random_hours} scores\n"
                        f"Комментарий: Сегодня я потратил на это {random_hours} hours.\n"
                    )
                else:
                    output_criterions.append(
                        f"• {description}:\n"
                        f"{random_hours} hours = {score_per_hour * random_hours} scores\n")

            else:
                pass

        # Количество множителей
        print(mnojitel_num)
        for mnoj_num in range(mnojitel_num):
            get_or_not, do_or_not, yes_or_no = random_mnojitel_get_or_not()
            mnojitel = user_mnojitel_dict.get(f'mnojitel_{mnoj_num + 1}')
            if mnojitel:
                description, scores, comment_bool = mnojitel
                if comment_bool:
                    output_mnojitels.append(
                        f"• {description}: {yes_or_no}\n"
                        f"Множитель x{scores}: {get_or_not}\n"
                        f"Комментарий: Сегодня я {do_or_not} этим.\n"
                    )
                else:
                    output_mnojitels.append(
                        f"• {description}: {yes_or_no}\n"
                        f"Множитель x{scores}: {get_or_not}\n"
                    )

            else:
                pass

        user_id = message.from_user.id

        # Соединяем все строки в одну с помощью join при условии наличия
        result_crits = "\n".join(output_criterions)

        if once_mnoj_is_exist:
            result_mnojs = "\n".join(output_mnojitels)
        else:
            result_mnojs = None

        if result_mnojs != None:
            await client.send_message(user_id, f"Отчет: {message.from_user.first_name}\n"
                                               f"........................\n"
                                               f"Критерии:\n"
                                               f"\n"
                                               f"{result_crits}\n"
                                               f"........................\n"
                                               f"Множители:\n"
                                               f"\n"
                                               f"{result_mnojs}\n"
                                               f"........................\n"
                                      )
        else:
            await client.send_message(user_id, f"Отчет: {message.from_user.first_name}\n"
                                               f"........................\n"
                                               f"Критерии:\n"
                                               f"\n"
                                               f"{result_crits}\n"
                                               f"........................\n"
                                      )




                                           # f"Сумма баллов за сегодня: {count_scores - ((float(answers['timeout_time']))) / 2} scores\n"
                                           # f"Общая сумма баллов: {float(answers['global_scores']) + count_scores - minus_5_scores_val(minus_5_scores_get_or_not(answers), answers) - (float(answers['timeout_time']) / 2)} scores")

        print(user_criterion_dict)

    @client.on_message(filters.text & filters.regex("Выйти"))
    async def quit_template(client, message):
        global user_criterion_dict
        user_criterion_dict = {}
        await message.reply_text("Выход из конструктора шаблонов.", reply_markup=keyboards.main_keyboard())

    async def ask_question(client, user_id, question):
        await client.send_message(user_id, question)
        user_states[user_id] = asyncio.Future()
        response = await user_states[user_id]
        return response

    @client.on_message(filters.private)
    async def receive_response(client, message):
        user_id = message.from_user.id
        if user_id in user_states:
            user_states[user_id].set_result(message.text)


