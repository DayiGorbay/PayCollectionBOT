from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()

@dataclass
class Settings:
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./data.db")
    CHANNEL_ID: str | None = os.getenv("CHANNEL_ID")
    CHANNEL_LINK: str = os.getenv("CHANNEL_LINK", "")
    CHANNEL_USERNAME: str = os.getenv("CHANNEL_USERNAME", "")
    ADMIN_TELEGRAM_ID: int | None = int(os.getenv("ADMIN_TELEGRAM_ID")) if os.getenv("ADMIN_TELEGRAM_ID") else None
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")


settings = Settings()
