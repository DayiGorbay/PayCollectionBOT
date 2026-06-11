from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.core.rate_limit import LoginRateLimiter
from app.core.security import create_access_token, hash_password, verify_password
from app.models.admin_user import AdminUser
from app.schemas.auth import AuthUserOut, LoginResponse

settings = get_settings()
login_limiter = LoginRateLimiter(
    max_attempts=settings.LOGIN_RATE_LIMIT_MAX_ATTEMPTS,
    window_seconds=settings.LOGIN_RATE_LIMIT_WINDOW_SECONDS,
)

ACCOUNT_LOCK_MINUTES = 15
MAX_FAILED_BEFORE_LOCK = 8


async def ensure_default_admin(session: AsyncSession) -> None:
    result = await session.execute(select(AdminUser).where(AdminUser.username == settings.ADMIN_USERNAME))
    admin = result.scalar_one_or_none()
    if admin is None:
        session.add(
            AdminUser(
                username=settings.ADMIN_USERNAME,
                password_hash=hash_password(settings.ADMIN_PASSWORD),
                display_name=settings.ADMIN_DISPLAY_NAME,
                role="admin",
            )
        )
        await session.flush()


async def authenticate_admin(
    session: AsyncSession,
    username: str,
    password: str,
    client_ip: str,
) -> LoginResponse:
    rate_key = f"{client_ip}:{username.lower()}"
    if login_limiter.is_blocked(rate_key):
        raise ValueError("تعداد تلاش‌های ورود زیاد است. لطفاً بعداً تلاش کنید.")

    result = await session.execute(select(AdminUser).where(AdminUser.username == username))
    admin = result.scalar_one_or_none()
    now = datetime.now(timezone.utc)

    if admin is None:
        login_limiter.record_failure(rate_key)
        raise ValueError("نام کاربری یا رمز عبور نادرست است.")

    if admin.locked_until and admin.locked_until > now:
        raise ValueError("حساب به‌طور موقت قفل شده است. بعداً تلاش کنید.")

    if not admin.is_active:
        raise ValueError("حساب غیرفعال است.")

    if not verify_password(password, admin.password_hash):
        admin.failed_login_attempts += 1
        if admin.failed_login_attempts >= MAX_FAILED_BEFORE_LOCK:
            admin.locked_until = now + timedelta(minutes=ACCOUNT_LOCK_MINUTES)
        login_limiter.record_failure(rate_key)
        raise ValueError("نام کاربری یا رمز عبور نادرست است.")

    admin.failed_login_attempts = 0
    admin.locked_until = None
    admin.last_login_at = now
    login_limiter.reset(rate_key)

    token, expires_in = create_access_token(
        subject=str(admin.id),
        extra_claims={"admin_id": admin.id, "role": admin.role},
    )

    return LoginResponse(
        access_token=token,
        expires_in=expires_in,
        user=AuthUserOut(
            id=admin.id,
            username=admin.username,
            display_name=admin.display_name,
            role=admin.role,
        ),
    )
