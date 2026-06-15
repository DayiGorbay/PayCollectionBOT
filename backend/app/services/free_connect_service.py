from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.catalog import FreeConnectConfig, Panel, UserService
from app.models.telegram_user import TelegramUser
from app.providers.factory import create_provider
from app.providers.models import PanelUserCreate
from app.repositories.panel_repository import PanelRepository
from app.services.provision_service import _data_limit_bytes, allocate_panel_username, sanitize_username
from app.services.telegram_notify import send_service_activation_message


async def get_config(session: AsyncSession) -> FreeConnectConfig:
    result = await session.execute(select(FreeConnectConfig).where(FreeConnectConfig.id == 1))
    row = result.scalar_one_or_none()
    if row is None:
        row = FreeConnectConfig(id=1, coins_required=5, data_gb=10, duration_days=30, is_active=False)
        session.add(row)
        await session.flush()
    return row


async def update_config(
    session: AsyncSession,
    *,
    coins_required: int,
    data_gb: int,
    panel_id: int | None,
    duration_days: int,
    is_active: bool,
) -> FreeConnectConfig:
    if panel_id is not None:
        panel = await session.get(Panel, panel_id)
        if panel is None:
            raise ValueError("پنل انتخاب‌شده یافت نشد.")

    config = await get_config(session)
    config.coins_required = coins_required
    config.data_gb = data_gb
    config.panel_id = panel_id
    config.duration_days = duration_days
    config.is_active = is_active
    await session.flush()
    return config


async def provision_free_connect(
    session: AsyncSession,
    telegram_user_id: int,
    requested_username: str,
) -> UserService:
    config = await get_config(session)
    if not config.is_active:
        raise ValueError("اتصال رایگان فعلاً غیرفعال است.")
    if not config.panel_id:
        raise ValueError("پنل اتصال رایگان تنظیم نشده است.")

    result = await session.execute(select(TelegramUser).where(TelegramUser.telegram_id == telegram_user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise ValueError("کاربر یافت نشد.")
    if user.is_blocked:
        raise ValueError("حساب شما مسدود است.")
    if (user.coins or 0) < config.coins_required:
        raise ValueError(f"حداقل {config.coins_required} کوین لازم است.")

    panel_repo = PanelRepository(session)
    panel = await panel_repo.get_by_id(config.panel_id)
    if panel is None:
        raise ValueError("پنل یافت نشد.")

    provider = create_provider(panel, session)
    panel_username = await allocate_panel_username(provider, sanitize_username(requested_username))

    data_limit = _data_limit_bytes(config.data_gb)
    now = datetime.now(timezone.utc)
    expire_at = now + timedelta(days=config.duration_days)

    panel_user = await provider.create_user(
        PanelUserCreate(
            username=panel_username,
            data_limit_bytes=data_limit,
            expire_at=expire_at,
            note=f"free_connect:{telegram_user_id}",
        )
    )

    subscription_url = panel_user.subscription_url
    config_text = panel_user.links[0] if panel_user.links else subscription_url
    if not subscription_url and config_text:
        subscription_url = config_text
    if not subscription_url and not config_text:
        subscription_url = f"user:{panel_user.username}"
        config_text = subscription_url

    user.coins = (user.coins or 0) - config.coins_required

    service = UserService(
        telegram_user_id=telegram_user_id,
        order_id=None,
        product_id=None,
        panel_id=panel.id,
        panel_type=panel.panel_type,
        panel_username=panel_user.username,
        subscription_url=subscription_url,
        config_text=config_text,
        data_gb=config.data_gb,
        expire_at=expire_at,
        status="active",
    )
    session.add(service)
    await session.flush()

    try:
        await send_service_activation_message(
            telegram_user_id,
            username=service.panel_username,
            data_gb=service.data_gb,
            subscription_url=service.subscription_url or "",
            config_text=service.config_text,
        )
    except Exception:
        pass

    return service
