from aiogram import Bot, Dispatcher
from threading import Thread
import asyncio
import logging

from keep_alive import run
from config import settings

from services.sheets import SheetsService
from services.cache import Cache

from handlers.start import register_start_handlers
from handlers.search import register_search_handlers
from handlers.callbacks import register_callback_handlers
from handlers.admin import register_admin_handlers
from handlers.admin_fsm import register_admin_fsm

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    bot = Bot(token=settings.BOT_TOKEN)
    dp = Dispatcher()

    # Google Sheets
    sheets = SheetsService()

    # Cache
    cache = Cache(sheets)

    # Запускаем обновление кэша
    asyncio.create_task(cache.start())

    # Регистрация обработчиков
    register_start_handlers(dp, cache, sheets)
    register_search_handlers(dp, cache)
    register_callback_handlers(dp, sheets, cache)
    register_admin_handlers(dp, cache, sheets)
    register_admin_handlers(dp, cache, sheets)
    register_admin_fsm(dp, sheets, cache)
    register_callback_handlers(dp, sheets, cache)

    # Keep Alive (Render)
    Thread(target=run, daemon=True).start()

    logger.info("Bot started successfully")

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
