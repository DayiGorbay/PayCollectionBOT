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
from app.services.service_admin_service import (
    create_panel_user_idempotent,
    get_service_by_order_id,
    persist_service_from_panel_user,
)

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
    PostgreSQL = Source of Truth.
    1) Idempotent: اگر سرویس برای این سفارش وجود دارد، همان برگردانده می‌شود.
    2) ساخت/بازیابی کاربر در پنل (Marzban/XUI)
    3) ذخیره Service در DB قبل از هر اعلان
    """
    if order.order_type != "purchase":
        raise ValueError("فقط سفارش خرید سرویس قابل ساخت است.")
    if not order.product_id:
        raise ValueError("محصول سفارش مشخص نیست.")
    if not order.requested_username:
        raise ValueError("نام کاربری سفارش ثبت نشده است.")

    existing = await get_service_by_order_id(session, order.id)
    if existing is not None and existing.status != "deleted":
        logger.info("provision_idempotent order_id=%s service_id=%s", order.id, existing.id)
        order.service_id = existing.id
        return existing

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
    panel_username = sanitize_username(f"{order.requested_username}_{order.id}")[:32] or f"order{order.id}"

    data_gb = parse_data_gb(product.size)
    data_limit = _data_limit_bytes(data_gb)
    now = datetime.now(timezone.utc)
    expire_at = now + timedelta(days=product.duration_days)

    try:
        panel_user = await create_panel_user_idempotent(
            provider,
            PanelUserCreate(
                username=panel_username,
                data_limit_bytes=data_limit,
                expire_at=expire_at,
                note=f"order:{order.id}",
            ),
        )
    except PanelError as exc:
        logger.exception(
            "provision_failed order_id=%s panel_id=%s product_id=%s",
            order.id,
            panel.id,
            product.id,
        )
        raise ValueError(str(exc)) from exc

    service = await persist_service_from_panel_user(
        session,
        telegram_user_id=order.telegram_user_id,
        order=order,
        product=product,
        panel=panel,
        panel_user=panel_user,
        data_gb=data_gb,
        expire_at=expire_at,
    )
    logger.info(
        "provision_saved order_id=%s service_id=%s username=%s",
        order.id,
        service.id,
        service.panel_username,
    )
    return service
