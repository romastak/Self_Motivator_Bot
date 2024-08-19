from aiogram.types import Message
from aiogram import F, Router


router_cmd_ex = Router()

@router_cmd_ex.message(F.text == "Использование системы на примере") # Получена команда /help
async def cmd_ex(message: Message):
    await message.answer(
        "Здесь будет пример использования."
    )