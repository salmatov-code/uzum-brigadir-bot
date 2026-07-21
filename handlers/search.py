from aiogram import Router, F
from aiogram.types import Message
import re
import logging

from keyboards.inline import make_inline_markup

router = Router()
logger = logging.getLogger("search")

PHONE_RE = re.compile(r"\+?\d{7,15}")
NUMBER_RE = re.compile(r"^\d+$")

STATUS = {
    "active": "🟢 Active",
    "lost": "🟡 Lost",
    "blocked": "🔵 Blocked",
    "retired": "🔴 Retired",
}

TRANSPORT = {
    "foot": "🚶 Пешком",
    "bike": "🚲 Велосипед",
    "bicycle": "🚲 Велосипед",
    "scooter": "🛴 Самокат",
    "moped": "🛵 Мопед",
    "motorcycle": "🏍️ Мотоцикл",
    "car": "🚗 Автомобиль",
}


async def search_handler(message: Message, cache):
    text = message.text.strip()
    text_lower = text.lower()

    logger.info(f"Search by {message.from_user.id}: {text}")

    item = None

    if PHONE_RE.fullmatch(text.replace(" ", "")):
        item = cache.find(text, key="phone")

    elif text_lower.startswith("курьер "):
        item = cache.find(text[8:].strip(), key="id")

    elif text_lower.startswith("сумка "):
        item = cache.find(text[6:].strip(), key="bag")

    elif NUMBER_RE.fullmatch(text):
        item = cache.find(text, key="id")
        if item is None:
            item = cache.find(text, key="bag")

    else:
        item = cache.find(text, key="bag")

    if not item:
        await message.answer("❌ Ничего не найдено.")
        return

    status = STATUS.get(
        str(item.get("status", "")).lower(),
        item.get("status") or "Неизвестно"
    )

    phone = str(item.get("phone") or "").strip()
    if phone:
        if not phone.startswith("+"):
            phone = "+" + phone
    else:
        phone = "Нет"

    transport_key = str(item.get("transport") or "").lower()
    transport = TRANSPORT.get(
        transport_key,
        item.get("transport") or "Нет"
    )

    name = item.get("name") or "Нет"
    partner = item.get("partner") or "Нет"
    city = item.get("city") or "Нет"
    bag = item.get("bag") or "Нет"

    is_admin = cache.is_admin(message.from_user.id)

    card = f"""
<b>👤 Карточка курьера</b>

🆔 <b>ID:</b> {item.get("id")}
📊 <b>Статус:</b> {status}

👤 <b>{name}</b>
📞 {phone}

🚚 <b>Транспорт:</b> {transport}
🤝 <b>Партнёр:</b> {partner}
🌍 <b>Город:</b> {city}
🎒 <b>Сумка:</b> {bag}
"""

    await message.answer(
        card.strip(),
        parse_mode="HTML",
        reply_markup=make_inline_markup(item, is_admin=is_admin)
    )


def register_search_handlers(dp, cache):

    async def wrapped(message: Message):
        if not cache.is_allowed(message.from_user.id):
            await message.answer("⛔ Доступ запрещён, запроси у админа.")
            return

        await search_handler(message, cache)

    router.message.register(
        wrapped,
        F.text,
        ~F.text.startswith("/")
    )

    dp.include_router(router)
