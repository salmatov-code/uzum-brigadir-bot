from aiogram import Router
from aiogram.types import CallbackQuery
import logging

router = Router()
logger = logging.getLogger("callbacks")

async def all_callbacks(query: CallbackQuery, sheets=None, cache=None):
    data = query.data or ''
    # data format: action:identifier
    parts = data.split(':', 1)
    action = parts[0]
    key = parts[1] if len(parts) > 1 else ''

    if action == 'bag':
        await query.message.answer(f"Сумка: {key}")
    elif action in ('video','doc'):
        # ensure sheets service is available
        if sheets is None:
            await query.message.answer("Сервис недоступен. Попробуйте позже.")
            await query.answer()
            return
        # lookup in sheets
        res = await sheets.find_video(key)
        if res:
            await query.message.answer(res)
        else:
            await query.message.answer("Материалы не найдены.")
    await query.answer()


def register_callback_handlers(dp, sheets, cache):
    # Wrap callback handler to perform access check and inject sheets/cache explicitly.
    async def _wrapped(query: CallbackQuery):
        try:
            if not cache.is_allowed(query.from_user.id):
                await query.message.answer("Доступ запрещён.")
                logger.warning(f"Unauthorized callback attempt by {query.from_user.id}")
                await query.answer()
                return
        except Exception as e:
            logger.exception("Error checking access in callback")
            # Inform user but do not raise
            await query.message.answer("Ошибка проверки доступа. Попробуйте позже.")
            await query.answer()
            return

        await all_callbacks(query, sheets=sheets, cache=cache)

    router.callback_query.register(_wrapped)
    dp.include_router(router)
