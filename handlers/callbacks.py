from aiogram import Router
from aiogram.types import CallbackQuery
import logging

router = Router()
logger = logging.getLogger("callbacks")

@router.callback_query()
async def all_callbacks(query: CallbackQuery, sheets=None, cache=None):
    data = query.data or ''
    # data format: action:identifier
    parts = data.split(':', 1)
    action = parts[0]
    key = parts[1] if len(parts) > 1 else ''

    if action == 'bag':
        await query.message.answer(f"Сумка: {key}")
    elif action in ('video','doc'):
        # lookup in sheets
        res = await sheets.find_video(key)
        if res:
            await query.message.answer(res)
        else:
            await query.message.answer("Материалы не найдены.")
    await query.answer()

def register_callback_handlers(dp, sheets, cache):
    router.callback_query.register(all_callbacks)
    dp.include_router(router)
