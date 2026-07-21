from aiogram import Router, types
from aiogram.filters import CommandStart
import logging

router = Router()
logger = logging.getLogger("start")

@router.message(CommandStart())
async def start_handler(message: types.Message, cache=None):
    # This function will not be registered directly; we use a wrapper to inject cache and check access.
    await message.answer("Привет! Отправь ID курьера, телефон или номер сумки для поиска.")


def register_start_handlers(dp, cache):
    async def _wrapped(message: types.Message):
        try:
            if not cache.is_allowed(message.from_user.id):
                await message.answer("Доступ запрещён.")
                logger.warning(f"Unauthorized /start attempt by {message.from_user.id}")
                return
        except Exception as e:
            # If cache or access check fails, don't crash — inform user and log.
            logger.exception("Error checking access in /start")
            await message.answer("Ошибка проверки доступа. Попробуйте позже.")
            return

        await start_handler(message, cache=cache)

    router.message.register(_wrapped, CommandStart())
    dp.include_router(router)
