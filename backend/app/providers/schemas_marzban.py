"""Pydantic models derived from Marzban OpenAPI (v0.8.4)."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class MarzbanToken(BaseModel):
    access_token: str
    token_type: str = "bearer"


class MarzbanUserCreate(BaseModel):
    username: str
    status: str = "active"
    expire: int | None = None
    data_limit: int | None = None
    data_limit_reset_strategy: str = "no_reset"
    proxies: dict[str, Any] = Field(default_factory=dict)
    inbounds: dict[str, list[str]] = Field(default_factory=dict)
    note: str | None = None


class MarzbanUserModify(BaseModel):
    status: str | None = None
    expire: int | None = None
    data_limit: int | None = None
    data_limit_reset_strategy: str | None = None
    proxies: dict[str, Any] | None = None
    inbounds: dict[str, list[str]] | None = None
    note: str | None = None


class MarzbanUserResponse(BaseModel):
    username: str
    status: str
    used_traffic: int = 0
    data_limit: int | None = None
    expire: int | None = None
    subscription_url: str = ""
    links: list[str] = Field(default_factory=list)
    note: str | None = None

    model_config = {"extra": "allow"}
