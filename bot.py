from aiogram import Bot, Dispatcher
from threading import Thread
from keep_alive import run
import asyncio
import logging
from config import settings
from services.sheets import SheetsService
from services.cache import Cache
from handlers.start import register_start_handlers
from handlers.search import register_search_handlers
from handlers.callbacks import register_callback_handlers

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    bot = Bot(token=settings.BOT_TOKEN)
    dp = Dispatcher()

    sheets = SheetsService()
    cache = Cache(sheets)

    asyncio.create_task(cache.start())

    register_start_handlers(dp, cache)
    register_search_handlers(dp, cache)
    register_callback_handlers(dp, sheets, cache)
    Thread(target=run, daemon=True).start()
    logger.info("Bot started")

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
