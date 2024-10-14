from aiogram.types import Message
from aiogram import F, Router


router_cmd_about = Router()

@router_cmd_about.message(F.text == "О системе мотивации")
async def cmd_about(message: Message):
    await message.answer('ХАю хай с вами Иван Гай')
