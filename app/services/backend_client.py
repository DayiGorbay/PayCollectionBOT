from __future__ import annotations

import logging

import httpx

from app.config import settings

logger = logging.getLogger(__name__)


async def delete_user_service_via_api(service_id: int, telegram_user_id: int) -> None:
    if not settings.INTERNAL_API_KEY:
        raise RuntimeError("INTERNAL_API_KEY تنظیم نشده است.")

    url = f"{settings.BACKEND_API_URL.rstrip('/')}/internal/services/{service_id}/delete"
    headers = {"X-Internal-Api-Key": settings.INTERNAL_API_KEY}
    params = {"telegramUserId": telegram_user_id}

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(url, headers=headers, params=params)

    if response.status_code >= 400:
        detail = response.text
        try:
            detail = response.json().get("detail", detail)
        except Exception:
            pass
        raise RuntimeError(str(detail))
