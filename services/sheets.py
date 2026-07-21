import gspread
import os
import json
import asyncio
import logging
import time
from google.oauth2.service_account import Credentials
from typing import List, Dict, Any
from config import settings

logger = logging.getLogger("sheets")

class SheetsService:
    def __init__(self):
        sa_json = os.getenv('GOOGLE_SERVICE_ACCOUNT_JSON') or getattr(settings, 'GOOGLE_SERVICE_ACCOUNT_JSON', None)
        if not sa_json:
            raise RuntimeError('GOOGLE_SERVICE_ACCOUNT_JSON not set')
        info = json.loads(sa_json)
        scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
        ]
        creds = Credentials.from_service_account_info(info, scopes=scopes)
        self.client = gspread.authorize(creds)
        self._lock = asyncio.Lock()

    async def fetch_sheet(self, name: str) -> List[Dict[str, Any]]:
        # run blocking call in thread with retries and backoff
        attempts = 3
        backoff = 1
        for i in range(attempts):
            try:
                return await asyncio.to_thread(self._fetch_sheet_sync, name)
            except Exception:
                logger.exception(f"Attempt {i+1}/{attempts} failed to fetch sheet '{name}'")
                if i < attempts - 1:
                    await asyncio.sleep(backoff)
                    backoff *= 2
        # final failure
        logger.error(f"Failed to fetch sheet '{name}' after {attempts} attempts")
        return []

    def _fetch_sheet_sync(self, name: str):
        # synchronous operations with gspread
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
        # Temporary debug: log fetched records to help diagnose data issues
        try:
            logger.info(f"Sheet '{name}': {records}")
        except Exception:
            # ensure logging never breaks functionality
            pass
        return records

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

    async def check_health(self) -> Dict[str, Any]:
        """Perform step-by-step health checks for the configured spreadsheet.

        Returns a dict with keys:
          connected, couriers, access, read, write
        """
        result = {
            'connected': False,
            'couriers': False,
            'access': False,
            'read': False,
            'write': False,
        }

        # 1) Try to open the spreadsheet
        try:
            if getattr(settings, 'SPREADSHEET_ID', None):
                sh = await asyncio.to_thread(self.client.open_by_key, settings.SPREADSHEET_ID)
            else:
                # fallback: try open by any means (may not be reliable)
                sh = await asyncio.to_thread(self.client.open, '')
            result['connected'] = True
        except Exception as e:
            logger.warning(f"Spreadsheet connection failed: {e}")
            return result

        # 2) Check worksheets existence
        try:
            await asyncio.to_thread(sh.worksheet, 'Курьеры')
            result['couriers'] = True
        except Exception:
            result['couriers'] = False

        try:
            await asyncio.to_thread(sh.worksheet, 'Доступ')
            result['access'] = True
        except Exception:
            result['access'] = False

        # 3) Readability test: try to read 'Курьеры' if exists
        if result['couriers']:
            try:
                ws = await asyncio.to_thread(sh.worksheet, 'Курьеры')
                await asyncio.to_thread(ws.get_all_records)
                result['read'] = True
            except Exception as e:
                logger.warning(f"Read test failed: {e}")
                result['read'] = False

        # 4) Writability test: try to create and delete a temporary worksheet
        tmp_title = f"ping_tmp_{int(time.time())}"
        try:
            tmp_ws = await asyncio.to_thread(
                sh.add_worksheet,
                tmp_title,
                1,
                1,
            )
            await asyncio.to_thread(sh.del_worksheet, tmp_ws)
            result["write"] = True
        except Exception as e:
            logger.warning(f"Write test failed: {e}")
            result['write'] = False

        return result

    # ==========================
    # ACCESS MANAGEMENT
    # ==========================

    async def add_user(
        self,
        telegram_id: int,
        name: str,
        role: str,
        added_by: str,
        date: str,
    ):
        await asyncio.to_thread(
            self._add_user_sync,
            telegram_id,
            name,
            role,
            added_by,
            date,
        )

    def _add_user_sync(
        self,
        telegram_id,
        name,
        role,
        added_by,
        date,
    ):
        if getattr(settings, "SPREADSHEET_ID", None):
            sh = self.client.open_by_key(settings.SPREADSHEET_ID)
        else:
            sh = self.client.open("Доступ")

        ws = sh.worksheet("Доступ")

        ws.append_row([
            str(telegram_id),
            name,
            role.lower(),
            added_by,
            date,
        ])

    async def update_role(
        self,
        telegram_id: int,
        role: str,
    ):
        await asyncio.to_thread(
            self._update_role_sync,
            telegram_id,
            role,
        )

    def _update_role_sync(
        self,
        telegram_id,
        role,
    ):
        if getattr(settings, "SPREADSHEET_ID", None):
            sh = self.client.open_by_key(settings.SPREADSHEET_ID)
        else:
            sh = self.client.open("Доступ")

        ws = sh.worksheet("Доступ")
        values = ws.get_all_values()

        for i, row in enumerate(values[1:], start=2):
            if len(row) >= 3 and row[0].strip() == str(telegram_id):
                ws.update_cell(i, 3, role.lower())
                return

    async def remove_user(
        self,
        telegram_id: int,
    ):
        await asyncio.to_thread(
            self._remove_user_sync,
            telegram_id,
        )

    def _remove_user_sync(
        self,
        telegram_id,
    ):
        if getattr(settings, "SPREADSHEET_ID", None):
            sh = self.client.open_by_key(settings.SPREADSHEET_ID)
        else:
            sh = self.client.open("Доступ")

        ws = sh.worksheet("Доступ")
        values = ws.get_all_values()

        for i, row in enumerate(values[1:], start=2):
            if row and row[0].strip() == str(telegram_id):
                ws.delete_rows(i)
                return

    async def list_users(self):
        return await self.fetch_sheet("Доступ")
