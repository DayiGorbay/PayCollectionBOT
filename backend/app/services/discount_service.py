from __future__ import annotations

import re
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.catalog import DiscountCode, Order, Transaction
from app.utils.jalali import format_jalali_datetime, format_rial


def _parse_used_label(value: str) -> tuple[int, int | None]:
    match = re.match(r"^(\d+)/(.+)$", value.strip())
    if not match:
        return 0, None
    used = int(match.group(1))
    cap_raw = match.group(2)
    if cap_raw in {"∞", "inf", "unlimited"}:
        return used, None
    if cap_raw.isdigit():
        return used, int(cap_raw)
    return used, None


def discount_to_dict(row: DiscountCode) -> dict:
    used, cap = _parse_used_label(row.used_label)
    if row.used_count:
        used = row.used_count
    max_uses = row.max_uses or cap
    used_label = f"{used}/{max_uses}" if max_uses else f"{used}/∞"
    return {
        "id": row.id,
        "code": row.code,
        "amount": row.amount,
        "type": row.type_label,
        "used": used_label,
        "validUntil": row.valid_until,
        "status": row.status,
        "discountPercent": row.discount_percent,
        "discountAmountRial": row.discount_amount_rial,
        "maxUses": row.max_uses,
        "usedCount": row.used_count or used,
    }


def calculate_discount(row: DiscountCode, amount_rial: int) -> int:
    if row.type_label == "درصدی":
        percent = row.discount_percent
        if percent is None:
            digits = re.sub(r"\D", "", row.amount)
            percent = int(digits) if digits else 0
        return min(amount_rial, amount_rial * percent // 100)
    fixed = row.discount_amount_rial
    if fixed is None:
        digits = re.sub(r"\D", "", row.amount)
        fixed = int(digits) if digits else 0
    return min(amount_rial, fixed)


async def validate_discount(session: AsyncSession, code: str, amount_rial: int) -> tuple[DiscountCode, int]:
    normalized = code.strip().upper()
    result = await session.execute(select(DiscountCode).where(DiscountCode.code == normalized))
    row = result.scalar_one_or_none()
    if row is None:
        raise ValueError("کد تخفیف یافت نشد.")
    if row.status != "فعال":
        raise ValueError("کد تخفیف غیرفعال است.")
    if row.max_uses and row.used_count >= row.max_uses:
        raise ValueError("سقف استفاده از این کد تکمیل شده است.")

    discount_rial = calculate_discount(row, amount_rial)
    if discount_rial <= 0:
        raise ValueError("کد تخفیف برای این مبلغ قابل اعمال نیست.")
    return row, discount_rial


async def apply_discount_usage(session: AsyncSession, row: DiscountCode) -> None:
    row.used_count = (row.used_count or 0) + 1
    max_uses = row.max_uses or None
    used_label = f"{row.used_count}/{max_uses}" if max_uses else f"{row.used_count}/∞"
    row.used_label = used_label
    await session.flush()


async def create_discount(session: AsyncSession, payload: dict) -> DiscountCode:
    code = payload["code"].strip().upper()
    existing = await session.execute(select(DiscountCode).where(DiscountCode.code == code))
    if existing.scalar_one_or_none():
        raise ValueError("کد تخفیف تکراری است.")

    type_label = payload["type"]
    amount_label = payload["amount"]
    if type_label == "درصدی":
        percent = int(re.sub(r"\D", "", str(payload.get("amount", "0"))))
        amount_label = f"{percent}%"
        discount_percent = percent
        discount_amount_rial = None
    else:
        rial = int(re.sub(r"\D", "", str(payload.get("amount", "0"))))
        amount_label = format_rial(rial)
        discount_percent = None
        discount_amount_rial = rial

    max_uses = int(payload.get("maxUses") or payload.get("max_use") or 0)
    row = DiscountCode(
        code=code,
        amount=amount_label,
        type_label=type_label,
        used_label=f"0/{max_uses}" if max_uses else "0/∞",
        valid_until=payload.get("validUntil") or payload.get("valid_until") or "—",
        status=payload.get("status") or "فعال",
        discount_percent=discount_percent,
        discount_amount_rial=discount_amount_rial,
        max_uses=max_uses,
        used_count=0,
    )
    session.add(row)
    await session.flush()
    return row


async def update_discount(session: AsyncSession, discount_id: int, payload: dict) -> DiscountCode:
    row = await session.get(DiscountCode, discount_id)
    if row is None:
        raise ValueError("کد تخفیف یافت نشد.")
    if "status" in payload:
        row.status = payload["status"]
    if "validUntil" in payload:
        row.valid_until = payload["validUntil"]
    if "maxUses" in payload:
        row.max_uses = int(payload["maxUses"])
    await session.flush()
    return row


async def delete_discount(session: AsyncSession, discount_id: int) -> None:
    row = await session.get(DiscountCode, discount_id)
    if row is None:
        raise ValueError("کد تخفیف یافت نشد.")
    await session.delete(row)


async def record_transaction(session: AsyncSession, order: Order) -> Transaction:
    tx = Transaction(
        status=order.status,
        user_label=order.user_label,
        hash_value=f"ORD-{order.id}",
        amount=order.amount,
        method=order.method,
        date_label=format_jalali_datetime(order.processed_at or order.created_at),
        type_label="خرید سرویس" if order.order_type == "purchase" else "افزایش موجودی",
        panel=order.product_name,
    )
    session.add(tx)
    await session.flush()
    return tx


async def list_transactions(session: AsyncSession) -> list[dict]:
    result = await session.execute(select(Transaction).order_by(Transaction.id.desc()))
    rows = result.scalars().all()
    if rows:
        return [
            {
                "id": row.id,
                "status": row.status,
                "user": row.user_label,
                "hash": row.hash_value,
                "amount": row.amount,
                "method": row.method,
                "date": row.date_label,
                "type": row.type_label,
                "panel": row.panel,
            }
            for row in rows
        ]

    orders_result = await session.execute(
        select(Order).where(Order.status == "موفق").order_by(Order.id.desc()).limit(500)
    )
    return [
        {
            "id": order.id,
            "status": order.status,
            "user": order.user_label,
            "hash": f"ORD-{order.id}",
            "amount": order.amount,
            "method": order.method,
            "date": format_jalali_datetime(order.processed_at or order.created_at),
            "type": "خرید سرویس" if order.order_type == "purchase" else "افزایش موجودی",
            "panel": order.product_name,
        }
        for order in orders_result.scalars().all()
    ]


async def transaction_stats(session: AsyncSession) -> dict:
    total_count = await session.scalar(select(func.count()).select_from(Transaction)) or 0
    if total_count == 0:
        total_count = await session.scalar(
            select(func.count()).select_from(Order).where(Order.status == "موفق")
        ) or 0
    total_revenue = await session.scalar(
        select(func.coalesce(func.sum(Order.amount_rial), 0)).where(Order.status == "موفق")
    ) or 0
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    today_count = await session.scalar(
        select(func.count()).select_from(Order).where(
            Order.status == "موفق",
            Order.processed_at >= today_start,
        )
    ) or 0
    return {
        "totalRevenue": int(total_revenue),
        "totalCount": int(total_count),
        "todayCount": int(today_count),
    }
