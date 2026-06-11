from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()

def _env_bool(name: str, default: bool = True) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


@dataclass
class Settings:
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://paycollection:paycollection@127.0.0.1:5432/paycollection",
    )
    CHANNEL_ID: str | None = os.getenv("CHANNEL_ID")
    CHANNEL_LINK: str = os.getenv("CHANNEL_LINK", "")
    CHANNEL_USERNAME: str = os.getenv("CHANNEL_USERNAME", "")
    ADMIN_TELEGRAM_ID: int | None = int(os.getenv("ADMIN_TELEGRAM_ID")) if os.getenv("ADMIN_TELEGRAM_ID") else None
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    # بدون کانال، force-join غیرفعال می‌شود — در پروداکشن true بماند
    REQUIRE_CHANNEL_JOIN: bool = _env_bool("REQUIRE_CHANNEL_JOIN", True)
    # سقف رفرال نهایی‌شده در روز برای هر دعوت‌کننده
    REFERRAL_DAILY_CAP: int = int(os.getenv("REFERRAL_DAILY_CAP", "50"))
    PAYMENT_CARD_NUMBER: str = os.getenv("PAYMENT_CARD_NUMBER", "")
    UPLOADS_DIR: str = os.getenv("UPLOADS_DIR", "data/uploads/receipts")
    MIN_TOPUP_RIAL: int = int(os.getenv("MIN_TOPUP_RIAL", "10000"))
    BACKEND_API_URL: str = os.getenv("BACKEND_API_URL", "http://127.0.0.1:8000/api/v1")
    INTERNAL_API_KEY: str | None = os.getenv("INTERNAL_API_KEY")
    BOT_PROXY_ENABLED: bool = _env_bool("BOT_PROXY_ENABLED", False)
    BOT_PROXY_URL: str = os.getenv("BOT_PROXY_URL", "")


settings = Settings()
