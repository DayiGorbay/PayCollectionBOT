from __future__ import annotations

import logging
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models.catalog import Order
from app.models.telegram_user import TelegramUser
from app.services.provision_service import provision_purchase_order
from app.services.telegram_notify import send_service_activation_message, send_telegram_text

logger = logging.getLogger(__name__)


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def uploads_dir() -> Path:
    settings = get_settings()
    path = Path(settings.UPLOADS_DIR)
    if path.is_absolute():
        return path
    return (_repo_root() / path).resolve()


def order_to_list_item(order: Order) -> dict:
    created = order.created_at.strftime("%Y/%m/%d %H:%M") if order.created_at else "—"
    return {
        "id": order.id,
        "user": order.user_label,
        "product": order.product_name,
        "amount": order.amount,
        "method": order.method,
        "date": created,
        "status": order.status,
        "orderType": "خرید سرویس" if order.order_type == "purchase" else "افزایش موجودی",
        "hasReceipt": bool(order.receipt_path),
    }


def order_to_detail(order: Order, receipt_url: str | None = None) -> dict:
    created = order.created_at.strftime("%Y/%m/%d %H:%M") if order.created_at else "—"
    return {
        "id": order.id,
        "user": order.user_label,
        "telegramUserId": order.telegram_user_id,
        "product": order.product_name,
        "amount": order.amount,
        "amountRial": order.amount_rial,
        "method": order.method,
        "date": created,
        "status": order.status,
        "orderType": "خرید سرویس" if order.order_type == "purchase" else "افزایش موجودی",
        "hasReceipt": bool(order.receipt_path),
        "receiptUrl": receipt_url,
        "adminNote": order.admin_note,
    }


async def get_order(session: AsyncSession, order_id: int) -> Order | None:
    result = await session.execute(select(Order).where(Order.id == order_id))
    return result.scalar_one_or_none()


def resolve_receipt_file(order: Order) -> Path | None:
    if not order.receipt_path:
        return None
    path = Path(order.receipt_path)
    if path.is_file():
        return path
    alt = uploads_dir() / f"order_{order.id}.jpg"
    return alt if alt.is_file() else None


async def approve_order(session: AsyncSession, order: Order) -> Order:
    if order.status != "در انتظار":
        raise ValueError("این سفارش قبلاً پردازش شده است.")

    now = datetime.now(timezone.utc)
    order.status = "موفق"
    order.processed_at = now

    if order.order_type == "topup":
        result = await session.execute(
            select(TelegramUser).where(TelegramUser.telegram_id == order.telegram_user_id)
        )
        user = result.scalar_one_or_none()
        if user:
            user.balance = (user.balance or 0) + order.amount_rial

    await session.flush()

    if order.order_type == "topup":
        msg = (
            f"✅ سفارش #{order.id} (افزایش موجودی) تأیید شد.\n"
            f"مبلغ {order.amount} به کیف پول شما اضافه شد."
        )
        await send_telegram_text(order.telegram_user_id, msg)
    else:
        service = await provision_purchase_order(session, order)
        await send_service_activation_message(
            order.telegram_user_id,
            username=service.panel_username,
            data_gb=service.data_gb,
            subscription_url=service.subscription_url or "",
            config_text=service.config_text,
        )

    return order


async def reject_order(session: AsyncSession, order: Order, *, note: str | None = None) -> None:
    if order.status != "در انتظار":
        raise ValueError("این سفارش قبلاً پردازش شده است.")

    telegram_id = order.telegram_user_id
    order_id = order.id
    receipt_file = resolve_receipt_file(order)

    await session.delete(order)
    await session.flush()

    if receipt_file and receipt_file.is_file():
        try:
            receipt_file.unlink()
        except OSError:
            pass

    await send_telegram_text(
        telegram_id,
        f"❌ سفارش #{order_id} رد شد و از سیستم حذف گردید.\n"
        "در صورت واریز واقعی، با پشتیبانی تماس بگیرید.",
    )
