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
    discount_code: str | None = Field(alias="discountCode", default=None)
    wallet_paid_rial: int = Field(alias="walletPaidRial", default=0)


class OrderApproveBody(BaseModel):
    block_user: bool = Field(default=False, alias="blockUser")

    model_config = {"populate_by_name": True}
