from __future__ import annotations

import httpx

from app.config import settings


def _internal_headers() -> dict[str, str]:
    if not settings.INTERNAL_API_KEY:
        raise RuntimeError("INTERNAL_API_KEY تنظیم نشده است.")
    return {"X-Internal-Api-Key": settings.INTERNAL_API_KEY}


def _api_url(path: str) -> str:
    return f"{settings.BACKEND_API_URL.rstrip('/')}{path}"


def _raise_on_error(response: httpx.Response) -> None:
    if response.status_code < 400:
        return
    detail = response.text
    try:
        detail = response.json().get("detail", detail)
    except Exception:
        pass
    raise RuntimeError(str(detail))


async def _post(
    path: str,
    *,
    json: dict | None = None,
    params: dict | None = None,
) -> httpx.Response:
    async with httpx.AsyncClient(timeout=60.0) as client:
        return await client.post(
            _api_url(path),
            headers=_internal_headers(),
            json=json,
            params=params,
        )


async def free_connect_via_api(telegram_user_id: int, requested_username: str) -> dict:
    response = await _post(
        "/internal/free-connect",
        json={"telegramUserId": telegram_user_id, "requestedUsername": requested_username},
    )
    _raise_on_error(response)
    return response.json()


async def approve_order_via_api(order_id: int) -> None:
    response = await _post(f"/internal/orders/{order_id}/approve")
    _raise_on_error(response)


async def delete_user_service_via_api(service_id: int, telegram_user_id: int) -> None:
    response = await _post(
        f"/internal/services/{service_id}/delete",
        params={"telegramUserId": telegram_user_id},
    )
    _raise_on_error(response)
