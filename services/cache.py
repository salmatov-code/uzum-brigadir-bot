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
            if key == 'id' and str(r.get('ID','')).lower() == q:
                return self._normalize(r)
            if key == 'phone' and q in str(r.get('Телефон','')).lower():
                return self._normalize(r)
            if key == 'bag' and q in str(r.get('Номер сумки','')).lower():
                return self._normalize(r)
        return None

    def _normalize(self, row: Dict[str, Any]):
        return {
            'id': row.get('ID') or row.get('Id') or row.get('id'),
            'name': f"{row.get('Имя','')} {row.get('Фамилия','')}",
            'phone': row.get('Телефон',''),
            'transport': row.get('Тип транспорта',''),
            'partner': row.get('Партнёр','') or row.get('Партнер',''),
            'city': row.get('Город',''),
            'bag': row.get('Номер сумки','') or row.get('Сумка',''),
            'status': row.get('Статус','')
        }
