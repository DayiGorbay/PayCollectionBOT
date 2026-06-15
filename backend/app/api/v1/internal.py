from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import verify_internal_api_key
from app.database import get_db
from app.services.free_connect_service import provision_free_connect
from app.services.order_admin_service import approve_order, get_order, order_can_approve
from app.services.service_admin_service import get_service_by_id, list_services, resolve_panel_name, resolve_product_name, resolve_user_label
from app.services.service_sync_service import fetch_panel_user, service_to_detail, service_to_list_item, sync_service_from_panel
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


@router.get("/users/{telegram_user_id}/services")
async def list_services_for_bot_user(
    telegram_user_id: int,
    _: None = Depends(verify_internal_api_key),
    db: AsyncSession = Depends(get_db),
):
    rows = await list_services(db, telegram_user_id=telegram_user_id)
    items = []
    for row in rows:
        items.append(
            service_to_list_item(
                row,
                user_label=await resolve_user_label(db, row.telegram_user_id),
                product_name=await resolve_product_name(db, row.product_id),
                panel_name=await resolve_panel_name(db, row.panel_id),
            )
        )
    return items


@router.get("/services/{service_id}")
async def get_service_for_bot_user(
    service_id: int,
    telegram_user_id: int = Query(..., alias="telegramUserId"),
    _: None = Depends(verify_internal_api_key),
    db: AsyncSession = Depends(get_db),
):
    service = await get_service_by_id(db, service_id)
    if service is None or service.status == "deleted" or service.telegram_user_id != telegram_user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="سرویس یافت نشد.")

    panel_user = None
    live = False
    try:
        await sync_service_from_panel(db, service, force=True)
        panel_user = await fetch_panel_user(db, service)
        live = True
    except Exception:
        panel_user = None

    return service_to_detail(
        service,
        user_label=await resolve_user_label(db, service.telegram_user_id),
        product_name=await resolve_product_name(db, service.product_id),
        panel_name=await resolve_panel_name(db, service.panel_id),
        panel_user=panel_user,
        live_from_panel=live,
    )


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
