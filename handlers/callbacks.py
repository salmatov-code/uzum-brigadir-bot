from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
import logging

router = Router()
logger = logging.getLogger("callbacks")


async def all_callbacks(
    query: CallbackQuery,
    sheets=None,
    cache=None,
    state: FSMContext = None,
):
    data = query.data or ""
    parts = data.split(":", 1)
    action = parts[0]
    key = parts[1] if len(parts) > 1 else ""

    # Просмотр сумки
    if action == "bag":
        await query.message.answer(f"Сумка: {key}")

    # Закрыть админ-панель
    elif action == "admin_close":
        await query.message.delete()

    # Список пользователей
    elif action == "admin_users":

        if not cache.is_admin(query.from_user.id):
            await query.answer("Нет доступа", show_alert=True)
            return

        users = await sheets.list_users()

        if not users:
            await query.message.answer("Пользователей не найдено.")
        else:
            text = "📋 <b>Список пользователей</b>\n\n"

            for user in users:
                text += (
                    f"👤 {user.get('Имя', '-')}\n"
                    f"🆔 {user.get('Telegram ID', '-')}\n"
                    f"🔑 {user.get('Роль', '-')}\n\n"
                )

            await query.message.answer(text)

    # Остальные callback'и обрабатываются другими роутерами
    else:
        return

    await query.answer()


def register_callback_handlers(dp, sheets, cache):

    async def _wrapped(query: CallbackQuery, state: FSMContext):

        try:
            if not cache.is_allowed(query.from_user.id):
                await query.message.answer("Доступ запрещён.")
                logger.warning(
                    f"Unauthorized callback attempt by {query.from_user.id}"
                )
                await query.answer()
                return

        except Exception:
            logger.exception("Error checking access")
            await query.message.answer(
                "Ошибка проверки доступа. Попробуйте позже."
            )
            await query.answer()
            return

        await all_callbacks(
            query=query,
            sheets=sheets,
            cache=cache,
            state=state,
        )

    router.callback_query.register(_wrapped)
    dp.include_router(router)
