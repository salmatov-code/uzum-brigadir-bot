from aiogram import Router
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from states.upload import UploadStates
import logging

router = Router()
logger = logging.getLogger("callbacks")


async def all_callbacks(query: CallbackQuery, sheets=None, cache=None, state: FSMContext = None):
    data = query.data or ''
    # data format: action:identifier
    parts = data.split(':', 1)
    action = parts[0]
    key = parts[1] if len(parts) > 1 else ''

    if action == 'bag':
        await query.message.answer(f"Сумка: {key}")

    elif action in ('video', 'doc'):
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

    elif action == 'manage':
        # present management menu (admins only)
        try:
            if not cache.is_admin(query.from_user.id):
                await query.answer("Только для администраторов.", show_alert=True)
                return
        except Exception:
            await query.answer("Ошибка проверки прав.", show_alert=True)
            return

        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⬆️ Загрузить видео", callback_data=f"upload_video:{key}")],
            [InlineKeyboardButton(text="⬆️ Загрузить акт", callback_data=f"upload_act:{key}")]
        ])
        await query.message.answer("⚙️ Управление", reply_markup=kb)

    elif action in ("upload_video", "upload_act"):
        # admin-only: enter FSM to accept file
        try:
            if not cache.is_admin(query.from_user.id):
                await query.answer("Только для администраторов.", show_alert=True)
                return
        except Exception:
            await query.answer("Ошибка проверки прав.", show_alert=True)
            return

        if state is None:
            await query.answer()
            return

        if action == "upload_video":
            await query.message.answer("Отправьте, пожалуйста, видео (файл) для загрузки в архивную группу.")
            await state.update_data(target_bag=key)
            await state.set_state(UploadStates.waiting_for_video)
            await query.answer()
            return

        if action == "upload_act":
            await query.message.answer("Отправьте, пожалуйста, акт (файл) для загрузки в архивную группу.")
            await state.update_data(target_bag=key)
            await state.set_state(UploadStates.waiting_for_act)
            await query.answer()
            return

    await query.answer()


def register_callback_handlers(dp, sheets, cache):
    # Wrap callback handler to perform access check and inject sheets/cache explicitly.
    async def _wrapped(query: CallbackQuery, state: FSMContext):
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

        await all_callbacks(query, sheets=sheets, cache=cache, state=state)

    router.callback_query.register(_wrapped)
    dp.include_router(router)
