from aiogram.types import Message
from aiogram import Router
from aiogram.filters import CommandStart # Команда /start
from assets.other_modules.keyboards import main_keyboard
from assets.db_modules.requests import add_tg_user, check_user_in_db_session

router_cmd_start = Router()


# Ожидание сообщения, в данном случае /start
@router_cmd_start.message(CommandStart())
async def cmd_start(message: Message):
    tg_id = message.from_user.id
    username = message.from_user.first_name

    user = await check_user_in_db_session(tg_id=tg_id)

    if not user:
        check = await add_tg_user(tg_id=tg_id, username=username)
        if check:
            print(f'DEBUG: SUCCESS! User "{username}" is created in db.')
        else:
            print(f'DEBUG: FAIL! User "{username}" is NOT created in db.')
    else:
        print(f'DEBUG: SUCCESS! User "{username}" is already exist.')

    await message.answer(
        f"Добро пожаловать, {username}!\n"
        f"Наша уникальная система мотивации предоставит вам возможность реализовать свои амбиции в полной мере.\n"
        f"Чтобы узнать подробнее, нажмите на кнопку <<О системе мотивации>>.",
        reply_markup=main_keyboard()
    )