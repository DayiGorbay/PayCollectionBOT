from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.user import Base


class Panel(Base):
    __tablename__ = "panels"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code_panel: Mapped[str] = mapped_column(String(64), nullable=False)
    api_url: Mapped[str] = mapped_column(String(512), nullable=False)
    panel_type: Mapped[str] = mapped_column(String(32), nullable=False)
    username_panel: Mapped[str] = mapped_column(String(128), nullable=False)
    password_panel: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="فعال")
    auth_mode: Mapped[str] = mapped_column(String(32), default="bearer")
    api_token: Mapped[str | None] = mapped_column(String(512), nullable=True)
    auth_cache: Mapped[str | None] = mapped_column(Text, nullable=True)
    datelogin: Mapped[str | None] = mapped_column(Text, nullable=True)
    inbounds: Mapped[str | None] = mapped_column(Text, nullable=True)
    proxies: Mapped[str | None] = mapped_column(Text, nullable=True)
    inbound_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    last_sync_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
