import asyncio
import random
import aiohttp
from aiogram.types import Message
from aiogram.filters import Command
from aiogram import F, Router
from aiogram.fsm.state import StatesGroup, State # Классы состояний
from aiogram.fsm.context import FSMContext # Инструмент управления состояниями
from assets.db_modules.requests import save_user_template
from assets.other_modules.keyboards import main_keyboard, create_template_keyboard, cancel_keyboard, delete_crit_keyboard


router_get_quote = Router()

async def get_random_quote():
    url = "http://api.forismatic.com/api/1.0/"
    params = {
        "method": "getQuote",
        "format": "json",
        "lang": "ru"
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as response:
            data = await response.json()
            return data.get("quoteText"), data.get("quoteAuthor")

@router_get_quote.message(F.text == "Мотивирующая цитата")
async def add_crit_one(message: Message, state: FSMContext):

    await state.clear()

    quote = await get_random_quote()
    clear_quote = quote[0]
    clear_author = quote[1]
    if not clear_author:
        clear_author = "Автор неизвестен"
    print(quote)
    await message.answer(f'{clear_quote}\n'
                   f'\n'
                   f'{clear_author}')
