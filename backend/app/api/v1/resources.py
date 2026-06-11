from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_admin_role
from app.database import get_db
from app.models.admin_user import AdminUser
from app.models.catalog import DiscountCode, Order, Transaction
from app.services.panel_service import list_panels
from app.schemas.dashboard import DashboardSummaryOut
from app.services.dashboard_service import build_dashboard_summary, list_panel_users

router = APIRouter(tags=["resources"])


@router.get("/dashboard/summary", response_model=DashboardSummaryOut, response_model_by_alias=True)
async def dashboard_summary(
    _: AdminUser = Depends(require_admin_role),
    db: AsyncSession = Depends(get_db),
) -> DashboardSummaryOut:
    return await build_dashboard_summary(db)


@router.get("/users")
async def users(
    _: AdminUser = Depends(require_admin_role),
    db: AsyncSession = Depends(get_db),
):
    return await list_panel_users(db)




@router.get("/transactions")
async def transactions(_: AdminUser = Depends(require_admin_role), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Transaction).order_by(Transaction.id.desc()))
    rows = result.scalars().all()
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


@router.get("/panels")
async def panels(_: AdminUser = Depends(require_admin_role), db: AsyncSession = Depends(get_db)):
    items = await list_panels(db)
    return [item.model_dump(by_alias=True) for item in items]


@router.get("/discounts")
async def discounts(_: AdminUser = Depends(require_admin_role), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(DiscountCode).order_by(DiscountCode.id))
    rows = result.scalars().all()
    return [
        {
            "id": row.id,
            "code": row.code,
            "amount": row.amount,
            "type": row.type_label,
            "used": row.used_label,
            "validUntil": row.valid_until,
            "status": row.status,
        }
        for row in rows
    ]


@router.get("/settings")
async def settings(_: AdminUser = Depends(require_admin_role)):
    return {
        "profileName": "مجموعه پِی",
        "version": "1.0.0",
        "theme": "مشکی خالص",
        "activeTheme": "dark",
        "panels": ["تنظیمات", "پنل ها", "امنیت"],
    }
