from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.user import User
from app.utils.security import generate_referral_code
from app.utils.telegram import is_iranian_phone, is_valid_iranian_phone, normalize_phone, sanitize_referral_code


class PhoneVerificationResult:
    OK = "ok"
    DUPLICATE = "duplicate"
    INVALID = "invalid"
    ALREADY_VERIFIED = "already_verified"


async def _generate_unique_referral_code(session: AsyncSession) -> str:
    for _ in range(10):
        code = generate_referral_code(8)
        query = select(User).where(User.referral_code == code)
        result = await session.execute(query)
        if result.scalar_one_or_none() is None:
            return code
    raise RuntimeError("Unable to generate unique referral code")


async def get_user_by_telegram_id(session: AsyncSession, telegram_id: int) -> User | None:
    result = await session.execute(select(User).where(User.telegram_id == telegram_id))
    return result.scalar_one_or_none()


async def get_user_by_referral_code(session: AsyncSession, referral_code: str) -> User | None:
    result = await session.execute(select(User).where(User.referral_code == referral_code))
    return result.scalar_one_or_none()


async def get_user_by_id(session: AsyncSession, user_id: int) -> User | None:
    result = await session.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def get_user_by_phone(session: AsyncSession, phone: str) -> User | None:
    normalized = normalize_phone(phone)
    result = await session.execute(select(User).where(User.phone_number == normalized))
    return result.scalar_one_or_none()


async def count_inviter_referrals_today(session: AsyncSession, inviter_id: int) -> int:
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    result = await session.execute(
        select(func.count())
        .select_from(User)
        .where(
            User.invited_by == inviter_id,
            User.referral_finalized.is_(True),
            User.referral_finalized_at >= today_start,
        )
    )
    return int(result.scalar_one() or 0)


def can_earn_referral_rewards(user: User | None) -> bool:
    if user is None:
        return False
    return bool(user.verified and not user.is_suspicious)


def referral_eligible(user: User) -> bool:
    return (
        user.verified
        and not user.is_suspicious
        and user.is_iranian
        and bool(user.phone_number)
        and is_valid_iranian_phone(user.phone_number)
        and user.joined_channel
        and not user.referral_finalized
        and user.invited_by is not None
    )


async def create_user(session: AsyncSession, tg_user, inviter_id: int | None = None) -> User:
    referral_code = await _generate_unique_referral_code(session)
    user = User(
        telegram_id=tg_user.id,
        first_name=tg_user.first_name,
        last_name=tg_user.last_name,
        username=tg_user.username,
        referral_code=referral_code,
        invited_by=inviter_id,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def get_or_create_user(session: AsyncSession, tg_user, inviter_id: int | None = None) -> User:
    user = await get_user_by_telegram_id(session, tg_user.id)
    if user is None:
        user = await create_user(session, tg_user, inviter_id)
    elif (
        inviter_id
        and user.invited_by is None
        and not user.verified
        and not user.referral_finalized
        and user.telegram_id != inviter_id
    ):
        user.invited_by = inviter_id
        await session.commit()
        await session.refresh(user)
    return user


async def register_referral(session: AsyncSession, user: User, referral_code: str) -> User | None:
    if user.verified or user.invited_by or user.referral_finalized or not referral_code:
        return None

    code = sanitize_referral_code(referral_code)
    if code is None:
        return None

    inviter = await get_user_by_referral_code(session, code)
    if inviter is None or inviter.id == user.id:
        return None
    if inviter.telegram_id == user.telegram_id:
        return None
    if inviter.is_suspicious or not inviter.verified:
        return None

    user.invited_by = inviter.id
    await session.commit()
    await session.refresh(user)
    return inviter


async def mark_phone_verified(session: AsyncSession, user: User, phone: str) -> str:
    if user.verified and user.phone_number:
        return PhoneVerificationResult.ALREADY_VERIFIED

    normalized_phone = normalize_phone(phone)
    if not is_valid_iranian_phone(normalized_phone):
        user.verified = True
        user.is_iranian = False
        user.is_suspicious = False
        await session.commit()
        await session.refresh(user)
        return PhoneVerificationResult.INVALID

    existing = await get_user_by_phone(session, normalized_phone)
    if existing is not None and existing.telegram_id != user.telegram_id:
        user.verified = True
        user.is_iranian = True
        user.is_suspicious = True
        await session.commit()
        await session.refresh(user)
        return PhoneVerificationResult.DUPLICATE

    user.phone_number = normalized_phone
    user.verified = True
    user.is_iranian = True
    user.is_suspicious = False
    await session.commit()
    await session.refresh(user)
    return PhoneVerificationResult.OK


async def mark_channel_joined(session: AsyncSession, user: User) -> None:
    if not user.joined_channel:
        user.joined_channel = True
        await session.commit()
        await session.refresh(user)


async def finalize_referral(session: AsyncSession, user: User, inviter: User) -> bool:
    await session.refresh(user)
    await session.refresh(inviter)

    if not referral_eligible(user):
        return False
    if user.invited_by != inviter.id:
        return False
    if inviter.telegram_id == user.telegram_id:
        return False
    if inviter.is_suspicious:
        return False

    daily_count = await count_inviter_referrals_today(session, inviter.id)
    if daily_count >= settings.REFERRAL_DAILY_CAP:
        return False

    inviter.invited_count += 1
    inviter.coins += 1
    user.referral_finalized = True
    user.referral_finalized_at = datetime.now(timezone.utc)
    user.joined_channel = True
    await session.commit()
    await session.refresh(user)
    await session.refresh(inviter)
    return True


async def try_complete_referral(session: AsyncSession, user: User, *, channel_member: bool) -> bool:
    if not channel_member or not user.invited_by:
        return False

    inviter = await get_user_by_id(session, user.invited_by)
    if inviter is None:
        return False

    if not user.joined_channel:
        await mark_channel_joined(session, user)
        await session.refresh(user)

    return await finalize_referral(session, user, inviter)


def build_profile_text(user: User) -> str:
    first_line = "👤 پروفایل کاربری\n\n"
    full_name = " ".join(filter(None, [user.first_name or "", user.last_name or ""])) or "بدون نام"
    username = f"@{user.username}" if user.username else "بدون نام کاربری"
    from app.utils.files import format_rial
    from app.utils.jalali import format_jalali_datetime

    return (
        f"{first_line}"
        f"📱 نام: {full_name}\n"
        f"🆔 نام کاربری: {username}\n"
        f"🔢 آیدی: {user.telegram_id}\n"
        f"📅 ثبت نام: {format_jalali_datetime(user.created_at)}\n"
        f"🥇 کوین: {user.coins}\n"
        f"📊 زیر مجموعه: {user.invited_count}\n\n"
        f"💰 موجودی: {format_rial(user.balance or 0)}"
    )
