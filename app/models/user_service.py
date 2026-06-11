from __future__ import annotations

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.user import Base


class UserService(Base):
    __tablename__ = "user_services"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    telegram_user_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    order_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("orders.id"), nullable=True)
    product_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("products.id"), nullable=True)
    panel_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("panels.id"), nullable=True)
    panel_type: Mapped[str] = mapped_column(String(32), nullable=False)
    panel_username: Mapped[str] = mapped_column(String(128), nullable=False)
    subscription_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    config_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    data_gb: Mapped[int] = mapped_column(Integer, nullable=False, default=10)
    expire_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="active", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
