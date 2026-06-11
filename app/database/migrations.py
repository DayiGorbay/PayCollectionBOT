from __future__ import annotations

import logging

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

logger = logging.getLogger(__name__)


async def run_sqlite_migrations(engine: AsyncEngine) -> None:
    """ستون‌های جدید را برای دیتابیس‌های قدیمی اضافه می‌کند."""
    if not str(engine.url).startswith("sqlite"):
        return

    statements = [
        "ALTER TABLE users ADD COLUMN referral_finalized_at DATETIME",
    ]

    async with engine.begin() as connection:
        for statement in statements:
            try:
                await connection.execute(text(statement))
                logger.info("Migration applied: %s", statement)
            except Exception:
                pass
