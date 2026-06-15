from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_admin_role
from app.database import get_db
from app.models.admin_user import AdminUser
from app.schemas.services import ServiceDetailOut, ServiceListItem, ServiceSyncResult
from app.services.service_admin_service import (
    get_service_by_id,
    list_services,
    resolve_panel_name,
    resolve_product_name,
    resolve_user_label,
)
from app.services.service_sync_service import (
    fetch_panel_user,
    service_to_detail,
    service_to_list_item,
    sync_service_from_panel,
)

router = APIRouter(prefix="/services", tags=["services"])


async def _build_list_items(session: AsyncSession, rows) -> list[dict]:
    items: list[dict] = []
    for row in rows:
        items.append(
            service_to_list_item(
                row,
                user_label=await resolve_user_label(session, row.telegram_user_id),
                product_name=await resolve_product_name(session, row.product_id),
                panel_name=await resolve_panel_name(session, row.panel_id),
            )
        )
    return items


@router.get("", response_model=list[ServiceListItem], response_model_by_alias=True)
async def list_all_services(
    _: AdminUser = Depends(require_admin_role),
    db: AsyncSession = Depends(get_db),
):
    rows = await list_services(db)
    return await _build_list_items(db, rows)


@router.get("/user/{telegram_user_id}", response_model=list[ServiceListItem], response_model_by_alias=True)
async def list_user_services(
    telegram_user_id: int,
    _: AdminUser = Depends(require_admin_role),
    db: AsyncSession = Depends(get_db),
):
    rows = await list_services(db, telegram_user_id=telegram_user_id)
    return await _build_list_items(db, rows)


@router.get("/{service_id}", response_model=ServiceDetailOut, response_model_by_alias=True)
async def get_service_detail(
    service_id: int,
    _: AdminUser = Depends(require_admin_role),
    db: AsyncSession = Depends(get_db),
):
    service = await get_service_by_id(db, service_id)
    if service is None or service.status == "deleted":
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


@router.post("/{service_id}/sync", response_model=ServiceSyncResult, response_model_by_alias=True)
async def sync_service_cached(
    service_id: int,
    _: AdminUser = Depends(require_admin_role),
    db: AsyncSession = Depends(get_db),
):
    service = await get_service_by_id(db, service_id)
    if service is None or service.status == "deleted":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="سرویس یافت نشد.")
    await sync_service_from_panel(db, service, force=False)
    return ServiceSyncResult(id=service.id, synced=True, lastSyncedAt=service.last_synced_at)


@router.post("/{service_id}/refresh", response_model=ServiceDetailOut, response_model_by_alias=True)
async def refresh_service_live(
    service_id: int,
    _: AdminUser = Depends(require_admin_role),
    db: AsyncSession = Depends(get_db),
):
    service = await get_service_by_id(db, service_id)
    if service is None or service.status == "deleted":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="سرویس یافت نشد.")

    await sync_service_from_panel(db, service, force=True)
    panel_user = await fetch_panel_user(db, service)
    return service_to_detail(
        service,
        user_label=await resolve_user_label(db, service.telegram_user_id),
        product_name=await resolve_product_name(db, service.product_id),
        panel_name=await resolve_panel_name(db, service.panel_id),
        panel_user=panel_user,
        live_from_panel=True,
    )
