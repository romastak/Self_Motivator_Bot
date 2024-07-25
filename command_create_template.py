import tgcrypto
from pyrogram import Client, filters
from pyrogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
import sqlite3
import asyncio
import keyboards

user_states = {}  # Хранение состояния пользователей
user_criterion_dict = {}
criterion_num = 0

def add_template(user_id, question, response_type):
    conn = sqlite3.connect('reports.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO templates (user_id, question, response_type) VALUES (?, ?, ?)', (user_id, question, response_type))
    conn.commit()
    conn.close()

def create_template_main(client, message, add_template):
    global user_states, criterion_num, user_criterion_dict # Доступ к глобальному состоянию пользователей

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

    @client.on_message(filters.text & filters.regex("Добавить критерий"))
    async def add_criterion(client, message):
        global criterion_num
        user_id = message.from_user.id
        criterion = await ask_question(client, user_id, "Введите новый критерий (Например: Изучение Python):")
        criterion_scores = await ask_question(client, user_id, "Обозначьте количество получаемых баллов за 1 час деятельности по этому критерию (Например: 1.5)")
        need_comment = await ask_question(client, user_id, f"Нужна ли будет возможность комментирования критерия?\n"
                                                           f"Отправьте 1 - если нужна\n"
                                                           f"0 - если не нужна.\n")

        if int(need_comment):
            need_comment = True
        else:
            need_comment = False

        criterion_num += 1
        user_criterion_dict["criterion_" + str(criterion_num)] = [criterion, criterion_scores, need_comment]
        await client.send_message(user_id, f'Критерий "{criterion}" добавлен в шаблон.')
        print(user_criterion_dict)

    @client.on_message(filters.text & filters.regex("Протестировать шаблон"))
    async def add_criterion(client, message):
        global criterion_num
        output_criterions = []

        # Количество критериев
        print(criterion_num)
        for crit_num in range(criterion_num):
            output_criterions.append(f"{user_criterion_dict[f'criterion_{crit_num + 1}']}: 3 hours ="
                                    f" {user_criterion_dict[f'criterion_{crit_num + 1}']} scores\n")

        user_id = message.from_user.id
        await client.send_message(user_id, f"Отчет: {message.from_user.first_name}\n"
                                           f"........................\n"
                                           f"{output for output in output_criterions}")
                                           # f"Сумма баллов за сегодня: {count_scores - ((float(answers['timeout_time']))) / 2} scores\n"
                                           # f"Общая сумма баллов: {float(answers['global_scores']) + count_scores - minus_5_scores_val(minus_5_scores_get_or_not(answers), answers) - (float(answers['timeout_time']) / 2)} scores")

        await client.send_message(user_id, f'Внешний вид отчета таков, долбоеб ебаный, иди нахуй!')
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


