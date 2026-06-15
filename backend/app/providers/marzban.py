from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Any

from app.core.errors import PanelNotFoundError
from app.core.http_client import PanelHttpClient
from app.models.catalog import Panel
from app.providers.base import AuthCacheCallback, PanelProvider
from app.providers.models import (
    PanelInbound,
    PanelNode,
    PanelSystemStats,
    PanelTestResult,
    PanelUser,
    PanelUserCreate,
    PanelUserList,
    PanelUserUpdate,
)
from app.providers.schemas_marzban import MarzbanUserCreate, MarzbanUserModify, MarzbanUserResponse

logger = logging.getLogger(__name__)

TOKEN_TTL_SECONDS = 3300


class MarzbanProvider(PanelProvider):
    """Provider مرزبان — مطابق OpenAPI رسمی."""

    def __init__(
        self,
        panel: Panel,
        http: PanelHttpClient,
        on_auth_cache_update: AuthCacheCallback,
    ) -> None:
        self.panel = panel
        self.http = http
        self._on_auth_cache_update = on_auth_cache_update
        self._base = panel.api_url.rstrip("/")

    def _url(self, path: str) -> str:
        return f"{self._base}{path}"

    def _read_auth_cache(self) -> dict[str, Any] | None:
        raw = self.panel.auth_cache or self.panel.datelogin
        if not raw:
            return None
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return None

    def _token_valid(self, cache: dict[str, Any]) -> bool:
        token = cache.get("access_token")
        saved_at = cache.get("obtained_at")
        if not token or not saved_at:
            return False
        try:
            parsed = datetime.fromisoformat(str(saved_at).replace("Z", "+00:00"))
        except ValueError:
            return False
        age = (datetime.now(timezone.utc) - parsed).total_seconds()
        return age <= TOKEN_TTL_SECONDS

    async def _obtain_token(self) -> str:
        response = await self.http.request(
            "POST",
            self._url("/api/admin/token"),
            data={
                "username": self.panel.username_panel,
                "password": self.panel.password_panel,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded", "accept": "application/json"},
        )
        self.http.raise_for_status(response, context="Marzban token")
        body = response.json()
        token = body.get("access_token")
        if not token:
            raise PanelNotFoundError("توکن Marzban دریافت نشد")
        cache = {
            "access_token": token,
            "token_type": body.get("token_type", "bearer"),
            "obtained_at": datetime.now(timezone.utc).isoformat(),
        }
        await self._on_auth_cache_update(cache)
        return token

    async def _get_token(self, *, force_refresh: bool = False) -> str:
        if not force_refresh:
            cache = self._read_auth_cache()
            if cache and self._token_valid(cache):
                return cache["access_token"]
        return await self._obtain_token()

    async def _auth_request(
        self,
        method: str,
        path: str,
        *,
        json: Any = None,
        params: dict | None = None,
        retry_on_401: bool = True,
    ):
        token = await self._get_token()
        headers = {"Authorization": f"Bearer {token}", "accept": "application/json"}
        if json is not None:
            headers["Content-Type"] = "application/json"
        response = await self.http.request(
            method,
            self._url(path),
            headers=headers,
            json=json,
            params=params,
        )
        if response.status_code == 401 and retry_on_401:
            token = await self._get_token(force_refresh=True)
            headers["Authorization"] = f"Bearer {token}"
            response = await self.http.request(
                method,
                self._url(path),
                headers=headers,
                json=json,
                params=params,
            )
        return response

    @staticmethod
    def _parse_inbounds_config(raw: str | None) -> dict[str, list[str]]:
        if not raw or not raw.strip():
            return {}
        try:
            parsed = json.loads(raw)
            if isinstance(parsed, dict):
                return {k: v if isinstance(v, list) else [v] for k, v in parsed.items()}
        except json.JSONDecodeError:
            pass
        return {}

    @staticmethod
    def _parse_proxies_config(raw: str | None) -> dict[str, Any]:
        if not raw or not raw.strip():
            return {}
        try:
            parsed = json.loads(raw)
            return parsed if isinstance(parsed, dict) else {}
        except json.JSONDecodeError:
            return {}

    @staticmethod
    def _to_panel_user(body: dict[str, Any]) -> PanelUser:
        parsed = MarzbanUserResponse.model_validate(body)
        expire_at = None
        if parsed.expire:
            expire_at = datetime.fromtimestamp(parsed.expire, tz=timezone.utc)
        return PanelUser(
            username=parsed.username,
            subscription_url=parsed.subscription_url or None,
            links=list(parsed.links or []),
            data_limit_bytes=parsed.data_limit,
            used_traffic_bytes=parsed.used_traffic,
            expire_at=expire_at,
            status=parsed.status,
            raw=body,
        )

    def _expire_timestamp(self, expire_at: datetime | None) -> int:
        if expire_at is None:
            return 0
        return int(expire_at.timestamp())

    async def test_connection(self) -> PanelTestResult:
        try:
            await self._get_token(force_refresh=True)
            response = await self._auth_request("GET", "/api/system")
            self.http.raise_for_status(response, context="Marzban system")
            return PanelTestResult(ok=True, message="اتصال به Marzban برقرار شد.")
        except Exception as exc:
            logger.exception("marzban_test_failed panel_id=%s", self.panel.id)
            return PanelTestResult(ok=False, message=str(exc))

    async def user_exists(self, username: str) -> bool:
        try:
            await self.get_user(username)
            return True
        except PanelNotFoundError:
            return False

    async def create_user(self, data: PanelUserCreate) -> PanelUser:
        inbounds = data.inbounds or self._parse_inbounds_config(self.panel.inbounds)
        proxies = data.proxies or self._parse_proxies_config(self.panel.proxies)
        payload = MarzbanUserCreate(
            username=data.username,
            status="active",
            expire=self._expire_timestamp(data.expire_at),
            data_limit=data.data_limit_bytes,
            inbounds=inbounds,
            proxies=proxies,
            note=data.note,
        )
        response = await self._auth_request("POST", "/api/user", json=payload.model_dump(exclude_none=True))
        if response.status_code == 409:
            logger.info("marzban_create_conflict username=%s — fetching existing", data.username)
            return await self.get_user(data.username)
        self.http.raise_for_status(response, context="Marzban create_user")
        return self._to_panel_user(response.json())

    async def update_user(self, username: str, data: PanelUserUpdate) -> PanelUser:
        payload = MarzbanUserModify(
            data_limit=data.data_limit_bytes,
            expire=self._expire_timestamp(data.expire_at) if data.expire_at else None,
            note=data.note,
            inbounds=data.inbounds,
            proxies=data.proxies,
            status="active" if data.enable else "disabled" if data.enable is not None else None,
        )
        body = payload.model_dump(exclude_none=True)
        response = await self._auth_request("PUT", f"/api/user/{username}", json=body)
        self.http.raise_for_status(response, context="Marzban update_user")
        return self._to_panel_user(response.json())

    async def delete_user(self, username: str) -> None:
        response = await self._auth_request("DELETE", f"/api/user/{username}")
        self.http.raise_for_status(response, context="Marzban delete_user")

    async def get_user(self, username: str) -> PanelUser:
        response = await self._auth_request("GET", f"/api/user/{username}")
        if response.status_code == 404:
            raise PanelNotFoundError(f"کاربر {username} یافت نشد")
        self.http.raise_for_status(response, context="Marzban get_user")
        return self._to_panel_user(response.json())

    async def get_users(self, *, offset: int = 0, limit: int = 50) -> PanelUserList:
        response = await self._auth_request(
            "GET",
            "/api/users",
            params={"offset": offset, "limit": limit},
        )
        self.http.raise_for_status(response, context="Marzban get_users")
        body = response.json()
        users = [self._to_panel_user(u) for u in body.get("users", [])]
        return PanelUserList(users=users, total=body.get("total", len(users)))

    async def reset_traffic(self, username: str) -> PanelUser:
        response = await self._auth_request("POST", f"/api/user/{username}/reset")
        self.http.raise_for_status(response, context="Marzban reset_traffic")
        return self._to_panel_user(response.json())

    async def get_inbounds(self) -> list[PanelInbound]:
        response = await self._auth_request("GET", "/api/inbounds")
        self.http.raise_for_status(response, context="Marzban get_inbounds")
        body = response.json()
        result: list[PanelInbound] = []
        if isinstance(body, dict):
            for protocol, items in body.items():
                if not isinstance(items, list):
                    continue
                for item in items:
                    if isinstance(item, dict):
                        result.append(
                            PanelInbound(
                                id=item.get("tag", protocol),
                                tag=item.get("tag"),
                                protocol=protocol,
                                port=int(item["port"]) if str(item.get("port", "")).isdigit() else None,
                                raw=item,
                            )
                        )
        return result

    async def get_nodes(self) -> list[PanelNode]:
        response = await self._auth_request("GET", "/api/nodes")
        self.http.raise_for_status(response, context="Marzban get_nodes")
        body = response.json()
        nodes: list[PanelNode] = []
        if isinstance(body, list):
            for item in body:
                if isinstance(item, dict) and "id" in item:
                    nodes.append(
                        PanelNode(
                            id=int(item["id"]),
                            name=str(item.get("name", "")),
                            address=item.get("address"),
                            status=str(item.get("status", "")),
                            raw=item,
                        )
                    )
        return nodes

    async def get_system_stats(self) -> PanelSystemStats:
        response = await self._auth_request("GET", "/api/system")
        self.http.raise_for_status(response, context="Marzban get_system_stats")
        return PanelSystemStats(raw=response.json())
