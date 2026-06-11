from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Any

import httpx

from app.core.errors import PanelAuthError, PanelError, PanelNotFoundError
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

logger = logging.getLogger(__name__)

SESSION_TTL_SECONDS = 2800


class XUIProvider(PanelProvider):
    """Provider 3X-UI — مطابق OpenAPI رسمی (Clients API + Bearer Token)."""

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
        return f"{self._base}/{path.lstrip('/')}"

    def _read_auth_cache(self) -> dict[str, Any] | None:
        raw = self.panel.auth_cache or self.panel.datelogin
        if not raw:
            return None
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return None

    def _session_valid(self, cache: dict[str, Any]) -> bool:
        cookies = cache.get("cookies")
        saved_at = cache.get("obtained_at")
        if not cookies or not saved_at:
            return False
        try:
            parsed = datetime.fromisoformat(str(saved_at).replace("Z", "+00:00"))
        except ValueError:
            return False
        return (datetime.now(timezone.utc) - parsed).total_seconds() <= SESSION_TTL_SECONDS

    async def _login_session(self) -> dict[str, str]:
        response = await self.http.request(
            "POST",
            self._url("/login"),
            json={
                "username": self.panel.username_panel,
                "password": self.panel.password_panel,
                "twoFactorCode": "",
            },
            headers={"Content-Type": "application/json", "accept": "application/json"},
        )
        self.http.raise_for_status(response, context="3X-UI login")
        body = response.json()
        if isinstance(body, dict) and body.get("success") is False:
            raise PanelAuthError(body.get("msg") or "ورود 3X-UI ناموفق")
        cookies = {name: value for name, value in response.cookies.items()}
        if not cookies:
            raise PanelAuthError("کوکی نشست 3X-UI دریافت نشد")
        cache = {
            "auth_mode": "session",
            "cookies": cookies,
            "obtained_at": datetime.now(timezone.utc).isoformat(),
        }
        await self._on_auth_cache_update(cache)
        return cookies

    async def _get_session_cookies(self, *, force_refresh: bool = False) -> dict[str, str]:
        if not force_refresh:
            cache = self._read_auth_cache()
            if cache and cache.get("auth_mode") == "session" and self._session_valid(cache):
                return cache["cookies"]
        return await self._login_session()

    def _uses_bearer(self) -> bool:
        mode = (self.panel.auth_mode or "bearer").lower()
        if mode == "session":
            return False
        return bool(self.panel.api_token)

    async def _api_request(
        self,
        method: str,
        path: str,
        *,
        json: Any = None,
        params: dict | None = None,
        retry_on_401: bool = True,
    ) -> httpx.Response:
        headers: dict[str, str] = {"accept": "application/json"}
        if json is not None:
            headers["Content-Type"] = "application/json"

        if self._uses_bearer():
            headers["Authorization"] = f"Bearer {self.panel.api_token}"
            response = await self.http.request(
                method,
                self._url(path),
                headers=headers,
                json=json,
                params=params,
            )
            if response.status_code == 401 and retry_on_401:
                raise PanelAuthError("توکن API پنل 3X-UI نامعتبر است")
            return response

        cookies = await self._get_session_cookies()
        started_headers = dict(headers)
        async with httpx.AsyncClient(timeout=self.http.timeout, verify=self.http.verify_ssl) as client:
            jar = httpx.Cookies()
            for key, value in cookies.items():
                jar.set(key, value)
            response = await client.request(
                method,
                self._url(path),
                headers=started_headers,
                json=json,
                params=params,
                cookies=jar,
            )
        if response.status_code == 401 and retry_on_401:
            cookies = await self._get_session_cookies(force_refresh=True)
            async with httpx.AsyncClient(timeout=self.http.timeout, verify=self.http.verify_ssl) as client:
                jar = httpx.Cookies()
                for key, value in cookies.items():
                    jar.set(key, value)
                response = await client.request(
                    method,
                    self._url(path),
                    headers=started_headers,
                    json=json,
                    params=params,
                    cookies=jar,
                )
        return response

    def _ensure_success(self, response: httpx.Response, *, context: str) -> dict[str, Any]:
        self.http.raise_for_status(response, context=context)
        try:
            body = response.json()
        except json.JSONDecodeError:
            raise PanelError(f"{context}: پاسخ JSON نامعتبر")
        if isinstance(body, dict) and body.get("success") is False:
            raise PanelError(body.get("msg") or context)
        return body if isinstance(body, dict) else {"obj": body}

    @staticmethod
    def _expiry_ms(expire_at: datetime | None) -> int:
        if expire_at is None:
            return 0
        return int(expire_at.timestamp() * 1000)

    def _resolve_inbound_ids(self, data: PanelUserCreate) -> list[int]:
        if data.inbound_ids:
            return data.inbound_ids
        if self.panel.inbound_id is not None:
            return [self.panel.inbound_id]
        return []

    def _to_panel_user(self, obj: dict[str, Any], *, links: list[str] | None = None) -> PanelUser:
        email = str(obj.get("email") or obj.get("username") or "")
        total = obj.get("totalGB") or obj.get("total") or 0
        up = int(obj.get("up") or obj.get("upload") or 0)
        down = int(obj.get("down") or obj.get("download") or 0)
        expiry_ms = obj.get("expiryTime") or obj.get("expiry_time")
        expire_at = None
        if expiry_ms and int(expiry_ms) > 0:
            expire_at = datetime.fromtimestamp(int(expiry_ms) / 1000, tz=timezone.utc)
        link_list = links or []
        sub_url = link_list[0] if link_list else None
        return PanelUser(
            username=email,
            subscription_url=sub_url,
            links=link_list,
            data_limit_bytes=int(total) if total else None,
            used_traffic_bytes=up + down,
            expire_at=expire_at,
            status="active" if obj.get("enable", True) else "disabled",
            sub_id=obj.get("subId") or obj.get("sub_id"),
            raw=obj,
        )

    async def _fetch_client_links(self, email: str) -> list[str]:
        response = await self._api_request("GET", f"/panel/api/clients/links/{email}")
        body = self._ensure_success(response, context="3X-UI client links")
        obj = body.get("obj")
        if isinstance(obj, list):
            return [str(x) for x in obj]
        return []

    async def test_connection(self) -> PanelTestResult:
        try:
            if self._uses_bearer() and not self.panel.api_token:
                return PanelTestResult(ok=False, message="API Token برای 3X-UI تنظیم نشده است.")
            response = await self._api_request("GET", "/panel/api/server/status")
            self._ensure_success(response, context="3X-UI test")
            return PanelTestResult(ok=True, message="اتصال به 3X-UI برقرار شد.")
        except Exception as exc:
            logger.exception("xui_test_failed panel_id=%s", self.panel.id)
            return PanelTestResult(ok=False, message=str(exc))

    async def user_exists(self, username: str) -> bool:
        try:
            await self.get_user(username)
            return True
        except PanelNotFoundError:
            return False

    async def create_user(self, data: PanelUserCreate) -> PanelUser:
        inbound_ids = self._resolve_inbound_ids(data)
        if not inbound_ids:
            raise PanelError("شناسه inbound برای 3X-UI تنظیم نشده است.")

        payload = {
            "client": {
                "email": data.username,
                "totalGB": data.data_limit_bytes or 0,
                "expiryTime": self._expiry_ms(data.expire_at),
                "enable": data.enable,
                "comment": data.note or "",
                "limitIp": 0,
                "tgId": 0,
            },
            "inboundIds": inbound_ids,
        }
        response = await self._api_request("POST", "/panel/api/clients/add", json=payload)
        self._ensure_success(response, context="3X-UI create_user")
        created = await self.get_user(data.username)
        links = await self._fetch_client_links(data.username)
        if links:
            created.links = links
            created.subscription_url = links[0]
        return created

    async def update_user(self, username: str, data: PanelUserUpdate) -> PanelUser:
        current = await self.get_user(username)
        payload: dict[str, Any] = {
            "email": username,
            "enable": data.enable if data.enable is not None else current.status == "active",
        }
        if data.data_limit_bytes is not None:
            payload["totalGB"] = data.data_limit_bytes
        elif current.data_limit_bytes is not None:
            payload["totalGB"] = current.data_limit_bytes
        if data.expire_at is not None:
            payload["expiryTime"] = self._expiry_ms(data.expire_at)
        elif current.expire_at is not None:
            payload["expiryTime"] = self._expiry_ms(current.expire_at)
        if data.note is not None:
            payload["comment"] = data.note

        response = await self._api_request("POST", f"/panel/api/clients/update/{username}", json=payload)
        self._ensure_success(response, context="3X-UI update_user")
        return await self.get_user(username)

    async def delete_user(self, username: str) -> None:
        response = await self._api_request(
            "POST",
            f"/panel/api/clients/del/{username}",
            params={"keepTraffic": 0},
        )
        self._ensure_success(response, context="3X-UI delete_user")

    async def get_user(self, username: str) -> PanelUser:
        response = await self._api_request("GET", f"/panel/api/clients/get/{username}")
        if response.status_code == 404:
            raise PanelNotFoundError(f"کلاینت {username} یافت نشد")
        body = self._ensure_success(response, context="3X-UI get_user")
        obj = body.get("obj")
        if not isinstance(obj, dict):
            raise PanelNotFoundError(f"کلاینت {username} یافت نشد")
        links = await self._fetch_client_links(username)
        return self._to_panel_user(obj, links=links)

    async def get_users(self, *, offset: int = 0, limit: int = 50) -> PanelUserList:
        response = await self._api_request("GET", "/panel/api/clients/list")
        body = self._ensure_success(response, context="3X-UI get_users")
        obj = body.get("obj")
        items: list[PanelUser] = []
        if isinstance(obj, list):
            sliced = obj[offset : offset + limit]
            for row in sliced:
                if isinstance(row, dict):
                    items.append(self._to_panel_user(row))
        return PanelUserList(users=items, total=len(obj) if isinstance(obj, list) else len(items))

    async def reset_traffic(self, username: str) -> PanelUser:
        response = await self._api_request("POST", f"/panel/api/clients/resetTraffic/{username}")
        self._ensure_success(response, context="3X-UI reset_traffic")
        return await self.get_user(username)

    async def get_inbounds(self) -> list[PanelInbound]:
        response = await self._api_request("GET", "/panel/api/inbounds/list")
        body = self._ensure_success(response, context="3X-UI get_inbounds")
        obj = body.get("obj")
        result: list[PanelInbound] = []
        if isinstance(obj, list):
            for item in obj:
                if isinstance(item, dict):
                    result.append(
                        PanelInbound(
                            id=item.get("id", 0),
                            tag=str(item.get("tag") or ""),
                            protocol=item.get("protocol"),
                            remark=item.get("remark"),
                            port=int(item["port"]) if str(item.get("port", "")).isdigit() else None,
                            raw=item,
                        )
                    )
        return result

    async def get_nodes(self) -> list[PanelNode]:
        response = await self._api_request("GET", "/panel/api/nodes/list")
        body = self._ensure_success(response, context="3X-UI get_nodes")
        obj = body.get("obj")
        nodes: list[PanelNode] = []
        if isinstance(obj, list):
            for item in obj:
                if isinstance(item, dict) and "id" in item:
                    nodes.append(
                        PanelNode(
                            id=int(item["id"]),
                            name=str(item.get("name", item.get("remark", ""))),
                            address=item.get("address"),
                            status=str(item.get("enable", "")),
                            raw=item,
                        )
                    )
        return nodes

    async def get_system_stats(self) -> PanelSystemStats:
        response = await self._api_request("GET", "/panel/api/server/status")
        body = self._ensure_success(response, context="3X-UI get_system_stats")
        obj = body.get("obj")
        return PanelSystemStats(raw=obj if isinstance(obj, dict) else body)

    async def _paged_filtered_count(self, filter_value: str) -> int:
        """OpenAPI: GET /panel/api/clients/list/paged — filtered count per status bucket."""
        response = await self._api_request(
            "GET",
            "/panel/api/clients/list/paged",
            params={
                "page": 1,
                "pageSize": 1,
                "search": "",
                "filter": filter_value,
                "protocol": "",
                "sort": "enable",
                "order": "ascend",
            },
        )
        body = self._ensure_success(response, context=f"3X-UI clients filter={filter_value}")
        obj = body.get("obj")
        if isinstance(obj, dict) and obj.get("filtered") is not None:
            return int(obj["filtered"])
        return 0

    async def get_clients_dashboard_stats(self) -> dict[str, int]:
        """آمار کاربران 3X-UI از Clients API (OpenAPI)."""
        import asyncio

        summary_resp = await self._api_request(
            "GET",
            "/panel/api/clients/list/paged",
            params={
                "page": 1,
                "pageSize": 1,
                "search": "",
                "filter": "",
                "protocol": "",
                "sort": "enable",
                "order": "ascend",
            },
        )
        summary_body = self._ensure_success(summary_resp, context="3X-UI clients summary")
        obj = summary_body.get("obj") if isinstance(summary_body.get("obj"), dict) else {}
        summary = obj.get("summary") if isinstance(obj.get("summary"), dict) else {}

        onlines_resp = await self._api_request("POST", "/panel/api/clients/onlines")
        onlines_body = self._ensure_success(onlines_resp, context="3X-UI clients onlines")
        onlines_obj = onlines_body.get("obj")
        online_count = len(onlines_obj) if isinstance(onlines_obj, list) else 0

        depleted_count, expiring_count = await asyncio.gather(
            self._paged_filtered_count("depleted"),
            self._paged_filtered_count("expiring"),
        )

        total = int(summary.get("total") or obj.get("total") or 0)
        return {
            "total_users": total,
            "online_users": online_count,
            "volume_exhausted_users": depleted_count,
            "expired_users": expiring_count,
        }
