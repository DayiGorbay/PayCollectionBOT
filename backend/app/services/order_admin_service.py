from __future__ import annotations

import logging
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models.catalog import DiscountCode, Order
from app.models.telegram_user import TelegramUser
from app.services.discount_service import apply_discount_usage, record_transaction
from app.services.provision_service import provision_purchase_order
from app.services.telegram_notify import send_service_activation_message, send_telegram_text
from app.utils.jalali import format_jalali_datetime, format_rial

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
    created = format_jalali_datetime(order.created_at)
    return {
        "id": order.id,
        "user": order.user_label,
        "product": order.product_name,
        "amount": order.amount,
        "method": order.method,
        "date": created,
        "status": order.status,
        "orderType": "خرید سرویس" if order.order_type == "purchase" else "افزایش موجودی",
        "hasReceipt": bool(order.receipt_path) or order.wallet_paid_rial > 0,
    }


def order_to_detail(order: Order, receipt_url: str | None = None) -> dict:
    created = format_jalali_datetime(order.created_at)
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
        "hasReceipt": bool(order.receipt_path) or order.wallet_paid_rial > 0,
        "receiptUrl": receipt_url,
        "adminNote": order.admin_note,
        "discountCode": order.discount_code,
        "walletPaidRial": order.wallet_paid_rial,
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


def order_can_approve(order: Order) -> bool:
    if order.status != "در انتظار":
        return False
    if order.wallet_paid_rial > 0:
        return True
    return bool(order.receipt_path)


async def approve_order(session: AsyncSession, order: Order) -> Order:
    if order.status != "در انتظار":
        raise ValueError("این سفارش قبلاً پردازش شده است.")
    if not order_can_approve(order):
        raise ValueError("رسید پرداخت یا پرداخت کیف پول ثبت نشده است.")

    service = None
    now = datetime.now(timezone.utc)

    if order.order_type == "topup":
        result = await session.execute(
            select(TelegramUser).where(TelegramUser.telegram_id == order.telegram_user_id)
        )
        user = result.scalar_one_or_none()
        if user:
            user.balance = (user.balance or 0) + order.amount_rial
    elif order.order_type == "purchase":
        service = await provision_purchase_order(session, order)
        if order.discount_code:
            result = await session.execute(
                select(DiscountCode).where(DiscountCode.code == order.discount_code.upper())
            )
            discount_row = result.scalar_one_or_none()
            if discount_row:
                await apply_discount_usage(session, discount_row)
    else:
        raise ValueError("نوع سفارش نامعتبر است.")

    order.status = "موفق"
    order.processed_at = now
    if service is not None:
        order.service_id = service.id
    await record_transaction(session, order)
    await session.flush()

    await _notify_order_completion(order, service)
    return order


async def _notify_order_completion(order: Order, service) -> None:
    try:
        if order.order_type == "topup":
            await send_telegram_text(
                order.telegram_user_id,
                f"✅ سفارش #{order.id} (افزایش موجودی) تأیید شد.\n"
                f"مبلغ {order.amount} به کیف پول شما اضافه شد.",
            )
        elif service is not None:
            await send_service_activation_message(
                order.telegram_user_id,
                username=service.panel_username,
                data_gb=service.data_gb,
                subscription_url=service.subscription_url or "",
                config_text=service.config_text,
            )
    except Exception:
        logger.exception("order_notify_failed order_id=%s service_id=%s", order.id, getattr(service, "id", None))


async def reject_order(session: AsyncSession, order: Order, *, note: str | None = None) -> None:
    if order.status != "در انتظار":
        raise ValueError("این سفارش قبلاً پردازش شده است.")

    telegram_id = order.telegram_user_id
    order_id = order.id
    wallet_refund = order.wallet_paid_rial
    receipt_file = resolve_receipt_file(order)

    if wallet_refund > 0:
        result = await session.execute(select(TelegramUser).where(TelegramUser.telegram_id == telegram_id))
        user = result.scalar_one_or_none()
        if user:
            user.balance = (user.balance or 0) + wallet_refund

    await session.delete(order)
    await session.flush()

    if receipt_file and receipt_file.is_file():
        try:
            receipt_file.unlink()
        except OSError:
            pass

    refund_note = ""
    if wallet_refund > 0:
        refund_note = f"\nمبلغ {format_rial(wallet_refund)} به کیف پول شما بازگردانده شد."

    await send_telegram_text(
        telegram_id,
        f"❌ سفارش #{order_id} رد شد و از سیستم حذف گردید.{refund_note}\n"
        "در صورت واریز واقعی، با پشتیبانی تماس بگیرید.",
    )


async def block_user_by_telegram_id(session: AsyncSession, telegram_id: int) -> None:
    result = await session.execute(select(TelegramUser).where(TelegramUser.telegram_id == telegram_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise ValueError("کاربر یافت نشد.")
    user.is_blocked = True
    await session.flush()
    await send_telegram_text(telegram_id, "⛔️ حساب شما توسط مدیریت مسدود شد.")
