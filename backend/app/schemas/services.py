from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class ServiceListItem(BaseModel):
    id: int
    user: str
    telegram_user_id: int = Field(alias="telegramUserId")
    product: str | None = None
    panel: str | None = None
    marzban_username: str = Field(alias="marzbanUsername")
    status: str
    expire_at: datetime | None = Field(default=None, alias="expireAt")
    remaining_traffic_bytes: int | None = Field(default=None, alias="remainingTrafficBytes")
    used_traffic_bytes: int = Field(default=0, alias="usedTrafficBytes")
    data_limit_bytes: int | None = Field(default=None, alias="dataLimitBytes")
    online_status: str | None = Field(default=None, alias="onlineStatus")
    last_online_at: datetime | None = Field(default=None, alias="lastOnlineAt")
    created_at: datetime = Field(alias="createdAt")
    last_synced_at: datetime | None = Field(default=None, alias="lastSyncedAt")

    model_config = {"populate_by_name": True}


class ServiceDetailOut(ServiceListItem):
    order_id: int | None = Field(default=None, alias="orderId")
    product_id: int | None = Field(default=None, alias="productId")
    panel_id: int | None = Field(default=None, alias="panelId")
    panel_type: str = Field(alias="panelType")
    subscription_url: str | None = Field(default=None, alias="subscriptionUrl")
    config_text: str | None = Field(default=None, alias="configText")
    data_gb: int = Field(alias="dataGb")
    days_remaining: int | None = Field(default=None, alias="daysRemaining")
    panel_user_status: str | None = Field(default=None, alias="panelUserStatus")
    inbounds: dict[str, Any] | list[Any] | None = None
    links: list[str] = Field(default_factory=list)
    live_from_panel: bool = Field(default=False, alias="liveFromPanel")
    panel_raw: dict[str, Any] | None = Field(default=None, alias="panelRaw")

    model_config = {"populate_by_name": True}


class ServiceSyncResult(BaseModel):
    id: int
    synced: bool
    last_synced_at: datetime | None = Field(default=None, alias="lastSyncedAt")
    message: str = "همگام‌سازی انجام شد."

    model_config = {"populate_by_name": True}
