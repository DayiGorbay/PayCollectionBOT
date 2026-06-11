from __future__ import annotations

import logging
import random
import re
from datetime import datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import PanelError
from app.models.catalog import Order, Product, UserService
from app.providers.factory import create_provider
from app.providers.models import PanelUserCreate
from app.repositories.panel_repository import PanelRepository

logger = logging.getLogger(__name__)

_USERNAME_RE = re.compile(r"[^a-z0-9_]")


def sanitize_username(raw: str) -> str:
    value = raw.strip().lower()
    value = _USERNAME_RE.sub("", value)
    return value[:24] or "user"


def parse_data_gb(size: str | None, default: int = 10) -> int:
    if not size or size.strip() in {"—", "-", ""}:
        return default
    match = re.search(r"(\d+)", size)
    return int(match.group(1)) if match else default


def _data_limit_bytes(gb: int) -> int:
    return gb * 1024 * 1024 * 1024


async def allocate_panel_username(provider, base_username: str) -> str:
    base = sanitize_username(base_username)
    for _ in range(25):
        candidate = f"{base}{random.randint(10, 99)}"[:32]
        if not await provider.user_exists(candidate):
            return candidate
    raise ValueError("نام کاربری آزاد یافت نشد؛ دوباره تلاش کنید.")


async def provision_purchase_order(session: AsyncSession, order: Order) -> UserService:
    """
    جریان: Product → panel_id → Panel → Provider → create_user → links
    """
    if order.order_type != "purchase":
        raise ValueError("فقط سفارش خرید سرویس قابل ساخت است.")
    if not order.product_id:
        raise ValueError("محصول سفارش مشخص نیست.")
    if not order.requested_username:
        raise ValueError("نام کاربری سفارش ثبت نشده است.")

    product = await session.get(Product, order.product_id)
    if product is None:
        raise ValueError("محصول یافت نشد.")
    if not product.panel_id:
        raise ValueError("پنل محصول تنظیم نشده است.")

    panel_repo = PanelRepository(session)
    panel = await panel_repo.get_by_id(product.panel_id)
    if panel is None:
        raise ValueError("پنل محصول یافت نشد.")

    provider = create_provider(panel, session)
    panel_username = await allocate_panel_username(provider, order.requested_username)

    data_gb = parse_data_gb(product.size)
    data_limit = _data_limit_bytes(data_gb)
    now = datetime.now(timezone.utc)
    expire_at = now + timedelta(days=product.duration_days)

    try:
        panel_user = await provider.create_user(
            PanelUserCreate(
                username=panel_username,
                data_limit_bytes=data_limit,
                expire_at=expire_at,
                note=f"order:{order.id}",
            )
        )
    except PanelError as exc:
        logger.exception(
            "provision_failed order_id=%s panel_id=%s product_id=%s",
            order.id,
            panel.id,
            product.id,
        )
        raise ValueError(str(exc)) from exc

    subscription_url = panel_user.subscription_url
    config_text = panel_user.links[0] if panel_user.links else subscription_url
    if not subscription_url and config_text:
        subscription_url = config_text
    if not subscription_url:
        raise ValueError("لینک سابسکریپشن از پنل دریافت نشد.")

    service = UserService(
        telegram_user_id=order.telegram_user_id,
        order_id=order.id,
        product_id=product.id,
        panel_id=panel.id,
        panel_type=panel.panel_type,
        panel_username=panel_user.username,
        subscription_url=subscription_url,
        config_text=config_text,
        data_gb=data_gb,
        expire_at=expire_at,
        status="active",
    )
    session.add(service)
    await session.flush()
    return service
