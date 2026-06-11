from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class PanelUserCreate(BaseModel):
    """ورودی یکپارچه ساخت کاربر/کلاینت روی پنل."""

    username: str
    data_limit_bytes: int | None = None
    expire_at: datetime | None = None
    inbound_ids: list[int] | None = None
    inbounds: dict[str, list[str]] | None = None
    proxies: dict[str, Any] | None = None
    note: str | None = None
    enable: bool = True


class PanelUserUpdate(BaseModel):
    data_limit_bytes: int | None = None
    expire_at: datetime | None = None
    enable: bool | None = None
    note: str | None = None
    inbounds: dict[str, list[str]] | None = None
    proxies: dict[str, Any] | None = None


class PanelUser(BaseModel):
    username: str
    subscription_url: str | None = None
    links: list[str] = Field(default_factory=list)
    data_limit_bytes: int | None = None
    used_traffic_bytes: int = 0
    expire_at: datetime | None = None
    status: str = "active"
    sub_id: str | None = None
    raw: dict[str, Any] = Field(default_factory=dict)


class PanelUserList(BaseModel):
    users: list[PanelUser] = Field(default_factory=list)
    total: int = 0


class PanelInbound(BaseModel):
    id: str | int
    tag: str | None = None
    protocol: str | None = None
    remark: str | None = None
    port: int | None = None
    raw: dict[str, Any] = Field(default_factory=dict)


class PanelNode(BaseModel):
    id: int
    name: str
    address: str | None = None
    status: str | None = None
    raw: dict[str, Any] = Field(default_factory=dict)


class PanelSystemStats(BaseModel):
    raw: dict[str, Any] = Field(default_factory=dict)


class PanelTestResult(BaseModel):
    ok: bool
    message: str
