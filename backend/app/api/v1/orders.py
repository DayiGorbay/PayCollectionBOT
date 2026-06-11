from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_admin_role
from app.config import get_settings
from app.database import get_db
from app.models.admin_user import AdminUser
from app.models.catalog import Order
from app.schemas.orders import OrderDetailOut, OrderListItem
from app.services.order_admin_service import (
    approve_order,
    get_order,
    order_to_detail,
    order_to_list_item,
    reject_order,
    resolve_receipt_file,
)

router = APIRouter(prefix="/orders", tags=["orders"])


@router.get("", response_model=list[OrderListItem], response_model_by_alias=True)
async def list_orders(
    _: AdminUser = Depends(require_admin_role),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Order).order_by(Order.id.desc()))
    return [order_to_list_item(row) for row in result.scalars().all()]


@router.get("/{order_id}", response_model=OrderDetailOut, response_model_by_alias=True)
async def get_order_detail(
    order_id: int,
    _: AdminUser = Depends(require_admin_role),
    db: AsyncSession = Depends(get_db),
):
    order = await get_order(db, order_id)
    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="سفارش یافت نشد.")

    settings = get_settings()
    receipt_url = None
    if order.receipt_path:
        receipt_url = f"{settings.API_V1_PREFIX}/orders/{order.id}/receipt"

    return order_to_detail(order, receipt_url=receipt_url)


@router.get("/{order_id}/receipt")
async def get_order_receipt(
    order_id: int,
    _: AdminUser = Depends(require_admin_role),
    db: AsyncSession = Depends(get_db),
):
    order = await get_order(db, order_id)
    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="سفارش یافت نشد.")

    file_path = resolve_receipt_file(order)
    if file_path is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="رسید یافت نشد.")

    return FileResponse(file_path, media_type="image/jpeg", filename=f"receipt_{order_id}.jpg")


@router.post("/{order_id}/approve", response_model=OrderDetailOut, response_model_by_alias=True)
async def approve_order_endpoint(
    order_id: int,
    _: AdminUser = Depends(require_admin_role),
    db: AsyncSession = Depends(get_db),
):
    order = await get_order(db, order_id)
    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="سفارش یافت نشد.")
    if not order.receipt_path:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="رسید هنوز ارسال نشده است.")

    try:
        order = await approve_order(db, order)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    settings = get_settings()
    receipt_url = f"{settings.API_V1_PREFIX}/orders/{order.id}/receipt" if order.receipt_path else None
    return order_to_detail(order, receipt_url=receipt_url)


@router.post("/{order_id}/reject")
async def reject_order_endpoint(
    order_id: int,
    _: AdminUser = Depends(require_admin_role),
    db: AsyncSession = Depends(get_db),
):
    order = await get_order(db, order_id)
    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="سفارش یافت نشد.")

    try:
        await reject_order(db, order)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return {"message": "سفارش رد و حذف شد."}
