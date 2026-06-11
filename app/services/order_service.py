from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.order import Order
from app.models.user import User


def user_display_label(user: User, telegram_username: str | None = None) -> str:
    if telegram_username:
        return telegram_username.lstrip("@")
    if user.username:
        return user.username
    parts = [user.first_name or "", user.last_name or ""]
    name = " ".join(p for p in parts if p).strip()
    return name or str(user.telegram_id)


async def get_pending_order(session: AsyncSession, telegram_id: int) -> Order | None:
    result = await session.execute(
        select(Order).where(
            Order.telegram_user_id == telegram_id,
            Order.status == "در انتظار",
        )
    )
    return result.scalar_one_or_none()


async def create_purchase_order(
    session: AsyncSession,
    *,
    telegram_id: int,
    user_label: str,
    product_id: int,
    product_name: str,
    amount_label: str,
    amount_rial: int,
    requested_username: str,
) -> Order:
    order = Order(
        telegram_user_id=telegram_id,
        user_label=user_label,
        order_type="purchase",
        product_id=product_id,
        product_name=product_name,
        requested_username=requested_username,
        amount=amount_label,
        amount_rial=amount_rial,
        status="در انتظار",
    )
    session.add(order)
    await session.commit()
    await session.refresh(order)
    return order


async def create_topup_order(
    session: AsyncSession,
    *,
    telegram_id: int,
    user_label: str,
    amount_rial: int,
) -> Order:
    from app.utils.files import format_rial

    order = Order(
        telegram_user_id=telegram_id,
        user_label=user_label,
        order_type="topup",
        product_id=None,
        product_name="افزایش موجودی",
        amount=format_rial(amount_rial),
        amount_rial=amount_rial,
        status="در انتظار",
    )
    session.add(order)
    await session.commit()
    await session.refresh(order)
    return order


async def attach_receipt(
    session: AsyncSession,
    order: Order,
    *,
    receipt_path: str,
    receipt_file_id: str,
) -> Order:
    order.receipt_path = receipt_path
    order.receipt_file_id = receipt_file_id
    await session.commit()
    await session.refresh(order)
    return order


async def cancel_pending_order(session: AsyncSession, order: Order) -> None:
    await session.delete(order)
    await session.commit()
