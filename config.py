import os
from pydantic import BaseSettings

class Settings(BaseSettings):
    BOT_TOKEN: str
    GOOGLE_SERVICE_ACCOUNT_JSON: str  # JSON string
    SPREADSHEET_ID: str
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"

settings = Settings()
