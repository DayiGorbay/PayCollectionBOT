from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_admin_role
from app.database import get_db
from app.models.admin_user import AdminUser
from app.schemas.dashboard import DashboardSummaryOut
from app.services.bot_settings_service import get_all_settings, update_settings
from app.services.dashboard_service import build_dashboard_summary
from app.services.discount_service import (
    create_discount,
    delete_discount,
    discount_to_dict,
    list_transactions,
    transaction_stats,
    update_discount,
)
from app.services.free_connect_service import get_config, update_config
from app.services.panel_service import list_panels
from app.services.user_admin_service import list_panel_users, set_user_blocked
from app.models.catalog import DiscountCode
from sqlalchemy import select

router = APIRouter(tags=["resources"])


class BotSettingsUpdate(BaseModel):
    payment_card_number: str = Field(default="", alias="paymentCardNumber")
    payment_card_holder: str = Field(default="", alias="paymentCardHolder")
    channel_id: str = Field(default="", alias="channelId")
    channel_link: str = Field(default="", alias="channelLink")
    channel_username: str = Field(default="", alias="channelUsername")
    admin_telegram_id: str = Field(default="", alias="adminTelegramId")
    require_channel_join: str = Field(default="true", alias="requireChannelJoin")
    min_topup_rial: str = Field(default="10000", alias="minTopupRial")
    referral_daily_cap: str = Field(default="50", alias="referralDailyCap")
    log_level: str = Field(default="INFO", alias="logLevel")

    model_config = {"populate_by_name": True}


class FreeConnectUpdate(BaseModel):
    coins_required: int = Field(alias="coinsRequired")
    data_gb: int = Field(alias="dataGb")
    panel_id: int | None = Field(default=None, alias="panelId")
    duration_days: int = Field(alias="durationDays")
    is_active: bool = Field(default=True, alias="isActive")

    model_config = {"populate_by_name": True}


class DiscountCreate(BaseModel):
    code: str
    amount: str
    type: str
    valid_until: str = Field(default="—", alias="validUntil")
    max_uses: int = Field(default=0, alias="maxUses")
    status: str = "فعال"

    model_config = {"populate_by_name": True}


class DiscountUpdate(BaseModel):
    status: str | None = None
    valid_until: str | None = Field(default=None, alias="validUntil")
    max_uses: int | None = Field(default=None, alias="maxUses")

    model_config = {"populate_by_name": True}


class BlockUserBody(BaseModel):
    blocked: bool = True


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


@router.patch("/users/{user_id}/block")
async def block_user(
    user_id: int,
    body: BlockUserBody,
    _: AdminUser = Depends(require_admin_role),
    db: AsyncSession = Depends(get_db),
):
    try:
        return await set_user_blocked(db, user_id, body.blocked)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.get("/transactions")
async def transactions(_: AdminUser = Depends(require_admin_role), db: AsyncSession = Depends(get_db)):
    return await list_transactions(db)


@router.get("/transactions/stats")
async def transactions_stats(_: AdminUser = Depends(require_admin_role), db: AsyncSession = Depends(get_db)):
    stats = await transaction_stats(db)
    from app.utils.jalali import format_rial

    return {
        "totalRevenueLabel": format_rial(stats["totalRevenue"]),
        "totalCount": stats["totalCount"],
        "todayCount": stats["todayCount"],
    }


@router.get("/panels")
async def panels(_: AdminUser = Depends(require_admin_role), db: AsyncSession = Depends(get_db)):
    items = await list_panels(db)
    return [item.model_dump(by_alias=True) for item in items]


@router.get("/discounts")
async def discounts(_: AdminUser = Depends(require_admin_role), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(DiscountCode).order_by(DiscountCode.id.desc()))
    return [discount_to_dict(row) for row in result.scalars().all()]


@router.post("/discounts", status_code=status.HTTP_201_CREATED)
async def create_discount_endpoint(
    payload: DiscountCreate,
    _: AdminUser = Depends(require_admin_role),
    db: AsyncSession = Depends(get_db),
):
    try:
        row = await create_discount(db, payload.model_dump(by_alias=True))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return discount_to_dict(row)


@router.patch("/discounts/{discount_id}")
async def patch_discount(
    discount_id: int,
    payload: DiscountUpdate,
    _: AdminUser = Depends(require_admin_role),
    db: AsyncSession = Depends(get_db),
):
    try:
        row = await update_discount(db, discount_id, payload.model_dump(exclude_unset=True, by_alias=True))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return discount_to_dict(row)


@router.delete("/discounts/{discount_id}")
async def remove_discount(
    discount_id: int,
    _: AdminUser = Depends(require_admin_role),
    db: AsyncSession = Depends(get_db),
):
    try:
        await delete_discount(db, discount_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return {"message": "کد تخفیف حذف شد."}


@router.get("/bot-settings")
async def get_bot_settings(_: AdminUser = Depends(require_admin_role), db: AsyncSession = Depends(get_db)):
    settings = await get_all_settings(db)
    return {
        "paymentCardNumber": settings.get("payment_card_number", ""),
        "paymentCardHolder": settings.get("payment_card_holder", ""),
        "channelId": settings.get("channel_id", ""),
        "channelLink": settings.get("channel_link", ""),
        "channelUsername": settings.get("channel_username", ""),
        "adminTelegramId": settings.get("admin_telegram_id", ""),
        "requireChannelJoin": settings.get("require_channel_join", "true"),
        "minTopupRial": settings.get("min_topup_rial", "10000"),
        "referralDailyCap": settings.get("referral_daily_cap", "50"),
        "logLevel": settings.get("log_level", "INFO"),
    }


@router.put("/bot-settings")
async def put_bot_settings(
    payload: BotSettingsUpdate,
    _: AdminUser = Depends(require_admin_role),
    db: AsyncSession = Depends(get_db),
):
    values = {
        "payment_card_number": payload.payment_card_number,
        "payment_card_holder": payload.payment_card_holder,
        "channel_id": payload.channel_id,
        "channel_link": payload.channel_link,
        "channel_username": payload.channel_username,
        "admin_telegram_id": payload.admin_telegram_id,
        "require_channel_join": payload.require_channel_join,
        "min_topup_rial": payload.min_topup_rial,
        "referral_daily_cap": payload.referral_daily_cap,
        "log_level": payload.log_level,
    }
    await update_settings(db, values)
    return {"message": "تنظیمات ربات ذخیره شد."}


@router.get("/free-connect")
async def get_free_connect(_: AdminUser = Depends(require_admin_role), db: AsyncSession = Depends(get_db)):
    config = await get_config(db)
    return {
        "coinsRequired": config.coins_required,
        "dataGb": config.data_gb,
        "panelId": config.panel_id,
        "durationDays": config.duration_days,
        "isActive": config.is_active,
    }


@router.put("/free-connect")
async def put_free_connect(
    payload: FreeConnectUpdate,
    _: AdminUser = Depends(require_admin_role),
    db: AsyncSession = Depends(get_db),
):
    try:
        config = await update_config(
            db,
            coins_required=payload.coins_required,
            data_gb=payload.data_gb,
            panel_id=payload.panel_id,
            duration_days=payload.duration_days,
            is_active=payload.is_active,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return {
        "coinsRequired": config.coins_required,
        "dataGb": config.data_gb,
        "panelId": config.panel_id,
        "durationDays": config.duration_days,
        "isActive": config.is_active,
    }


@router.get("/settings")
async def settings(_: AdminUser = Depends(require_admin_role)):
    return {
        "profileName": "مجموعه پِی",
        "version": "1.0.0",
        "theme": "مشکی خالص",
        "activeTheme": "dark",
        "panels": ["تنظیمات", "پنل ها", "امنیت"],
    }
