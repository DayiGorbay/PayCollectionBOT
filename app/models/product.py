from __future__ import annotations

from sqlalchemy import Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.user import Base


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    price_label: Mapped[str] = mapped_column(String(64), nullable=False)
    price_rial: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    duration_days: Mapped[int] = mapped_column(Integer, nullable=False, default=30)
    duration: Mapped[str] = mapped_column(String(64), nullable=False, default="30 روز")
    size: Mapped[str] = mapped_column(String(64), nullable=False, default="—")
    panel_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("panels.id"), nullable=True)
    panel: Mapped[str] = mapped_column(String(128), nullable=False, default="—")
    code: Mapped[str] = mapped_column(String(64), nullable=False)
    category: Mapped[str | None] = mapped_column(String(64))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
