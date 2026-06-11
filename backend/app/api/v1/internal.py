from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import verify_internal_api_key
from app.database import get_db
from app.services.user_service_admin import delete_user_service

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
