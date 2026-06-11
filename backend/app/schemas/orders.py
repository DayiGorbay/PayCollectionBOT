from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class OrderListItem(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: int
    user: str
    product: str
    amount: str
    method: str
    date: str
    status: str
    order_type: str = Field(alias="orderType")
    has_receipt: bool = Field(alias="hasReceipt")


class OrderDetailOut(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: int
    user: str
    telegram_user_id: int = Field(alias="telegramUserId")
    product: str
    amount: str
    amount_rial: int = Field(alias="amountRial")
    method: str
    date: str
    status: str
    order_type: str = Field(alias="orderType")
    has_receipt: bool = Field(alias="hasReceipt")
    receipt_url: str | None = Field(alias="receiptUrl", default=None)
    admin_note: str | None = Field(alias="adminNote", default=None)
