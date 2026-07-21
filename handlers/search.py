from aiogram import Router
from aiogram.types import Message
from keyboards.inline import make_inline_markup
import re
import logging

router = Router()
logger = logging.getLogger("search")

PHONE_RE = re.compile(r"\+?\d{7,15}")
NUMBER_RE = re.compile(r"^\d+$")


async def search_handler(message: Message, cache):
    text = message.text.strip()
    text_lower = text.lower()

    logger.info(f"Search by user {message.from_user.id}: {text}")

    item = None

    # Поиск по телефону
    if PHONE_RE.fullmatch(text.replace(" ", "")):
        item = cache.find(text, key="phone")

    # курьер 91087
    elif text_lower.startswith("курьер "):
        value = text[8:].strip()
        item = cache.find(value, key="id")

    # сумка 33677
    elif text_lower.startswith("сумка "):
        value = text[6:].strip()
        item = cache.find(value, key="bag")

    # Просто число
    elif NUMBER_RE.fullmatch(text):
        # Сначала пробуем найти courier_id
        item = cache.find(text, key="id")

        # Если не нашли — ищем по сумке
        if item is None:
            item = cache.find(text, key="bag")

    else:
        # Любой другой текст считаем номером сумки
        item = cache.find(text, key="bag")

    if not item:
        await message.answer("Ничего не найдено.")
        return

    card = (
        f"🆔 ID: {item['id']}\n"
        f"👤 {item['name']}\n"
        f"📞 {item['phone']}\n"
        f"🚗 {item['transport']}\n"
        f"🤝 {item['partner']}\n"
        f"🌍 {item['city']}\n"
        f"🎒 {item['bag']}\n"
        f"🟢 {item['status']}"
    )

    await message.answer(
        card,
        reply_markup=make_inline_markup(item)
    )


def register_search_handlers(dp, cache):
    async def wrapped(message: Message):
        if not cache.is_allowed(message.from_user.id):
            await message.answer("Доступ запрещён.")
            return

        await search_handler(message, cache)

    router.message.register(wrapped)
    dp.include_router(router)
