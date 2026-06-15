from __future__ import annotations

from pydantic import BaseModel, Field


class ProductCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    price: int = Field(gt=0, description="مبلغ به تومان")
    duration_days: int = Field(gt=0, le=3650, alias="durationDays")
    panel_id: int = Field(gt=0, alias="panelId")
    code: str = Field(min_length=1, max_length=64)
    category: str | None = Field(default=None, max_length=64)

    model_config = {"populate_by_name": True}


class ProductUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=255)
    price: int | None = Field(default=None, gt=0)
    duration_days: int | None = Field(default=None, gt=0, le=3650, alias="durationDays")
    panel_id: int | None = Field(default=None, gt=0, alias="panelId")
    category: str | None = Field(default=None, max_length=64)
    is_active: bool | None = Field(default=None, alias="isActive")

    model_config = {"populate_by_name": True}


class ProductOut(BaseModel):
    id: int
    name: str
    price: str
    duration_days: int = Field(alias="durationDays")
    duration: str
    panel: str
    panel_id: int | None = Field(default=None, alias="panelId")
    code: str
    category: str | None = None
    is_active: bool = True

    model_config = {"populate_by_name": True}
