from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def admin_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="➕ Добавить пользователя",
                    callback_data="admin_add_user"
                )
            ],
            [
                InlineKeyboardButton(
                    text="✏️ Изменить роль",
                    callback_data="admin_change_role"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🚫 Удалить доступ",
                    callback_data="admin_remove_user"
                )
            ],
            [
                InlineKeyboardButton(
                    text="📋 Список пользователей",
                    callback_data="admin_users"
                )
            ],
            [
                InlineKeyboardButton(
                    text="❌ Закрыть",
                    callback_data="admin_close"
                )
            ]
        ]
    )


def roles_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="👤 Moderator",
                    callback_data="role_moderator"
                )
            ],
            [
                InlineKeyboardButton(
                    text="👑 Admin",
                    callback_data="role_admin"
                )
            ],
            [
                InlineKeyboardButton(
                    text="❌ Отмена",
                    callback_data="admin_cancel"
                )
            ]
        ]
    )


def cancel_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="❌ Отмена",
                    callback_data="admin_cancel"
                )
            ]
        ]
    )

