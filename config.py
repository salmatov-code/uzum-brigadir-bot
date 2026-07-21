from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    BOT_TOKEN: str
    GOOGLE_SERVICE_ACCOUNT_JSON: str
    SPREADSHEET_ID: str
    ARCHIVE_CHAT_ID: int = -1004317651045
    TIMEZONE: str = "Asia/Tashkent"
    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )

settings = Settings()
