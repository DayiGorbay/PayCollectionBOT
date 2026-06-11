from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.services.auth_service import ensure_default_admin


async def bootstrap_application(session: AsyncSession) -> None:
    """فقط ادمین پیش‌فرض را در اولین اجرا می‌سازد — بدون داده نمونه."""
    await ensure_default_admin(session)
