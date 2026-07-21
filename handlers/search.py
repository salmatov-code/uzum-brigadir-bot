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
        value = text[8:].strip()
        item = cache.find(value, key="id")

    # сумка 33677
    elif text_lower.startswith("сумка "):
        value = text[6:].strip()
        item = cache.find(value, key="bag")

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

    # Красивый статус
    status = STATUS.get(
        str(item["status"]).lower(),
        item["status"]
    )

    # Добавляем "+" к телефону
    phone = str(item["phone"]).strip()
    if phone and not phone.startswith("+"):
        phone = "+" + phone

    # Пока заглушки (потом будут браться из таблицы Видео)
    has_video = False
    has_act = False

    video = "✅" if has_video else "❌"
    act = "✅" if has_act else "❌"

    card = (
        "👤 <b>Карточка курьера</b>\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🆔 <b>ID:</b> {item['id']}    {status}\n\n"
        f"👤 {item['name']}\n"
        f"📞 {phone}\n\n"
        f"🚗 {item['transport']}\n"
        f"🤝 {item['partner']}\n"
        f"🌍 {item['city']}\n"
        f"🎒 {item['bag']}\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "📂 <b>Материалы</b>\n\n"
        f"🎥 Видео {video}    📄 Акт {act}"
    )

    await message.answer(
        card,
        parse_mode="HTML",
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
