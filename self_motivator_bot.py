import logging
import asyncio

from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart # Команда /start
from aiogram.types import Message

from assets.other_modules.keyboards import main_keyboard
from assets.command_modules.command_start import router_cmd_start
from assets.command_modules.command_about import router_cmd_about
from assets.command_modules.command_example import router_cmd_ex
from assets.command_modules.command_create_template import router_cmd_cr_templ, router_cancel, router_cmd_save_templ, router_cancel, router_cmd_delete_crit, router_delete_crit_el, router_cmd_delete_mnoj, router_delete_mnoj_el
from assets.command_modules.command_get_quote import router_get_quote
from assets.command_modules.command_get_templates import router_cmd_get_user_templ
from assets.command_modules.command_get_key import router_cmd_get_key
from assets.command_modules.command_created_by_key import router_cmd_cr_by_key
from assets.db_modules.requests import get_all_telegram_ids


# Инициализация бота и диспетчера
bot = Bot(token="7266990703:AAE58wOTTLQsAU05jV0Exh8ODRz29ljqSMM")
dp = Dispatcher() # Это основной роутер, работа происходит через него, его задача обрабатывать updates

# Отправляет запросы на сервера телеграма, если ответы есть, сервер отдаст, если нет ответа, то метод будет ожидать ответа
async def main():
    dp.include_router(router_cmd_start)
    dp.include_router(router_cmd_about)
    dp.include_router(router_cmd_ex)
    dp.include_router(router_cmd_cr_templ)
    dp.include_router(router_cmd_save_templ)
    dp.include_router(router_cancel)
    dp.include_router(router_cmd_delete_crit)
    dp.include_router(router_get_quote)
    dp.include_router(router_delete_crit_el)
    dp.include_router(router_cmd_delete_mnoj)
    dp.include_router(router_delete_mnoj_el)
    dp.include_router(router_cmd_get_user_templ)
    dp.include_router(router_cmd_get_key)
    dp.include_router(router_cmd_cr_by_key)
    tg_ids = await get_all_telegram_ids()

    for id in tg_ids: # Отправляем всем main_keyboard при запуске бота
        await bot.send_message(chat_id=id, text='Бот снова работает', reply_markup=main_keyboard())

    await dp.start_polling(bot)

# Запускаем бота
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Остановка бота")