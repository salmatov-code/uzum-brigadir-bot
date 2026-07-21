from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def make_inline_markup(item: dict) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎒 Сумка", callback_data=f"bag:{item.get('bag','')}")],
        [InlineKeyboardButton(text="🎥 Видео", callback_data=f"video:{item.get('id','')}")],
        [InlineKeyboardButton(text="📄 Документ", callback_data=f"doc:{item.get('id','')}")]
    ])
    return kb
