from aiogram import Router, types
from aiogram.filters import CommandStart, Command
import logging
import time
from services.sheets import SheetsService

router = Router()
logger = logging.getLogger("start")

@router.message(CommandStart())
async def start_handler(message: types.Message, cache=None):
    # This function will not be registered directly; we use a wrapper to inject cache and check access.
    await message.answer("Привет! Отправь ID курьера, телефон или номер сумки для поиска.")


async def _ping_handler(message: types.Message, cache=None, sheets: SheetsService | None = None):
    """Perform a health check of Google Sheets and return a multi-line status."""
    start = time.perf_counter()

    # Basic Google Sheets availability
    if sheets is None:
        await message.answer("🟢 Google Sheets\n\n❌ Подключение\n\nСервис недоступен. Попробуйте позже.")
        return

    status = await sheets.check_health()

    lines = []
    lines.append("🟢 Google Sheets")
    lines.append("")
    lines.append(f"{ '✅' if status.get('connected') else '❌' } Подключение")
    lines.append(f"{ '✅' if status.get('couriers') else '❌' } Лист \"Курьеры\"")
    lines.append(f"{ '✅' if status.get('access') else '❌' } Лист \"Доступ\"")
    lines.append(f"{ '✅' if status.get('read') else '❌' } Чтение")
    lines.append(f"{ '✅' if status.get('write') else '❌' } Запись")

    elapsed = int((time.perf_counter() - start) * 1000)
    lines.append("")
    lines.append(f"Время ответа: {elapsed} ms")

    await message.answer("\n".join(lines))


def register_start_handlers(dp, cache, sheets):
    async def _wrapped_start(message: types.Message):
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

    async def _wrapped_ping(message: types.Message):
        try:
            if not cache.is_allowed(message.from_user.id):
                await message.answer("Доступ запрещён.")
                logger.warning(f"Unauthorized /ping attempt by {message.from_user.id}")
                return
        except Exception:
            logger.exception("Error checking access in /ping")
            await message.answer("Ошибка проверки доступа. Попробуйте позже.")
            return

        await _ping_handler(message, cache=cache, sheets=sheets)

    router.message.register(_wrapped_start, CommandStart())
    router.message.register(_wrapped_ping, Command("ping"))
    dp.include_router(router)
