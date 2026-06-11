from __future__ import annotations

import json
from collections.abc import Awaitable, Callable
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.http_client import PanelHttpClient
from app.models.catalog import Panel
from app.providers.base import PanelProvider
from app.providers.marzban import MarzbanProvider
from app.providers.xui import XUIProvider

AuthCacheCallback = Callable[[dict], Awaitable[None]]


def _make_cache_callback(panel: Panel, session: AsyncSession) -> AuthCacheCallback:
    async def _save(cache: dict) -> None:
        panel.auth_cache = json.dumps(cache, ensure_ascii=False)
        panel.last_sync_at = datetime.now(timezone.utc)
        await session.flush()

    return _save


def create_provider(panel: Panel, session: AsyncSession) -> PanelProvider:
    """Product.panel_id → Panel → Provider مناسب."""

    http = PanelHttpClient(panel_id=panel.id, panel_type=panel.panel_type)
    on_cache = _make_cache_callback(panel, session)

    if panel.panel_type == "marzban":
        return MarzbanProvider(panel, http, on_cache)
    if panel.panel_type == "xui":
        return XUIProvider(panel, http, on_cache)
    raise ValueError(f"نوع پنل پشتیبانی نمی‌شود: {panel.panel_type}")
