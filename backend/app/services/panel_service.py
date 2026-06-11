from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import PanelError
from app.models.catalog import Panel
from app.providers.factory import create_provider
from app.repositories.panel_repository import PanelRepository
from app.schemas.panels import PanelCreate, PanelOut, PanelStatsOut, PanelTestResult, PanelUpdate

logger = logging.getLogger(__name__)


def _last_sync_label(dt: datetime | None) -> str:
    if dt is None:
        return "هرگز"
    return dt.strftime("%Y/%m/%d %H:%M")


def panel_to_out(panel: Panel) -> PanelOut:
    return PanelOut(
        id=panel.id,
        name=panel.name,
        code_panel=panel.code_panel,
        api=panel.api_url,
        type="Marzban" if panel.panel_type == "marzban" else "x-ui",
        status=panel.status,
        last_sync=_last_sync_label(panel.last_sync_at),
        auth_mode=panel.auth_mode,
        api_token_set=bool(panel.api_token),
        inbound_id=panel.inbound_id,
        has_inbounds=bool(panel.inbounds),
        has_proxies=bool(panel.proxies),
    )


async def list_panels(session: AsyncSession) -> list[PanelOut]:
    repo = PanelRepository(session)
    return [panel_to_out(row) for row in await repo.list_all()]


async def get_panel(session: AsyncSession, panel_id: int) -> Panel | None:
    return await PanelRepository(session).get_by_id(panel_id)


async def get_panel_by_code(session: AsyncSession, code: str) -> Panel | None:
    return await PanelRepository(session).get_by_code(code)


async def create_panel(session: AsyncSession, payload: PanelCreate) -> Panel:
    if payload.panel_type == "xui" and payload.inbound_id is None:
        raise ValueError("برای 3X-UI شناسه inbound الزامی است.")
    if payload.panel_type == "xui" and payload.auth_mode == "bearer" and not payload.api_token:
        raise ValueError("برای 3X-UI با احراز Bearer، API Token الزامی است.")

    panel = Panel(
        name=payload.name,
        code_panel=payload.code_panel,
        api_url=payload.api_url,
        panel_type=payload.panel_type,
        username_panel=payload.username_panel,
        password_panel=payload.password_panel,
        status=payload.status,
        auth_mode=payload.auth_mode,
        api_token=payload.api_token,
        inbounds=payload.inbounds,
        proxies=payload.proxies,
        inbound_id=payload.inbound_id,
    )
    session.add(panel)
    await session.flush()
    await session.refresh(panel)
    return panel


async def update_panel(session: AsyncSession, panel: Panel, payload: PanelUpdate) -> Panel:
    data = payload.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(panel, key, value)
    await session.flush()
    await session.refresh(panel)
    return panel


def _panel_from_create(payload: PanelCreate) -> Panel:
    return Panel(
        id=0,
        name=payload.name,
        code_panel=payload.code_panel,
        api_url=payload.api_url,
        panel_type=payload.panel_type,
        username_panel=payload.username_panel,
        password_panel=payload.password_panel,
        status=payload.status,
        auth_mode=payload.auth_mode,
        api_token=payload.api_token,
        inbounds=payload.inbounds,
        proxies=payload.proxies,
        inbound_id=payload.inbound_id,
    )


async def test_panel_connection(session: AsyncSession, panel: Panel) -> PanelTestResult:
    provider = create_provider(panel, session)
    result = await provider.test_connection()
    return PanelTestResult(ok=result.ok, message=result.message)


def _mem_percent(used: int | None, total: int | None) -> float | None:
    if used is None or total is None or total <= 0:
        return None
    return round(used / total * 100, 1)


def _normalize_marzban_stats(panel_id: int, raw: dict[str, Any]) -> PanelStatsOut:
    now = datetime.now(timezone.utc).strftime("%H:%M:%S")
    mem_used = raw.get("mem_used")
    mem_total = raw.get("mem_total")
    return PanelStatsOut(
        panel_id=panel_id,
        ok=True,
        panel_type="marzban",
        version=raw.get("version"),
        cpu_percent=float(raw["cpu_usage"]) if raw.get("cpu_usage") is not None else None,
        mem_used_bytes=mem_used,
        mem_total_bytes=mem_total,
        mem_percent=_mem_percent(mem_used, mem_total),
        total_users=raw.get("total_user"),
        online_users=raw.get("online_users"),
        expired_users=raw.get("users_expired"),
        volume_exhausted_users=raw.get("users_limited"),
        net_up_bytes=raw.get("outgoing_bandwidth"),
        net_down_bytes=raw.get("incoming_bandwidth"),
        fetched_at=now,
    )


def _normalize_xui_stats(panel_id: int, raw: dict[str, Any]) -> PanelStatsOut:
    now = datetime.now(timezone.utc).strftime("%H:%M:%S")
    mem = raw.get("mem") if isinstance(raw.get("mem"), dict) else {}
    xray = raw.get("xray") if isinstance(raw.get("xray"), dict) else {}
    net = raw.get("netIO") if isinstance(raw.get("netIO"), dict) else {}
    mem_used = mem.get("current")
    mem_total = mem.get("total")
    return PanelStatsOut(
        panel_id=panel_id,
        ok=True,
        panel_type="xui",
        version=xray.get("version"),
        cpu_percent=float(raw["cpu"]) if raw.get("cpu") is not None else None,
        mem_used_bytes=mem_used,
        mem_total_bytes=mem_total,
        mem_percent=_mem_percent(mem_used, mem_total),
        xray_state=xray.get("state"),
        tcp_count=raw.get("tcpCount"),
        net_up_bytes=net.get("up"),
        net_down_bytes=net.get("down"),
        fetched_at=now,
    )


def _stats_error(panel_id: int, panel_type: str, message: str) -> PanelStatsOut:
    return PanelStatsOut(
        panel_id=panel_id,
        ok=False,
        error=message,
        panel_type=panel_type,
        fetched_at=datetime.now(timezone.utc).strftime("%H:%M:%S"),
    )


async def get_panel_stats(session: AsyncSession, panel: Panel) -> PanelStatsOut:
    provider = create_provider(panel, session)
    try:
        result = await provider.get_system_stats()
        raw = result.raw
        if panel.panel_type == "marzban":
            return _normalize_marzban_stats(panel.id, raw)

        stats = _normalize_xui_stats(panel.id, raw)
        from app.providers.xui import XUIProvider

        if isinstance(provider, XUIProvider):
            counts = await provider.get_clients_dashboard_stats()
            stats = stats.model_copy(
                update={
                    "total_users": counts.get("total_users"),
                    "online_users": counts.get("online_users"),
                    "expired_users": counts.get("expired_users"),
                    "volume_exhausted_users": counts.get("volume_exhausted_users"),
                }
            )
        return stats
    except PanelError as exc:
        logger.warning("panel_stats_failed panel_id=%s error=%s", panel.id, exc)
        return _stats_error(panel.id, panel.panel_type, str(exc))
    except Exception as exc:
        logger.exception("panel_stats_unexpected panel_id=%s", panel.id)
        return _stats_error(panel.id, panel.panel_type, str(exc))


async def list_panels_stats(session: AsyncSession) -> list[PanelStatsOut]:
    repo = PanelRepository(session)
    panels = await repo.list_all()
    results: list[PanelStatsOut] = []
    for panel in panels:
        if panel.status != "فعال":
            results.append(_stats_error(panel.id, panel.panel_type, "پنل غیرفعال است"))
            continue
        results.append(await get_panel_stats(session, panel))
    return results


async def test_panel_credentials(payload: PanelCreate) -> PanelTestResult:
    temp = _panel_from_create(payload)
    from app.core.http_client import PanelHttpClient
    from app.providers.marzban import MarzbanProvider
    from app.providers.xui import XUIProvider

    async def noop(_: dict) -> None:
        return None

    http = PanelHttpClient(panel_id=0, panel_type=temp.panel_type)
    if temp.panel_type == "marzban":
        provider = MarzbanProvider(temp, http, noop)
    else:
        provider = XUIProvider(temp, http, noop)
    result = await provider.test_connection()
    return PanelTestResult(ok=result.ok, message=result.message)
