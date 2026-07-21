from services.sheets import SheetsService
import asyncio
from typing import Dict, Any, List, Optional


class Cache:
    def __init__(self, sheets: SheetsService, refresh_interval: int = 300):
        self.sheets = sheets
        self.refresh_interval = refresh_interval
        self._data = []
        self._videos = []
        self._access = {}
        self._lock = asyncio.Lock()

    async def start(self):
        await self.refresh()
        while True:
            await asyncio.sleep(self.refresh_interval)
            await self.refresh()

    async def refresh(self):
        async with self._lock:
            access = await self.sheets.get_access_list()

            self._access = {}

            for row in access:
                tg_id = str(row.get("Telegram ID", "")).strip()
                role = str(row.get("Роль", "user")).strip().lower()

                if tg_id:
                    self._access[tg_id] = role

            self._data = await self.sheets.get_couriers()
            self._videos = await self.sheets.get_videos()

            print("ACCESS:", self._access)

    def get_role(self, tg_id: int):
        return self._access.get(str(tg_id))

    def is_allowed(self, tg_id: int):
        return str(tg_id) in self._access

    def is_admin(self, tg_id: int):
        return self._access.get(str(tg_id)) == "admin"

    def get_all(self):
        return list(self._data)

    def find(self, query: str, key: Optional[str] = None):
        q = query.strip().lower()

        for r in self._data:
            if key == "id" and str(r.get("courier_id", "")).strip().lower() == q:
                return self._normalize(r)

            if key == "phone" and q in str(r.get("Номер телефона", "")).lower():
                return self._normalize(r)

            if key == "bag" and q in str(r.get("Сумка", "")).lower():
                return self._normalize(r)

        return None

    def _normalize(self, row):
        return {
            "id": row.get("courier_id", ""),
            "name": f"{row.get('Имя', '')} {row.get('Фамилия', '')}".strip(),
            "phone": row.get("Номер телефона", ""),
            "transport": row.get("Тип передвижения", ""),
            "partner": row.get("Лог партнеры", ""),
            "city": row.get("Город", ""),
            "bag": row.get("Сумка", ""),
            "status": row.get("Статус курьера", ""),
        }
