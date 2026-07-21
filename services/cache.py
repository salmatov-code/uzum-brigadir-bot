from services.sheets import SheetsService
import asyncio
from typing import Dict, Any, List, Optional


class Cache:
    def __init__(self, sheets: SheetsService, refresh_interval: int = 300):
        self.sheets = sheets
        self.refresh_interval = refresh_interval

        self._data: List[Dict[str, Any]] = []
        self._media: Dict[str, Dict[str, Any]] = {}
        self._access: Dict[str, str] = {}

        self._lock = asyncio.Lock()

    async def start(self):
        await self.refresh()

        while True:
            await asyncio.sleep(self.refresh_interval)
            await self.refresh()

    async def refresh(self):
        async with self._lock:

            # ---------- ACCESS ----------
            try:
                access = await self.sheets.get_access_list()

                self._access = {}

                for row in access:
                    tg = str(row.get("Telegram ID", "")).strip()
                    role = str(row.get("Роль", "moderator")).strip().lower()

                    if tg:
                        self._access[tg] = role

            except Exception as e:
                print("ACCESS ERROR:", e)
                self._access = {}

            print("ACCESS:", self._access)

            # ---------- COURIERS ----------
            try:
                self._data = await self.sheets.get_couriers()
                print(f"Loaded couriers: {len(self._data)}")
            except Exception as e:
                print("COURIERS ERROR:", e)
                self._data = []

            # ---------- MEDIA ----------
            try:
                videos = await self.sheets.get_videos()

                self._media = {}

                for row in videos:
                    courier_id = str(row.get("courier_id", "")).strip()

                    if courier_id:
                        self._media[courier_id] = {
                            "video": row.get("video_message_id"),
                            "act": row.get("act_message_id"),
                            "uploaded_by": row.get("uploaded_by"),
                            "upload_date": row.get("upload_date"),
                        }

            except Exception as e:
                print("MEDIA ERROR:", e)
                self._media = {}

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

    # =======================
    # ACCESS
    # =======================

    def get_role(self, tg_id: int):
        return self._access.get(str(tg_id))

    def is_allowed(self, tg_id: int):
        return self.get_role(tg_id) is not None

    def is_admin(self, tg_id: int):
        return self.get_role(tg_id) == "admin"

    def is_moderator(self, tg_id: int):
        return self.get_role(tg_id) in ("admin", "moderator")

    # =======================
    # MEDIA
    # =======================

    def get_media(self, courier_id):
        return self._media.get(str(courier_id), {})

    def has_video(self, courier_id):
        media = self.get_media(courier_id)
        return bool(media.get("video"))

    def has_act(self, courier_id):
        media = self.get_media(courier_id)
        return bool(media.get("act"))

    # =======================
    # NORMALIZE
    # =======================

    def _normalize(self, row):
        courier_id = str(row.get("courier_id", "")).strip()

        media = self.get_media(courier_id)

        return {
            "id": courier_id,
            "name": f"{row.get('Имя', '')} {row.get('Фамилия', '')}".strip(),
            "phone": row.get("Номер телефона", ""),
            "transport": row.get("Тип передвижения", ""),
            "partner": row.get("Лог партнеры", ""),
            "city": row.get("Город", ""),
            "bag": row.get("Сумка", ""),
            "status": row.get("Статус курьера", ""),
            "has_video": bool(media.get("video")),
            "has_act": bool(media.get("act")),
            "video_message_id": media.get("video"),
            "act_message_id": media.get("act"),
            "uploaded_by": media.get("uploaded_by"),
            "upload_date": media.get("upload_date"),
        }
