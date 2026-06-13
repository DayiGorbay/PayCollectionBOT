from __future__ import annotations
from datetime import datetime
from sqlalchemy import Boolean, DateTime, ForeignKey, BigInteger, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

class TelegramUser(Base):
    """همان جدول users ربات — مشترک بین bot و API."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False, index=True)
    first_name: Mapped[str | None] = mapped_column(String(128))
    last_name: Mapped[str | None] = mapped_column(String(128))
    username: Mapped[str | None] = mapped_column(String(64))
    phone_number: Mapped[str | None] = mapped_column(String(32), unique=True)
    is_iranian: Mapped[bool] = mapped_column(Boolean, default=False)
    verified: Mapped[bool] = mapped_column(Boolean, default=False)
    joined_channel: Mapped[bool] = mapped_column(Boolean, default=False)
    referral_code: Mapped[str] = mapped_column(String(32), unique=True, nullable=False, index=True)
    invited_by: Mapped[int | None] = mapped_column(BigInteger,ForeignKey("users.id"),nullable=True)
    invited_count: Mapped[int] = mapped_column(Integer, default=0)
    coins: Mapped[int] = mapped_column(Integer, default=0)
    balance: Mapped[int] = mapped_column(Integer, default=0)
    referral_finalized: Mapped[bool] = mapped_column(Boolean, default=False)
    referral_finalized_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    is_suspicious: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    inviter: Mapped["TelegramUser" | None] = relationship("TelegramUser", remote_side=[id], foreign_keys=[invited_by])
