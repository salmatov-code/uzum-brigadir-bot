from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def make_inline_markup(item: dict, is_admin: bool = False) -> InlineKeyboardMarkup:
    keyboard = []

    if is_admin:
        keyboard.append([
            InlineKeyboardButton(
                text="⚙️ Управление",
                callback_data=f"manage:{item['id']}"
            )
        ])

    return InlineKeyboardMarkup(
        inline_keyboard=keyboard
    )
