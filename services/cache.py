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
                    tg = str(row.get("Telegram ID", "")).strip()
                    role = str(row.get("Роль", "user")).strip().lower()

                    if tg:
                        self._access[tg] = role

            except Exception as e:
                print("ACCESS ERROR:", e)
                self._access = {}

            print("ACCESS:", self._access)

            try:
                self._data = await self.sheets.get_couriers()
                print(f"Loaded couriers: {len(self._data)}")
            except Exception as e:
                print("COURIERS ERROR:", e)
                self._data = []

            try:
                self._videos = await self.sheets.get_videos()
            except Exception:
                self._videos = []

    def get_all(self):
        return list(self._data)

    def find(self, query: str, key: Optional[str] = None):
        q = query.strip().lower()

        for row in self._data:

            courier_id = str(row.get("courier_id", "")).strip().lower()

            phone = str(row.get("Номер телефона", "")).strip().lower()

            bag = str(row.get("Сумка", "")).strip().lower()

            if key == "id":
                if courier_id == q:
                    return self._normalize(row)

            elif key == "phone":
                if q in phone:
                    return self._normalize(row)

            elif key == "bag":
                if bag == q:
                    return self._normalize(row)

        return None

    def is_allowed(self, tg_id: int):
        return str(tg_id) in self._access

    def is_admin(self, tg_id: int):
        return self._access.get(str(tg_id)) == "admin"

    def _normalize(self, row):

        return {
            "id": row.get("courier_id"),
            "name": f"{row.get('Имя','')} {row.get('Фамилия','')}".strip(),
            "phone": row.get("Номер телефона", ""),
            "transport": row.get("Тип передвижения", ""),
            "partner": row.get("Лог партнеры", ""),
            "city": row.get("Город", ""),
            "bag": row.get("Сумка", ""),
            "status": row.get("Статус курьера", "")
        }
