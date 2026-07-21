import gspread
import os
import json
import asyncio
import logging
from google.oauth2.service_account import Credentials
from typing import List, Dict, Any
from config import settings

logger = logging.getLogger("sheets")


class SheetsService:
    def __init__(self):
        sa_json = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON") or getattr(
            settings, "GOOGLE_SERVICE_ACCOUNT_JSON", None
        )

        if not sa_json:
            raise RuntimeError("GOOGLE_SERVICE_ACCOUNT_JSON not set")

        info = json.loads(sa_json)

        scopes = [
            "https://www.googleapis.com/auth/spreadsheets.readonly",
        ]

        creds = Credentials.from_service_account_info(info, scopes=scopes)
        self.client = gspread.authorize(creds)

    async def fetch_sheet(self, name: str):
        return await asyncio.to_thread(self._fetch_sheet_sync, name)

    def _fetch_sheet_sync(self, name: str):
        if getattr(settings, "SPREADSHEET_ID", None):
            sh = self.client.open_by_key(settings.SPREADSHEET_ID)
        else:
            sh = self.client.open(name)

        ws = sh.worksheet(name)

        # Лист доступа читаем отдельно
        if name == "Доступ":
            ids = ws.col_values(1)[1:]  # пропускаем заголовок

            result = []
            for tg_id in ids:
                tg_id = str(tg_id).strip()
                if tg_id:
                    result.append({"Telegram ID": tg_id})

            logger.info(f"Loaded access list: {result}")
            return result

        return ws.get_all_records()

    async def get_access_list(self):
        return await self.fetch_sheet("Доступ")

    async def get_couriers(self):
        return await self.fetch_sheet("Курьеры")

    async def get_videos(self):
        return await self.fetch_sheet("Видео")

    async def find_video(self, key: str):
        videos = await self.get_videos()

        for r in videos:
            if (
                str(r.get("id", "")).strip() == str(key).strip()
                or str(r.get("bag", "")).strip() == str(key).strip()
                or str(r.get("phone", "")).strip() == str(key).strip()
            ):
                if r.get("video"):
                    return r["video"]

                if r.get("doc"):
                    return r["doc"]

        return None
