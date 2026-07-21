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
        str(item.get("status", "")).lower(),
        item.get("status", "")
    )

    # Добавляем "+" к телефону
    phone = str(item.get("phone", "")).strip()
    if phone and not phone.startswith("+"):
        phone = "+" + phone

    # Пока заглушки (потом будут браться из таблицы Видео)
    has_video = False
    has_act = False

    video = "✅" if has_video else "❌"
    act = "✅" if has_act else "❌"

    # detect admin status for current user — minimal heuristic based on cache._access contents
    is_admin = False
    try:
        uid = str(message.from_user.id)
        access_list = getattr(cache, "_access", [])
        for row in access_list:
            if isinstance(row, dict):
                # check if this row contains the user id (as key or value)
                contains_id = any(str(k).strip() == uid or str(v).strip() == uid for k, v in row.items())
                if not contains_id:
                    continue
                # if the row contains admin-like marker in any value -> admin
                for k, v in row.items():
                    try:
                        if isinstance(v, str) and v.strip().lower() in ("admin", "админ", "administrator"):
                            is_admin = True
                            break
                    except Exception:
                        continue
                if is_admin:
                    break
            else:
                # row is primitive, unlikely to contain role info
                continue
    except Exception:
        is_admin = False

    card = (
        "👤 <b>Карточка курьера</b>\n\n"
        f"🆔 <b>{item.get('id')}</b> • {status}\n\n"
        f"👤 {item.get('name')}\n"
        f"📞 {phone}\n"
        f"🚗 {item.get('transport')}\n"
        f"🤝 {item.get('partner')}\n"
        f"🌍 {item.get('city')}\n"
        f"🎒 {item.get('bag')}\n\n"
        "📂 <b>Материалы</b>\n"
        f"🎥 Видео {video}\n"
        f"📄 Акт {act}"
    )

    await message.answer(
        card,
        parse_mode="HTML",
        reply_markup=make_inline_markup(item, is_admin=is_admin)
    )


def register_search_handlers(dp, cache):
    async def wrapped(message: Message):
        if not cache.is_allowed(message.from_user.id):
            await message.answer("Доступ запрещён.")
            return

        await search_handler(message, cache)

    router.message.register(wrapped)
    dp.include_router(router)
