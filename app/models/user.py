from __future__ import annotations

from sqlalchemy import BigInteger, Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    # Telegram IDs can exceed int32 range
    telegram_id = Column(BigInteger, unique=True, nullable=False, index=True)
    first_name = Column(String(128), nullable=True)
    last_name = Column(String(128), nullable=True)
    username = Column(String(64), nullable=True)
    phone_number = Column(String(32), unique=True, nullable=True)
    is_iranian = Column(Boolean, default=False)
    verified = Column(Boolean, default=False)
    joined_channel = Column(Boolean, default=False)
    referral_code = Column(String(32), unique=True, nullable=False, index=True)
    invited_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    invited_count = Column(Integer, default=0)
    coins = Column(Integer, default=0)
    balance = Column(Integer, default=0)
    referral_finalized = Column(Boolean, default=False)
    referral_finalized_at = Column(DateTime(timezone=True), nullable=True)
    is_suspicious = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    inviter = relationship("User", remote_side=[id], backref="invitees")
