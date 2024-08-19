from aiogram.types import Message
from aiogram import F, Router


router_cmd_about = Router()

@router_cmd_about.message(F.text == "О системе мотивации") # Получена команда /help
async def cmd_about(message: Message):
    await message.answer(
        "Наша система мотивации разработана для того, чтобы помочь вам достигать своих целей. "
        "Используйте наш бот для создания отчетов и шаблонов,"
        "чтобы отслеживать ваш прогресс и оставаться на верном пути."
    )