from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from keyboards.admin import admin_menu

router = Router()


async def admin_panel(message: Message, cache):
    if not cache.is_admin(message.from_user.id):
        await message.answer("❌ У вас нет доступа к панели администратора.")
        return

    await message.answer(
        "⚙️ <b>Панель администратора</b>",
        reply_markup=admin_menu(),
    )


def register_admin_handlers(dp, cache, sheets):
    async def wrapper(message: Message):
        await admin_panel(message, cache)

    router.message.register(wrapper, Command("admin"))

    dp.include_router(router)
