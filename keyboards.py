from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

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

def main_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="О системе мотивации"), KeyboardButton(text="Использование системы на примере")],
            [KeyboardButton(text="Создать отчёт")],
            [KeyboardButton(text="Создать шаблон"), KeyboardButton(text="Просмотреть шаблоны")],
            [KeyboardButton(text="Получить ключ шаблона"), KeyboardButton(text="Создать шаблон по ключу")]
        ],
        resize_keyboard=True  # Уменьшение размера кнопок
    )
    return keyboard

def user_templates_keyboard(templates_list):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=templates_list
    )
    return keyboard

def cancel_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Отмена")]],
        resize_keyboard=True  # Уменьшение размера кнопок
    )
    return keyboard