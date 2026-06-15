from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_admin_role
from app.database import get_db
from app.models.admin_user import AdminUser
from app.schemas.panels import PanelCreate, PanelOut, PanelStatsOut, PanelTestResult, PanelUpdate
from app.services.panel_service import (
    create_panel,
    delete_panel,
    fetch_panel_inbounds,
    get_panel,
    get_panel_stats,
    list_panels,
    list_panels_stats,
    panel_to_out,
    test_panel_connection,
    test_panel_credentials,
    update_panel,
)

router = APIRouter(prefix="/panels", tags=["panels"])


@router.get("", response_model=list[PanelOut], response_model_by_alias=True)
async def get_panels(
    _: AdminUser = Depends(require_admin_role),
    db: AsyncSession = Depends(get_db),
):
    return await list_panels(db)


@router.get("/stats", response_model=list[PanelStatsOut], response_model_by_alias=True)
async def get_all_panels_stats(
    _: AdminUser = Depends(require_admin_role),
    db: AsyncSession = Depends(get_db),
):
    return await list_panels_stats(db)


@router.get("/{panel_id}/stats", response_model=PanelStatsOut, response_model_by_alias=True)
async def get_panel_stats_endpoint(
    panel_id: int,
    _: AdminUser = Depends(require_admin_role),
    db: AsyncSession = Depends(get_db),
):
    panel = await get_panel(db, panel_id)
    if panel is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="پنل یافت نشد.")
    return await get_panel_stats(db, panel)


@router.post("", response_model=PanelOut, response_model_by_alias=True, status_code=status.HTTP_201_CREATED)
async def post_panel(
    payload: PanelCreate,
    _: AdminUser = Depends(require_admin_role),
    db: AsyncSession = Depends(get_db),
):
    from app.services.panel_service import get_panel_by_code

    if await get_panel_by_code(db, payload.code_panel):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="کد پنل تکراری است.")

    try:
        panel = await create_panel(db, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return panel_to_out(panel)


@router.post("/preview-inbounds")
async def preview_inbounds(
    payload: PanelCreate,
    _: AdminUser = Depends(require_admin_role),
):
    return await fetch_panel_inbounds(payload)


@router.post("/test", response_model=PanelTestResult)
async def test_before_create(
    payload: PanelCreate,
    _: AdminUser = Depends(require_admin_role),
):
    return await test_panel_credentials(payload)


@router.post("/{panel_id}/test", response_model=PanelTestResult)
async def test_existing_panel(
    panel_id: int,
    _: AdminUser = Depends(require_admin_role),
    db: AsyncSession = Depends(get_db),
):
    panel = await get_panel(db, panel_id)
    if panel is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="پنل یافت نشد.")
    return await test_panel_connection(db, panel)


@router.patch("/{panel_id}", response_model=PanelOut, response_model_by_alias=True)
async def patch_panel(
    panel_id: int,
    payload: PanelUpdate,
    _: AdminUser = Depends(require_admin_role),
    db: AsyncSession = Depends(get_db),
):
    panel = await get_panel(db, panel_id)
    if panel is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="پنل یافت نشد.")
    panel = await update_panel(db, panel, payload)
    return panel_to_out(panel)


@router.delete("/{panel_id}")
async def remove_panel(
    panel_id: int,
    _: AdminUser = Depends(require_admin_role),
    db: AsyncSession = Depends(get_db),
):
    panel = await get_panel(db, panel_id)
    if panel is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="پنل یافت نشد.")
    await delete_panel(db, panel)
    return {"message": "پنل حذف شد."}
