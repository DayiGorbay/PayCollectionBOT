from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class ActiveCouponOut(BaseModel):
    id: int
    code: str
    type: str
    amount: int | float
    valid_until: str = Field(alias="validUntil")

    model_config = ConfigDict(populate_by_name=True)


class RecentOrderOut(BaseModel):
    id: int
    user: str
    product: str
    amount: str
    status: str
    date: str


class DashboardSummaryOut(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    total_users: int = Field(alias="totalUsers")
    active_users: int = Field(alias="activeUsers")
    today_users: int = Field(alias="todayUsers")
    total_revenue: int = Field(alias="totalRevenue")
    pending_orders: int = Field(alias="pendingOrders")
    active_panels: int = Field(alias="activePanels")
    active_coupons: list[ActiveCouponOut] = Field(alias="activeCoupons")
    recent_orders: list[RecentOrderOut] = Field(alias="recentOrders")
