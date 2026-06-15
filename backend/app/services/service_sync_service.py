from __future__ import annotations

import json
import logging
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.catalog import UserService
from app.providers.factory import create_provider
from app.providers.models import PanelUser
from app.repositories.panel_repository import PanelRepository

logger = logging.getLogger(__name__)

SYNC_CACHE_SECONDS = 120


def _extract_online_status(raw: dict) -> str | None:
    for key in ("online", "is_online", "online_status"):
        value = raw.get(key)
        if value is not None:
            return "online" if bool(value) else "offline"
    return None


def _extract_last_online(raw: dict) -> datetime | None:
    for key in ("online_at", "last_online", "sub_last_user_agent", "last_seen"):
        value = raw.get(key)
        if value is None:
            continue
        if isinstance(value, (int, float)) and value > 0:
            try:
                return datetime.fromtimestamp(value, tz=timezone.utc)
            except (OSError, ValueError):
                continue
        if isinstance(value, str):
            try:
                return datetime.fromisoformat(value.replace("Z", "+00:00"))
            except ValueError:
                continue
    return None


def _parse_inbounds_cache(raw: str | None) -> dict | list | None:
    if not raw:
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return None


def compute_days_remaining(expire_at: datetime | None) -> int | None:
    if expire_at is None:
        return None
    now = datetime.now(timezone.utc)
    expire = expire_at if expire_at.tzinfo else expire_at.replace(tzinfo=timezone.utc)
    delta = expire - now
    return max(0, delta.days)


def apply_panel_user_to_service(service: UserService, panel_user: PanelUser) -> None:
    now = datetime.now(timezone.utc)
    limit = panel_user.data_limit_bytes
    used = panel_user.used_traffic_bytes or 0

    service.panel_username = panel_user.username
    service.used_traffic_bytes = used
    service.data_limit_bytes = limit
    service.remaining_traffic_bytes = max(0, limit - used) if limit is not None else None
    service.panel_user_status = panel_user.status
    if panel_user.expire_at is not None:
        service.expire_at = panel_user.expire_at
    if panel_user.subscription_url:
        service.subscription_url = panel_user.subscription_url
    if panel_user.links:
        service.config_text = panel_user.links[0]
    if limit is not None:
        service.data_gb = max(1, int(limit / (1024**3)))

    raw = panel_user.raw or {}
    service.online_status = _extract_online_status(raw)
    service.last_online_at = _extract_last_online(raw)
    inbounds = raw.get("inbounds")
    if inbounds is not None:
        service.inbounds_cache = json.dumps(inbounds, ensure_ascii=False)

    service.last_synced_at = now
    service.updated_at = now


def needs_sync(service: UserService, *, force: bool = False) -> bool:
    if force:
        return True
    if service.last_synced_at is None:
        return True
    synced = service.last_synced_at
    if synced.tzinfo is None:
        synced = synced.replace(tzinfo=timezone.utc)
    age = (datetime.now(timezone.utc) - synced).total_seconds()
    return age >= SYNC_CACHE_SECONDS


async def fetch_panel_user(session: AsyncSession, service: UserService) -> PanelUser:
    if not service.panel_id:
        raise ValueError("پنل سرویس تنظیم نشده است.")
    panel_repo = PanelRepository(session)
    panel = await panel_repo.get_by_id(service.panel_id)
    if panel is None:
        raise ValueError("پنل سرویس یافت نشد.")
    provider = create_provider(panel, session)
    return await provider.get_user(service.panel_username)


async def sync_service_from_panel(
    session: AsyncSession,
    service: UserService,
    *,
    force: bool = False,
) -> UserService:
    if service.status == "deleted":
        return service
    if not needs_sync(service, force=force):
        logger.debug("service_sync_skipped service_id=%s (cache valid)", service.id)
        return service

    try:
        panel_user = await fetch_panel_user(session, service)
        apply_panel_user_to_service(service, panel_user)
        await session.flush()
        logger.info("service_synced service_id=%s username=%s", service.id, service.panel_username)
    except Exception as exc:
        logger.warning(
            "service_sync_failed service_id=%s username=%s error=%s",
            service.id,
            service.panel_username,
            exc,
        )
        if force:
            raise
    return service


def service_to_list_item(
    service: UserService,
    *,
    user_label: str,
    product_name: str | None,
    panel_name: str | None,
) -> dict:
    return {
        "id": service.id,
        "user": user_label,
        "telegramUserId": service.telegram_user_id,
        "product": product_name,
        "panel": panel_name,
        "marzbanUsername": service.panel_username,
        "status": service.status,
        "expireAt": service.expire_at,
        "remainingTrafficBytes": service.remaining_traffic_bytes,
        "usedTrafficBytes": service.used_traffic_bytes or 0,
        "dataLimitBytes": service.data_limit_bytes,
        "onlineStatus": service.online_status,
        "lastOnlineAt": service.last_online_at,
        "createdAt": service.created_at,
        "lastSyncedAt": service.last_synced_at,
    }


def service_to_detail(
    service: UserService,
    *,
    user_label: str,
    product_name: str | None,
    panel_name: str | None,
    panel_user: PanelUser | None = None,
    live_from_panel: bool = False,
) -> dict:
    base = service_to_list_item(
        service,
        user_label=user_label,
        product_name=product_name,
        panel_name=panel_name,
    )
    links = list(panel_user.links) if panel_user and panel_user.links else []
    if panel_user and panel_user.subscription_url and panel_user.subscription_url not in links:
        links.insert(0, panel_user.subscription_url)

    return {
        **base,
        "orderId": service.order_id,
        "productId": service.product_id,
        "panelId": service.panel_id,
        "panelType": service.panel_type,
        "subscriptionUrl": service.subscription_url,
        "configText": service.config_text,
        "dataGb": service.data_gb,
        "daysRemaining": compute_days_remaining(service.expire_at),
        "panelUserStatus": service.panel_user_status,
        "inbounds": _parse_inbounds_cache(service.inbounds_cache),
        "links": links,
        "liveFromPanel": live_from_panel,
        "panelRaw": panel_user.raw if panel_user else None,
    }
