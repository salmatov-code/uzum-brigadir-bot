from services.sheets import SheetsService
import asyncio
from typing import Dict, Any, List, Optional


class Cache:
    def __init__(self, sheets: SheetsService, refresh_interval: int = 300):
        self.sheets = sheets
        self.refresh_interval = refresh_interval
        self._data: List[Dict[str, Any]] = []
        self._videos = []
        self._access = []
        self._task = None
        self._lock = asyncio.Lock()

    async def start(self):
        # initial load
        await self.refresh()
        while True:
            await asyncio.sleep(self.refresh_interval)
            await self.refresh()

    async def refresh(self):
        async with self._lock:
            self._access = await self.sheets.get_access_list()
            self._data = await self.sheets.get_couriers()
            self._videos = await self.sheets.get_videos()

    def get_all(self):
        return list(self._data)

    def find(self, query: str, key: Optional[str] = None):
        q = query.strip().lower()
        for r in self._data:
            # try a few common column names
            if key == 'id' and str(r.get('ID','')).lower() == q:
                return self._normalize(r)
            if key == 'phone' and q in str(r.get('Телефон','')).lower():
                return self._normalize(r)
            if key == 'bag' and q in str(r.get('Номер сумки','')).lower():
                return self._normalize(r)
        return None

    def is_allowed(self, tg_id: int) -> bool:
        """Check whether tg_id exists in access list. Access rows can contain the id in any column.
        Returns True if found, False otherwise.
        """
        try:
            target = int(tg_id)
        except Exception:
            target = None

        for row in self._access:
            for v in row.values():
                if v is None:
                    continue
                s = str(v).strip()
                # numeric compare
                try:
                    if target is not None and int(s) == target:
                        return True
                except Exception:
                    # fallback to string compare
                    if s == str(tg_id):
                        return True
        return False

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
