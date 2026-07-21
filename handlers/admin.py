from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from keyboards.admin import admin_menu

router = Router()


def register_admin_handlers(dp, cache, sheets):

    @router.message(Command("admin"))
    async def admin(message: Message):
        print("ADMIN COMMAND RECEIVED")

        await message.answer(
            f"""
ID: {message.from_user.id}
Role: {cache.get_role(message.from_user.id)}
Is admin: {cache.is_admin(message.from_user.id)}
"""
        )

        if not cache.is_admin(message.from_user.id):
            await message.answer("❌ Нет доступа")
            return

        await message.answer(
            "⚙️ Панель администратора",
            reply_markup=admin_menu(),
        )

    dp.include_router(router)
