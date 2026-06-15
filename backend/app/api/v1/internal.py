from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import verify_internal_api_key
from app.database import get_db
from app.services.free_connect_service import provision_free_connect
from app.services.order_admin_service import approve_order, get_order, order_can_approve
from app.services.user_service_admin import delete_user_service
from pydantic import BaseModel, Field

router = APIRouter(prefix="/internal", tags=["internal"])


@router.post("/services/{service_id}/delete")
async def delete_service_for_user(
    service_id: int,
    telegram_user_id: int = Query(..., alias="telegramUserId"),
    _: None = Depends(verify_internal_api_key),
    db: AsyncSession = Depends(get_db),
):
    try:
        await delete_user_service(db, service_id, telegram_user_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return {"message": "سرویس حذف شد."}


@router.post("/orders/{order_id}/approve")
async def approve_order_internal(
    order_id: int,
    _: None = Depends(verify_internal_api_key),
    db: AsyncSession = Depends(get_db),
):
    order = await get_order(db, order_id)
    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="سفارش یافت نشد.")
    if not order_can_approve(order):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="سفارش قابل تأیید نیست.")
    try:
        await approve_order(db, order)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return {"message": "سفارش انجام شد."}


class FreeConnectBody(BaseModel):
    telegram_user_id: int = Field(alias="telegramUserId")
    requested_username: str = Field(alias="requestedUsername")

    model_config = {"populate_by_name": True}


@router.post("/free-connect")
async def free_connect_internal(
    body: FreeConnectBody,
    _: None = Depends(verify_internal_api_key),
    db: AsyncSession = Depends(get_db),
):
    try:
        service = await provision_free_connect(db, body.telegram_user_id, body.requested_username)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return {
        "message": "اتصال رایگان فعال شد.",
        "username": service.panel_username,
        "subscriptionUrl": service.subscription_url,
    }
