# Uzum Brigadir Bot

Этот проект — Telegram-бот на aiogram 3 для поиска данных курьеров в Google Sheets.

Подготовка

1. Создайте Service Account в Google Cloud и скачайте JSON-ключ.
2. Добавьте ключ в переменную окружения GOOGLE_SERVICE_ACCOUNT_JSON (как строку JSON) или сохраните в .env при локальной разработке.
3. В Render добавьте BOT_TOKEN и GOOGLE_SERVICE_ACCOUNT_JSON в секреты окружения.

Запуск локально

pip install -r requirements.txt
cp .env.example .env
# заполните .env
python bot.py

Структура

- handlers/ — обработчики команд и сообщений
- services/ — интеграция с Google Sheets, кеш
- keyboards/ — inline-кнопки
- data/ — логи

Google Sheets

Ожидаемые листы:
- "Доступ" — список разрешённых Telegram ID (в колонке A)
- "Курьеры" — основной лист с информацией о курьерах
- "Видео" — ссылки на видео/документы по курьеру или сумке

Кэш обновляется каждые 5 минут; во время поиска бот обращается к кэшу.
