from __future__ import annotations

import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import PanelError
from app.models.catalog import UserService
from app.providers.factory import create_provider
from app.repositories.panel_repository import PanelRepository

logger = logging.getLogger(__name__)


async def delete_user_service(session: AsyncSession, service_id: int, telegram_user_id: int) -> None:
    result = await session.execute(
        select(UserService).where(
            UserService.id == service_id,
            UserService.telegram_user_id == telegram_user_id,
            UserService.status == "active",
        )
    )
    service = result.scalar_one_or_none()
    if service is None:
        raise ValueError("سرویس یافت نشد.")

    if service.panel_id:
        panel = await PanelRepository(session).get_by_id(service.panel_id)
        if panel:
            provider = create_provider(panel, session)
            try:
                await provider.delete_user(service.panel_username)
            except PanelError as exc:
                logger.warning(
                    "panel_delete_failed service_id=%s panel_id=%s error=%s",
                    service.id,
                    panel.id,
                    exc,
                )

    service.status = "deleted"
    await session.flush()
