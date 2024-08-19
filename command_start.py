from aiogram.types import Message
from aiogram import Router
from aiogram.filters import CommandStart # Команда /start
from keyboards import main_keyboard


router_cmd_start = Router()

# Ожидание сообщения, в данном случае /start
@router_cmd_start.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        f"Добро пожаловать, {message.from_user.first_name}!\n"
        f"Наша уникальная система мотивации предоставит вам возможность реализовать свои амбиции в полной мере.\n"
        f"Чтобы узнать подробнее, нажмите на кнопку <<О системе мотивации>>.",
        reply_markup=main_keyboard()
    )