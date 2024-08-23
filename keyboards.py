from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

def main_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="О системе мотивации"), KeyboardButton(text="Использование системы на примере")],
            [KeyboardButton(text="Создать отчёт")],
            [KeyboardButton(text="Создать шаблон"), KeyboardButton(text="Просмотреть шаблоны")],
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

def cancel_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Отмена")]],
        resize_keyboard=True  # Уменьшение размера кнопок
    )
    return keyboard