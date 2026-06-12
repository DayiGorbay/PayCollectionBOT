from __future__ import annotations

import re

from aiogram import Bot
from aiogram.enums import ChatMemberStatus

IRAN_MOBILE_PATTERN = re.compile(r"^\+989\d{9}$")
REFERRAL_CODE_PATTERN = re.compile(r"^[A-Za-z0-9_-]{4,32}$")


def normalize_channel_link(
    channel_link: str | None = None,
    channel_username: str | None = None,
) -> str | int | None:
    if channel_link:
        cleaned = channel_link.strip()

        if cleaned.startswith("https://") or cleaned.startswith("http://"):
            cleaned = re.sub(r"^https?://t\.me/", "", cleaned)

        if cleaned.startswith("@"):
            return cleaned

        if cleaned.isdigit() or (
            cleaned.startswith("-100")
            and cleaned.replace("-", "").isdigit()
        ):
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

    if cleaned.startswith("00"):
        cleaned = "+" + cleaned[2:]

    if cleaned.startswith("0") and len(cleaned) == 11 and cleaned[1] == "9":
        return "+98" + cleaned[1:]

    if len(cleaned) == 10 and cleaned.startswith("9"):
        return "+98" + cleaned

    if cleaned.startswith("+98"):
        return cleaned

    if cleaned.startswith("0098"):
        return "+" + cleaned[4:]

    if cleaned.startswith("98") and len(cleaned) >= 12:
        return "+" + cleaned

    return cleaned


def is_valid_iranian_phone(phone: str) -> bool:
    normalized = normalize_phone(phone)
    return bool(IRAN_MOBILE_PATTERN.match(normalized))


def is_iranian_phone(phone: str) -> bool:
    return is_valid_iranian_phone(phone)


def sanitize_referral_code(code: str) -> str | None:
    cleaned = code.strip()[:32]

    if not cleaned or not REFERRAL_CODE_PATTERN.match(cleaned):
        return None

    return cleaned


async def is_channel_member(
    bot: Bot,
    channel_id: str | int | None,
    user_id: int,
) -> bool:
    if channel_id is None:
        return False

    try:
        member = await bot.get_chat_member(
            chat_id=channel_id,
            user_id=user_id,
        )

        return member.status in (
            ChatMemberStatus.MEMBER,
            ChatMemberStatus.ADMINISTRATOR,
            ChatMemberStatus.CREATOR,
        )

    except Exception:
        return False


def get_channel_chat_id(
    channel_id: str | None = None,
    channel_link: str | None = None,
    channel_username: str | None = None,
) -> str | int | None:
    if channel_id:
        return normalize_channel_link(channel_id, channel_username)

    return normalize_channel_link(
        channel_link or None,
        channel_username,
    )


def is_channel_configured(
    channel_id: str | None = None,
    channel_link: str | None = None,
    channel_username: str | None = None,
) -> bool:
    return (
        get_channel_chat_id(
            channel_id,
            channel_link,
            channel_username,
        )
        is not None
    )
