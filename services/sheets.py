import gspread
import os
import json
import asyncio
from google.oauth2.service_account import Credentials
from typing import List, Dict, Any
from config import settings

class SheetsService:
    def __init__(self):
        sa_json = os.getenv('GOOGLE_SERVICE_ACCOUNT_JSON') or getattr(settings, 'GOOGLE_SERVICE_ACCOUNT_JSON', None)
        if not sa_json:
            raise RuntimeError('GOOGLE_SERVICE_ACCOUNT_JSON not set')
        info = json.loads(sa_json)
        scopes = [
            'https://www.googleapis.com/auth/spreadsheets.readonly',
        ]
        creds = Credentials.from_service_account_info(info, scopes=scopes)
        self.client = gspread.authorize(creds)
        self._lock = asyncio.Lock()

    async def fetch_sheet(self, name: str) -> List[Dict[str, Any]]:
        # run blocking call in thread
        return await asyncio.to_thread(self._fetch_sheet_sync, name)

    def _fetch_sheet_sync(self, name: str):
        try:
            # Prefer opening spreadsheet by ID (more reliable). Fall back to open(name).
            if getattr(settings, 'SPREADSHEET_ID', None):
                sh = self.client.open_by_key(settings.SPREADSHEET_ID)
            else:
                sh = self.client.open(name)

            # Try to get worksheet by title first; fall back to the first worksheet
            try:
                ws = sh.worksheet(name)
            except Exception:
                ws = sh.sheet1

            records = ws.get_all_records()
            return records
        except Exception:
            # on any error return empty list
            return []

    async def get_access_list(self):
        return await self.fetch_sheet('Доступ')

    async def get_couriers(self):
        return await self.fetch_sheet('Курьеры')

    async def get_videos(self):
        return await self.fetch_sheet('Видео')

    async def find_video(self, key: str):
        videos = await self.get_videos()
        for r in videos:
            # match by id, bag or phone (case-insensitive)
            if str(r.get('id','')).strip() == str(key).strip() or str(r.get('bag','')).strip() == str(key).strip() or str(r.get('phone','')).strip() == str(key).strip():
                # prefer video then doc
                if r.get('video'):
                    return r.get('video')
                if r.get('doc'):
                    return r.get('doc')
        return None
