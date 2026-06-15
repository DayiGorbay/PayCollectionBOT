from __future__ import annotations

import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import PanelConflictError, PanelError
from app.models.catalog import Order, Panel, Product, UserService
from app.models.telegram_user import TelegramUser
from app.providers.factory import create_provider
from app.providers.models import PanelUser, PanelUserCreate
from app.repositories.panel_repository import PanelRepository
from app.services.service_sync_service import apply_panel_user_to_service

logger = logging.getLogger(__name__)


async def get_service_by_id(session: AsyncSession, service_id: int) -> UserService | None:
    return await session.get(UserService, service_id)


async def get_service_by_order_id(session: AsyncSession, order_id: int) -> UserService | None:
    result = await session.execute(select(UserService).where(UserService.order_id == order_id))
    return result.scalar_one_or_none()


async def list_services(
    session: AsyncSession,
    *,
    telegram_user_id: int | None = None,
    include_deleted: bool = False,
) -> list[UserService]:
    query = select(UserService).order_by(UserService.id.desc())
    if telegram_user_id is not None:
        query = query.where(UserService.telegram_user_id == telegram_user_id)
    if not include_deleted:
        query = query.where(UserService.status != "deleted")
    result = await session.execute(query)
    return list(result.scalars().all())


async def resolve_user_label(session: AsyncSession, telegram_user_id: int) -> str:
    result = await session.execute(
        select(TelegramUser).where(TelegramUser.telegram_id == telegram_user_id)
    )
    user = result.scalar_one_or_none()
    if user is None:
        return str(telegram_user_id)
    name = " ".join(filter(None, [user.first_name, user.last_name])).strip()
    if user.username:
        return f"{name or user.username} (@{user.username})"
    return name or str(telegram_user_id)


async def resolve_product_name(session: AsyncSession, product_id: int | None) -> str | None:
    if not product_id:
        return None
    product = await session.get(Product, product_id)
    return product.name if product else None


async def resolve_panel_name(session: AsyncSession, panel_id: int | None) -> str | None:
    if not panel_id:
        return None
    panel = await session.get(Panel, panel_id)
    return panel.name if panel else None


async def create_panel_user_idempotent(provider, data: PanelUserCreate) -> PanelUser:
    try:
        return await provider.create_user(data)
    except PanelConflictError:
        logger.info("panel_user_conflict username=%s — fetching existing user", data.username)
        return await provider.get_user(data.username)
    except PanelError as exc:
        message = str(exc).lower()
        if "already exists" in message or "exist" in message:
            logger.info("panel_user_exists username=%s — fetching existing user", data.username)
            return await provider.get_user(data.username)
        raise


def _links_from_panel_user(panel_user: PanelUser) -> tuple[str | None, str | None]:
    subscription_url = panel_user.subscription_url
    config_text = panel_user.links[0] if panel_user.links else subscription_url
    if not subscription_url and config_text:
        subscription_url = config_text
    if not subscription_url and not config_text:
        subscription_url = f"user:{panel_user.username}"
        config_text = subscription_url
    return subscription_url, config_text


async def persist_service_from_panel_user(
    session: AsyncSession,
    *,
    telegram_user_id: int,
    order: Order | None,
    product: Product | None,
    panel,
    panel_user: PanelUser,
    data_gb: int,
    expire_at,
) -> UserService:
    subscription_url, config_text = _links_from_panel_user(panel_user)

    user_id: int | None = None
    result = await session.execute(
        select(TelegramUser).where(TelegramUser.telegram_id == telegram_user_id)
    )
    tg_user = result.scalar_one_or_none()
    if tg_user:
        user_id = tg_user.id

    service = UserService(
        user_id=user_id,
        telegram_user_id=telegram_user_id,
        order_id=order.id if order else None,
        product_id=product.id if product else None,
        panel_id=panel.id,
        panel_type=panel.panel_type,
        panel_username=panel_user.username,
        subscription_url=subscription_url,
        config_text=config_text,
        data_gb=data_gb,
        expire_at=expire_at,
        status="active",
    )
    apply_panel_user_to_service(service, panel_user)
    session.add(service)
    await session.flush()

    if order is not None:
        order.service_id = service.id

    return service
