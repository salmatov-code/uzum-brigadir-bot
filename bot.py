from aiogram import Router
from aiogram.types import Message
from keyboards.inline import make_inline_markup
import re
import logging

router = Router()
logger = logging.getLogger("search")

PHONE_RE = re.compile(r"\+?\d{7,15}")
ID_RE = re.compile(r"^\d{3,}$")
BAG_RE = re.compile(r"^[A-Za-z0-9\-]{3,}$")


async def search_handler(message: Message, cache):
    text = message.text.strip()
    logger.info(f"Search by user {message.from_user.id}: {text}")

    # Определяем тип поиска
    if ID_RE.match(text):
        key = "id"
    elif PHONE_RE.search(text):
        key = "phone"
    else:
        key = "bag"

    item = cache.find(text, key=key)

    if not item:
        await message.answer("Ничего не найдено.")
        return

    card = (
        f"🆔 ID: {item.get('id', '')}\n"
        f"👤 {item.get('name', '')}\n"
        f"📞 {item.get('phone', '')}\n"
        f"🚗 {item.get('transport', '')}\n"
        f"🤝 {item.get('partner', '')}\n"
        f"🌍 {item.get('city', '')}\n"
        f"🎒 {item.get('bag', '')}\n"
        f"🟢 {item.get('status', '')}"
    )

    markup = make_inline_markup(item)
    await message.answer(card, reply_markup=markup)


def register_search_handlers(dp, cache):
    async def wrapped(message: Message):
        if not cache.is_allowed(message.from_user.id):
            await message.answer("Доступ запрещён.")
            logger.warning(f"Unauthorized access by {message.from_user.id}")
            return

        await search_handler(message, cache)

    router.message.register(wrapped)
    dp.include_router(router)
