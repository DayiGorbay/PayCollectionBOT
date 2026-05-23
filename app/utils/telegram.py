from __future__ import annotations

import re
from typing import Optional

from aiogram import Bot
from aiogram.types import ChatMemberStatus


def normalize_channel_link(channel_link: str | None = None, channel_username: str | None = None) -> str | int | None:
    if channel_link:
        cleaned = channel_link.strip()
        if cleaned.startswith("https://") or cleaned.startswith("http://"):
            cleaned = re.sub(r"^https?://t\.me/", "", cleaned)
        if cleaned.startswith("@"):
            return cleaned
        if cleaned.isdigit() or (cleaned.startswith("-100") and cleaned.replace("-", "").isdigit()):
            return int(cleaned)
        return f"@{cleaned}"
    if channel_username:
        cleaned = channel_username.strip()
        if cleaned.startswith("@"):
            return cleaned
        return f"@{cleaned}"
    return None


def normalize_phone(phone: str) -> str:
    cleaned = phone.strip().replace(" ", "").replace("-", "")
    if cleaned.startswith("+98"):
        return cleaned
    if cleaned.startswith("0098"):
        return "+" + cleaned[2:]
    if cleaned.startswith("98"):
        return "+" + cleaned
    return cleaned


def is_iranian_phone(phone: str) -> bool:
    normalized = normalize_phone(phone)
    return normalized.startswith("+98")


async def is_channel_member(bot: Bot, channel_id: str | int | None, user_id: int) -> bool:
    if channel_id is None:
        return False
    try:
        member = await bot.get_chat_member(chat_id=channel_id, user_id=user_id)
        return member.status not in (ChatMemberStatus.LEFT, ChatMemberStatus.KICKED, ChatMemberStatus.RESTRICTED)
    except Exception:
        return False


def get_channel_chat_id(channel_id: str | None = None, channel_link: str | None = None, channel_username: str | None = None) -> str | int | None:
    return normalize_channel_link(channel_link or None, channel_username) if not channel_id else normalize_channel_link(channel_id, channel_username)
