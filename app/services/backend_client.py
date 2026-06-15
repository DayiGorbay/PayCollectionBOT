from __future__ import annotations

import httpx

from app.config import settings


async def free_connect_via_api(telegram_user_id: int, requested_username: str) -> dict:
    if not settings.INTERNAL_API_KEY:
        raise RuntimeError("INTERNAL_API_KEY تنظیم نشده است.")

    url = f"{settings.BACKEND_API_URL.rstrip('/')}/internal/free-connect"
    headers = {"X-Internal-Api-Key": settings.INTERNAL_API_KEY}

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            url,
            headers=headers,
            json={"telegramUserId": telegram_user_id, "requestedUsername": requested_username},
        )

    if response.status_code >= 400:
        detail = response.text
        try:
            detail = response.json().get("detail", detail)
        except Exception:
            pass
        raise RuntimeError(str(detail))
    return response.json()


async def approve_order_via_api(order_id: int) -> None:
    if not settings.INTERNAL_API_KEY:
        raise RuntimeError("INTERNAL_API_KEY تنظیم نشده است.")

    url = f"{settings.BACKEND_API_URL.rstrip('/')}/internal/orders/{order_id}/approve"
    headers = {"X-Internal-Api-Key": settings.INTERNAL_API_KEY}

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(url, headers=headers)

    if response.status_code >= 400:
        detail = response.text
        try:
            detail = response.json().get("detail", detail)
        except Exception:
            pass
        raise RuntimeError(str(detail))
