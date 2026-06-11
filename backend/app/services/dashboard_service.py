from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.catalog import DiscountCode, Order, Panel
from app.models.telegram_user import TelegramUser
from app.schemas.dashboard import ActiveCouponOut, DashboardSummaryOut, RecentOrderOut


def _user_display_name(user: TelegramUser) -> str:
    if user.username:
        return user.username
    parts = [user.first_name or "", user.last_name or ""]
    name = " ".join(p for p in parts if p).strip()
    return name or str(user.telegram_id)


def _user_status(user: TelegramUser) -> str:
    if user.is_suspicious:
        return "در انتظار"
    if not user.verified:
        return "در انتظار"
    if user.referral_finalized or user.coins > 0:
        return "فعال"
    return "فعال"


async def list_panel_users(session: AsyncSession) -> list[dict]:
    result = await session.execute(select(TelegramUser).order_by(TelegramUser.id.desc()).limit(500))
    users = result.scalars().all()
    rows = []
    for user in users:
        rows.append(
            {
                "id": user.id,
                "name": _user_display_name(user),
                "plan": f"زیرمجموعه: {user.invited_count}",
                "volume": f"{user.coins} کوین",
                "expiry": user.created_at.strftime("%Y/%m/%d") if user.created_at else "-",
                "status": _user_status(user),
            }
        )
    return rows


async def build_dashboard_summary(session: AsyncSession) -> DashboardSummaryOut:
    total_users = await session.scalar(select(func.count()).select_from(TelegramUser)) or 0
    active_users = await session.scalar(
        select(func.count()).select_from(TelegramUser).where(
            TelegramUser.verified.is_(True),
            TelegramUser.is_suspicious.is_(False),
        )
    ) or 0

    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    today_users = await session.scalar(
        select(func.count()).select_from(TelegramUser).where(TelegramUser.created_at >= today_start)
    ) or 0

    pending_orders = await session.scalar(
        select(func.count()).select_from(Order).where(Order.status == "در انتظار")
    ) or 0
    active_panels = await session.scalar(
        select(func.count()).select_from(Panel).where(Panel.status == "فعال")
    ) or 0

    coupons_result = await session.execute(
        select(DiscountCode).where(DiscountCode.status == "فعال").order_by(DiscountCode.id).limit(5)
    )
    active_coupons = [
        ActiveCouponOut(
            id=c.id,
            code=c.code,
            type=c.type_label,
            amount=_parse_amount(c.amount),
            validUntil=c.valid_until,
        )
        for c in coupons_result.scalars().all()
    ]

    orders_result = await session.execute(select(Order).order_by(Order.id.desc()).limit(4))
    recent_orders = [
        RecentOrderOut(
            id=o.id,
            user=o.user_label,
            product=o.product_name,
            amount=o.amount,
            status=o.status,
            date=o.created_at.strftime("%Y/%m/%d") if o.created_at else "—",
        )
        for o in orders_result.scalars().all()
    ]

    total_revenue = await session.scalar(
        select(func.coalesce(func.sum(Order.amount_rial), 0)).where(Order.status == "موفق")
    )
    total_revenue = int(total_revenue or 0)

    return DashboardSummaryOut(
        total_users=total_users,
        active_users=active_users,
        today_users=today_users,
        total_revenue=total_revenue,
        pending_orders=pending_orders,
        active_panels=active_panels,
        active_coupons=active_coupons,
        recent_orders=recent_orders,
    )


def _parse_amount(value: str) -> int | float:
    digits = "".join(ch for ch in value if ch.isdigit())
    if not digits:
        return 0
    if "%" in value:
        return int(digits)
    return int(digits)
