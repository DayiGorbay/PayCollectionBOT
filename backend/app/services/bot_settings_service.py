from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.catalog import BotSetting

DEFAULT_KEYS = {
    "payment_card_number": "",
    "payment_card_holder": "",
    "channel_id": "",
    "channel_link": "",
    "channel_username": "",
    "admin_telegram_id": "",
    "require_channel_join": "true",
    "min_topup_rial": "10000",
    "referral_daily_cap": "50",
    "log_level": "INFO",
}


async def get_all_settings(session: AsyncSession) -> dict[str, str]:
    result = await session.execute(select(BotSetting))
    stored = {row.key: row.value for row in result.scalars().all()}
    merged = dict(DEFAULT_KEYS)
    merged.update(stored)
    return merged


async def update_settings(session: AsyncSession, values: dict[str, str]) -> dict[str, str]:
    for key, value in values.items():
        if key not in DEFAULT_KEYS:
            continue
        result = await session.execute(select(BotSetting).where(BotSetting.key == key))
        row = result.scalar_one_or_none()
        if row is None:
            session.add(BotSetting(key=key, value=value))
        else:
            row.value = value
    await session.flush()
    return await get_all_settings(session)


async def get_setting(session: AsyncSession, key: str, default: str = "") -> str:
    result = await session.execute(select(BotSetting).where(BotSetting.key == key))
    row = result.scalar_one_or_none()
    if row is None:
        return DEFAULT_KEYS.get(key, default)
    return row.value
