from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user_service import UserService


async def list_active_services(session: AsyncSession, telegram_id: int) -> list[UserService]:
    result = await session.execute(
        select(UserService)
        .where(
            UserService.telegram_user_id == telegram_id,
            UserService.status == "active",
        )
        .order_by(UserService.id.desc())
    )
    return list(result.scalars().all())


async def get_service(session: AsyncSession, service_id: int, telegram_id: int) -> UserService | None:
    result = await session.execute(
        select(UserService).where(
            UserService.id == service_id,
            UserService.telegram_user_id == telegram_id,
            UserService.status == "active",
        )
    )
    return result.scalar_one_or_none()


async def mark_service_deleted(session: AsyncSession, service: UserService) -> None:
    service.status = "deleted"
    await session.commit()
