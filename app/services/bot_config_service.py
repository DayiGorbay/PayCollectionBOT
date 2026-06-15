from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.bot_setting import BotSetting


async def get_setting(session: AsyncSession, key: str, default: str = "") -> str:
    result = await session.execute(select(BotSetting).where(BotSetting.key == key))
    row = result.scalar_one_or_none()
    if row is None or not row.value.strip():
        return default
    return row.value.strip()


async def get_payment_card_number(session: AsyncSession) -> str:
    return await get_setting(session, "payment_card_number", settings.PAYMENT_CARD_NUMBER)


async def get_payment_card_holder(session: AsyncSession) -> str:
    return await get_setting(session, "payment_card_holder", "")
