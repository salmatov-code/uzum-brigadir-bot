from services.sheets import SheetsService
import asyncio
from typing import Dict, Any, List, Optional


class Cache:
    def __init__(self, sheets: SheetsService, refresh_interval: int = 300):
        self.sheets = sheets
        self.refresh_interval = refresh_interval
        self._data: List[Dict[str, Any]] = []
        self._videos = []
        self._access: Dict[str, str] = {}
        self._lock = asyncio.Lock()

    async def start(self):
        await self.refresh()
        while True:
            await asyncio.sleep(self.refresh_interval)
            await self.refresh()

    async def refresh(self):
        async with self._lock:
            try:
                access = await self.sheets.get_access_list()

                self._access = {}

                for row in access:
                    tg_id = str(row.get("Telegram ID", "")).strip()
                    role = str(row.get("Роль", "user")).strip().lower()

                    if tg_id:
                        self._access[tg_id] = role

            except Exception as e:
                print("ACCESS fetch error:", e)
                self._access = {}

            print("ACCESS:", self._access)

            try:
                self._data = await self.sheets.get_couriers()
                print(f"Loaded couriers: {len(self._data)}")
            except Exception as e:
                print("Couriers:", e)
                self._data = []

            try:
                self._videos = await self.sheets.get_videos()
            except Exception as e:
                print("Videos:", e)
                self._videos = []

    def get_all(self):
        return list(self._data)

    def find(self, query: str, key: Optional[str] = None):
        q = query.strip().lower()

        for r in self._data:
            courier_id = str(
                r.get("courier_id")
                or r.get("ID")
                or r.get("Id")
                or r.get("id")
                or ""
            ).strip().lower()

            phone = str(
                r.get("Телефон")
                or r.get("Номер телефона")
                or ""
            ).strip().lower()

            bag = str(
                r.get("Сумка")
                or r.get("Номер сумки")
                or ""
            ).strip().lower()

            if key == "id" and courier_id == q:
                return self._normalize(r)

            if key == "phone" and q in phone:
                return self._normalize(r)

            if key == "bag" and bag == q:
                return self._normalize(r)

        return None

    def is_allowed(self, tg_id: int) -> bool:
        return str(tg_id) in self._access

    def is_admin(self, tg_id: int) -> bool:
        return self._access.get(str(tg_id)) == "admin"

    def _normalize(self, row: Dict[str, Any]):
        return {
            "id": (
                row.get("courier_id")
                or row.get("ID")
                or row.get("Id")
                or row.get("id")
            ),
            "name": (
                row.get("ФИО")
                or f"{row.get('Имя', '')} {row.get('Фамилия', '')}".strip()
            ),
            "phone": row.get("Телефон") or row.get("Номер телефона", ""),
            "transport": row.get("Тип транспорта", ""),
            "partner": row.get("Партнёр") or row.get("Партнер", ""),
            "city": row.get("Город", ""),
            "bag": row.get("Сумка") or row.get("Номер сумки", ""),
            "status": row.get("Статус", ""),
        }
