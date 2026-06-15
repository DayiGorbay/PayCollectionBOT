from __future__ import annotations

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.user import Base


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    telegram_user_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    user_label: Mapped[str] = mapped_column(String(128), nullable=False)
    order_type: Mapped[str] = mapped_column(String(32), nullable=False)
    product_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("products.id"), nullable=True)
    product_name: Mapped[str] = mapped_column(String(255), nullable=False)
    requested_username: Mapped[str | None] = mapped_column(String(64), nullable=True)
    amount: Mapped[str] = mapped_column(String(64), nullable=False)
    amount_rial: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    original_amount_rial: Mapped[int | None] = mapped_column(Integer, nullable=True)
    discount_code: Mapped[str | None] = mapped_column(String(64), nullable=True)
    discount_amount_rial: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    wallet_paid_rial: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    method: Mapped[str] = mapped_column(String(64), default="کارت به کارت")
    status: Mapped[str] = mapped_column(String(32), default="در انتظار", index=True)
    receipt_path: Mapped[str | None] = mapped_column(String(512), nullable=True)
    receipt_file_id: Mapped[str | None] = mapped_column(String(256), nullable=True)
    admin_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    processed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
