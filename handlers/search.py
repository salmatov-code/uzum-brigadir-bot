from aiogram import Router
from aiogram.types import Message
from keyboards.inline import make_inline_markup
import re
import logging

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
        item = cache.find(text[8:].strip(), key="id")

    # сумка 33677
    elif text_lower.startswith("сумка "):
        item = cache.find(text[6:].strip(), key="bag")

    # Просто число
    elif NUMBER_RE.fullmatch(text):
        item = cache.find(text, key="id")
        if item is None:
            item = cache.find(text, key="bag")

    else:
        item = cache.find(text, key="bag")

    if not item:
        await message.answer("❌ Ничего не найдено.")
        return

    # Статус
    status = STATUS.get(
        str(item.get("status", "")).lower(),
        item.get("status", "Неизвестно")
    )

    # Телефон
    phone = str(item.get("phone") or "").strip()
    if phone:
        if not phone.startswith("+"):
            phone = "+" + phone
    else:
        phone = "Нет"

    # Остальные поля
    name = item.get("name") or "Нет"
    transport = item.get("transport") or "Нет"
    partner = item.get("partner") or "Нет"
    city = item.get("city") or "Нет"
    bag = item.get("bag") or "Нет"

    # Пока заглушки (позже будут из cache/media)
    has_video = False
    has_act = False

    video = "✅" if has_video else "❌"
    act = "✅" if has_act else "❌"

    # Проверка роли
    is_admin = cache.is_admin(message.from_user.id)

    card = "\n".join([
        "👤 <b>Карточка курьера</b>",
        "",
        f"🆔 <b>{item.get('id')}</b> • {status}",
        "",
        f"👤 {name}",
        f"📞 {phone}",
        f"🛵 {transport}",
        f"🤝 {partner}",
        f"🌍 {city}",
        f"🎒 {bag}",
        "",
        "📂 <b>Материалы</b>",
        f"🎥 Видео {video}",
        f"📄 Акт {act}",
    ])

    await message.answer(
        card,
        parse_mode="HTML",
        reply_markup=make_inline_markup(item, is_admin=is_admin)
    )


def register_search_handlers(dp, cache):
    async def wrapped(message: Message):
        if not cache.is_allowed(message.from_user.id):
            await message.answer("⛔ Доступ запрещён.")
            return

        await search_handler(message, cache)

    router.message.register(wrapped)
    dp.include_router(router)
