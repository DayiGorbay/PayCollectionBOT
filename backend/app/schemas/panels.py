from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator


class PanelCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    code_panel: str = Field(min_length=2, max_length=64, pattern=r"^[a-zA-Z0-9_-]+$")
    api_url: str = Field(min_length=8, max_length=512)
    panel_type: Literal["marzban", "xui"]
    username_panel: str = Field(min_length=1, max_length=128)
    password_panel: str = Field(min_length=1, max_length=255)
    status: str = "فعال"
    auth_mode: Literal["bearer", "session"] = "bearer"
    api_token: str | None = None
    inbounds: str | None = None
    proxies: str | None = None
    inbound_id: int | None = None

    @field_validator("api_url")
    @classmethod
    def strip_trailing_slash(cls, v: str) -> str:
        return v.strip().rstrip("/")

    @field_validator("inbounds", "proxies", "api_token")
    @classmethod
    def empty_to_none(cls, v: str | None) -> str | None:
        if v is None or not str(v).strip():
            return None
        return v.strip()


class PanelUpdate(BaseModel):
    name: str | None = None
    api_url: str | None = None
    username_panel: str | None = None
    password_panel: str | None = None
    status: str | None = None
    auth_mode: Literal["bearer", "session"] | None = None
    api_token: str | None = None
    inbounds: str | None = None
    proxies: str | None = None
    inbound_id: int | None = None


class PanelOut(BaseModel):
    id: int
    name: str
    code_panel: str = Field(alias="codePanel")
    api: str
    type: str
    status: str
    last_sync: str = Field(alias="lastSync")
    auth_mode: str = Field(default="bearer", alias="authMode")
    api_token_set: bool = Field(default=False, alias="apiTokenSet")
    inbound_id: int | None = Field(default=None, alias="inboundId")
    has_inbounds: bool = Field(default=False, alias="hasInbounds")
    has_proxies: bool = Field(default=False, alias="hasProxies")

    model_config = {"populate_by_name": True}


class PanelTestResult(BaseModel):
    ok: bool
    message: str


class PanelStatsOut(BaseModel):
    panel_id: int = Field(alias="panelId")
    ok: bool
    error: str | None = None
    panel_type: str = Field(alias="panelType")
    version: str | None = None
    cpu_percent: float | None = Field(default=None, alias="cpuPercent")
    mem_used_bytes: int | None = Field(default=None, alias="memUsedBytes")
    mem_total_bytes: int | None = Field(default=None, alias="memTotalBytes")
    mem_percent: float | None = Field(default=None, alias="memPercent")
    xray_state: str | None = Field(default=None, alias="xrayState")
    total_users: int | None = Field(default=None, alias="totalUsers")
    online_users: int | None = Field(default=None, alias="onlineUsers")
    expired_users: int | None = Field(default=None, alias="expiredUsers")
    volume_exhausted_users: int | None = Field(default=None, alias="volumeExhaustedUsers")
    tcp_count: int | None = Field(default=None, alias="tcpCount")
    net_up_bytes: int | None = Field(default=None, alias="netUpBytes")
    net_down_bytes: int | None = Field(default=None, alias="netDownBytes")
    fetched_at: str = Field(alias="fetchedAt")

    model_config = {"populate_by_name": True}
