from datetime import datetime

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message

from keyboards.admin import roles_keyboard

router = Router()


class AdminFSM(StatesGroup):
    waiting_add_id = State()
    waiting_role = State()

    waiting_edit_id = State()

    waiting_remove_id = State()


def register_admin_fsm(dp, sheets, cache):
        # ---------- ЗАПУСК FSM ----------

    @router.callback_query(F.data == "admin_add_user")
    async def start_add(query, state: FSMContext):

        await state.clear()
        await state.set_state(AdminFSM.waiting_add_id)

        await query.message.answer(
            "Введите Telegram ID нового пользователя:"
        )

        await query.answer()

    @router.callback_query(F.data == "admin_change_role")
    async def start_edit(query, state: FSMContext):

        await state.clear()
        await state.set_state(AdminFSM.waiting_edit_id)

        await query.message.answer(
            "Введите Telegram ID пользователя:"
        )

        await query.answer()

    @router.callback_query(F.data == "admin_remove_user")
    async def start_remove(query, state: FSMContext):

        await state.clear()
        await state.set_state(AdminFSM.waiting_remove_id)

        await query.message.answer(
            "Введите Telegram ID пользователя для удаления:"
        )

        await query.answer()
    # ---------- ДОБАВЛЕНИЕ ----------

    @router.message(AdminFSM.waiting_add_id)
    async def add_id(message: Message, state: FSMContext):

        if not message.text.isdigit():
            await message.answer("Введите корректный Telegram ID.")
            return

        tg_id = int(message.text)

        if cache.is_allowed(tg_id):
            await message.answer("❌ Пользователь уже существует.")
            await state.clear()
            return

        await state.update_data(tg_id=tg_id)

        await message.answer(
            "Выберите роль:",
            reply_markup=roles_keyboard()
        )

        await state.set_state(AdminFSM.waiting_role)

    # ---------- ИЗМЕНЕНИЕ ----------

    @router.message(AdminFSM.waiting_edit_id)
    async def edit_role(message: Message, state: FSMContext):

        if not message.text.isdigit():
            await message.answer("Введите Telegram ID.")
            return

        tg_id = int(message.text)

        if not cache.is_allowed(tg_id):
            await message.answer("❌ Пользователь не найден.")
            await state.clear()
            return

        await state.update_data(
            tg_id=tg_id,
            edit=True,
        )

        await message.answer(
            "Выберите новую роль:",
            reply_markup=roles_keyboard(),
        )

        await state.set_state(AdminFSM.waiting_role)

    # ---------- УДАЛЕНИЕ ----------

    @router.message(AdminFSM.waiting_remove_id)
    async def remove_user(message: Message, state: FSMContext):

        if not message.text.isdigit():
            await message.answer("Введите Telegram ID.")
            return

        tg_id = int(message.text)

        if tg_id == message.from_user.id:
            await message.answer("❌ Нельзя удалить самого себя.")
            await state.clear()
            return

        await sheets.remove_user(tg_id)

        cache.remove_access(tg_id)

        await message.answer("✅ Пользователь удалён.")

        await state.clear()

    # ---------- ВЫБОР РОЛИ ----------

    @router.callback_query(
        F.data.in_(["role_admin", "role_moderator"])
    )
    async def choose_role(query, state: FSMContext):

        data = await state.get_data()

        tg_id = data["tg_id"]

        role = (
            "admin"
            if query.data == "role_admin"
            else "moderator"
        )

        # изменение роли
        if data.get("edit"):

            await sheets.update_role(
                tg_id,
                role,
            )

            cache.update_access(
                tg_id,
                role,
            )

            await query.message.answer(
                "✅ Роль изменена."
            )

        else:

            await sheets.add_user(
                telegram_id=tg_id,
                name="",
                role=role,
                added_by=str(query.from_user.id),
                date=datetime.now().strftime("%d.%m.%Y"),
            )

            cache.add_access(
                tg_id,
                role,
            )

            await query.message.answer(
                "✅ Пользователь добавлен."
            )

        await state.clear()

        await query.answer()

    dp.include_router(router)
