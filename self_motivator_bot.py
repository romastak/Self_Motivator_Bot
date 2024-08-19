import logging
import asyncio

from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart # Команда /start
from aiogram.types import Message

from command_start import router_cmd_start
from command_about import router_cmd_about
from command_example import router_cmd_ex
from command_create_template import router_cmd_cr_templ


# Инициализация бота и диспетчера
bot = Bot(token="7266990703:AAE58wOTTLQsAU05jV0Exh8ODRz29ljqSMM")
dp = Dispatcher() # Это основной роутер, работа происходит через него, его задача обрабатывать updates

# Отправляет запросы на сервера телеграма, если ответы есть, сервер отдаст, если нет ответа, то метод будет ожидать ответа
async def main():
    dp.include_router(router_cmd_start)
    dp.include_router(router_cmd_about)
    dp.include_router(router_cmd_ex)
    dp.include_router(router_cmd_cr_templ)
    await dp.start_polling(bot)

# Запускаем бота
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Остановка бота")