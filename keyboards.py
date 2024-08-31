from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardMarkup, ReplyKeyboardBuilder, InlineKeyboardBuilder

def main_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="О системе мотивации"), KeyboardButton(text="Использование системы на примере")],
            [KeyboardButton(text="Создать отчёт")],
            [KeyboardButton(text="Создать шаблон"), KeyboardButton(text="Мои шаблоны")],
            [KeyboardButton(text="Получить ключ шаблона"), KeyboardButton(text="Создать шаблон по ключу")],
            [KeyboardButton(text="Мотивирующая цитата")]
        ],
        resize_keyboard=True  # Уменьшение размера кнопок
    )
    return keyboard

def create_template_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="+ Добавить критерий"), KeyboardButton(text="- Удалить критерий")],
            [KeyboardButton(text="+ Добавить множитель"), KeyboardButton(text="- Удалить множитель")],
            [KeyboardButton(text="+ Добавить условие"), KeyboardButton(text="- Удалить условие")],
            [KeyboardButton(text="Протестировать шаблон")],
            [KeyboardButton(text="Сохранить шаблон")],
            [KeyboardButton(text="Выйти без сохранения")],
        ],
        resize_keyboard=True  # Уменьшение размера кнопок
    )
    return keyboard

def delete_crit_keyboard(crits_list):
    keyboard = InlineKeyboardBuilder()
    n = 0
    for el in crits_list:
        keyboard.add(InlineKeyboardButton(text=el, callback_data=str("crit_num_" + str(n))))
        n += 1
    return keyboard.adjust(1).as_markup() # Сколько будет кнопок в ряду

def delete_mnoj_keyboard(mnoj_list):
    keyboard = InlineKeyboardBuilder()
    n = 0
    for el in mnoj_list:
        keyboard.add(InlineKeyboardButton(text=el, callback_data=str("mnoj_num_" + str(n))))
        n += 1
    return keyboard.adjust(1).as_markup()

def get_user_templ_keyboard(templ_list):
    keyboard = InlineKeyboardBuilder()
    n = 0
    for el in templ_list:
        keyboard.add(InlineKeyboardButton(text=el, callback_data=str("templ_num_" + str(n))))
        n += 1
    return keyboard.adjust(1).as_markup()

def get_templ_key_keyboard(templ_list):
    keyboard = InlineKeyboardBuilder()
    n = 0
    for el in templ_list:
        keyboard.add(InlineKeyboardButton(text=el, callback_data=str("templ_key_" + str(n))))
        n += 1
    return keyboard.adjust(1).as_markup()

def cancel_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Отмена")]
        ],
        resize_keyboard=True  # Уменьшение размера кнопок
    )
    return keyboard

# Инлайн-клавиатура для действий над выбранным шаблоном
def templ_actions_keyboard():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Отредактировать шаблон", callback_data="edit_templ")],
            [InlineKeyboardButton(text="Изменить глобальные очки", callback_data="edit_templ")],
            [InlineKeyboardButton(text="Обнулить глобальные очки", callback_data="edit_templ")],
            [InlineKeyboardButton(text="Удалить шаблон", callback_data="delete_templ")]
        ]
    )
    return keyboard