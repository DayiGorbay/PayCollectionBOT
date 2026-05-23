from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.utils.security import generate_referral_code
from app.utils.telegram import is_iranian_phone, normalize_phone


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
    elif inviter_id and user.invited_by is None and not user.verified and user.telegram_id != inviter_id:
        user.invited_by = inviter_id
        await session.commit()
        await session.refresh(user)
    return user


async def register_referral(session: AsyncSession, user: User, referral_code: str) -> User | None:
    if user.verified or user.invited_by or not referral_code:
        return None
    inviter = await get_user_by_referral_code(session, referral_code)
    if inviter is None or inviter.id == user.id:
        return None
    user.invited_by = inviter.id
    await session.commit()
    await session.refresh(user)
    return inviter


async def mark_phone_verified(session: AsyncSession, user: User, phone: str) -> None:
    normalized_phone = normalize_phone(phone)
    user.phone_number = normalized_phone
    user.verified = True
    user.is_iranian = is_iranian_phone(normalized_phone)

    duplicate_query = select(User).where(User.phone_number == normalized_phone, User.telegram_id != user.telegram_id)
    duplicate = await session.execute(duplicate_query)
    if duplicate.scalar_one_or_none() is not None:
        user.is_suspicious = True

    await session.commit()
    await session.refresh(user)


async def mark_channel_joined(session: AsyncSession, user: User) -> None:
    if not user.joined_channel:
        user.joined_channel = True
        await session.commit()
        await session.refresh(user)


async def finalize_referral(session: AsyncSession, user: User, inviter: User) -> None:
    if user.referral_finalized or user.invited_by != inviter.id or not user.is_iranian:
        return
    inviter.invited_count += 1
    inviter.coins += 1
    user.referral_finalized = True
    user.joined_channel = True
    await session.commit()
    await session.refresh(user)
    await session.refresh(inviter)


def build_profile_text(user: User) -> str:
    first_line = f"👤 پروفایل کاربری\n\n"
    full_name = " ".join(filter(None, [user.first_name or "", user.last_name or ""])) or "بدون نام"
    username = f"@{user.username}" if user.username else "بدون نام کاربری"
    return (
        f"{first_line}"
        f"📱 نام: {full_name}\n"
        f"🆔 نام کاربری: {username}\n"
        f"🔢 آیدی: {user.telegram_id}\n"
        f"📅 ثبت نام: {user.created_at.strftime('%Y-%m-%d %H:%M')}\n"
        f"🥇 کوین: {user.coins}\n"
        f"📊 زیر مجموعه: {user.invited_count}\n\n"
        f"💰 موجودی: {user.balance} تومان"
    )
