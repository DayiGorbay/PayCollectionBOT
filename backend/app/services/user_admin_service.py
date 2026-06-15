from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.catalog import Order
from app.models.telegram_user import TelegramUser
from app.utils.jalali import format_jalali_datetime, format_rial


def _display_name(user: TelegramUser) -> str:
    parts = [user.first_name or "", user.last_name or ""]
    name = " ".join(p for p in parts if p).strip()
    return name or "بدون نام"


def _verification_status(user: TelegramUser) -> str:
    if user.is_blocked:
        return "مسدود"
    if user.verified and not user.is_suspicious:
        return "احراز شده"
    return "احراز نشده"


async def list_panel_users(session: AsyncSession) -> list[dict]:
    result = await session.execute(select(TelegramUser).order_by(TelegramUser.id.desc()).limit(500))
    users = result.scalars().all()
    rows = []
    for user in users:
        orders_result = await session.execute(
            select(Order).where(
                Order.telegram_user_id == user.telegram_id,
                Order.status == "موفق",
            ).order_by(Order.id.desc())
        )
        orders = orders_result.scalars().all()
        total_spent = sum(order.amount_rial for order in orders)
        purchase_history = ", ".join(order.product_name for order in orders[:5]) or "—"
        rows.append(
            {
                "id": user.id,
                "telegramId": user.telegram_id,
                "name": _display_name(user),
                "username": user.username or "—",
                "phone": user.phone_number or "—",
                "purchaseHistory": purchase_history,
                "totalSpent": format_rial(total_spent),
                "totalSpentRial": total_spent,
                "registeredAt": format_jalali_datetime(user.created_at, with_time=False),
                "status": _verification_status(user),
                "isBlocked": user.is_blocked,
                "balance": format_rial(user.balance or 0),
                "coins": user.coins,
            }
        )
    return rows


async def set_user_blocked(session: AsyncSession, user_id: int, blocked: bool) -> dict:
    user = await session.get(TelegramUser, user_id)
    if user is None:
        raise ValueError("کاربر یافت نشد.")
    user.is_blocked = blocked
    await session.flush()
    return {
        "id": user.id,
        "isBlocked": user.is_blocked,
        "status": _verification_status(user),
    }
