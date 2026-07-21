from aiogram import Router, types
from aiogram.filters import CommandStart
from services.sheets import SheetsService

router = Router()

@router.message(CommandStart())
async def start_handler(message: types.Message, sheets: SheetsService | None = None):
    # simple welcome
    await message.answer("Привет! Отправь ID курьера, телефон или номер сумки для поиска.")

def register_start_handlers(dp, sheets):
    dp.include_router(router)
