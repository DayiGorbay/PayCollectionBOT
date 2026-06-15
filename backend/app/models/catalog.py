from __future__ import annotations

from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


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
    code: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    category: Mapped[str | None] = mapped_column(String(64))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


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


class UserService(Base):
    """سرویس فعال کاربر روی پنل (پس از تأیید سفارش)."""

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


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    user_label: Mapped[str] = mapped_column(String(128), nullable=False)
    hash_value: Mapped[str] = mapped_column(String(64), nullable=False)
    amount: Mapped[str] = mapped_column(String(64), nullable=False)
    method: Mapped[str] = mapped_column(String(64), nullable=False)
    date_label: Mapped[str] = mapped_column(String(64), nullable=False)
    type_label: Mapped[str] = mapped_column(String(32), nullable=False)
    panel: Mapped[str] = mapped_column(String(128), nullable=False)


class Panel(Base):
    """اتصال به Marzban یا 3x-ui / x-ui."""

    __tablename__ = "panels"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code_panel: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    api_url: Mapped[str] = mapped_column(String(512), nullable=False)
    panel_type: Mapped[str] = mapped_column(String(32), nullable=False)  # marzban | xui
    username_panel: Mapped[str] = mapped_column(String(128), nullable=False)
    password_panel: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="فعال", nullable=False)
    last_sync_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    auth_mode: Mapped[str] = mapped_column(String(32), default="bearer", nullable=False)
    api_token: Mapped[str | None] = mapped_column(String(512), nullable=True)
    auth_cache: Mapped[str | None] = mapped_column(Text, nullable=True)
    datelogin: Mapped[str | None] = mapped_column(Text, nullable=True)
    inbounds: Mapped[str | None] = mapped_column(Text, nullable=True)
    proxies: Mapped[str | None] = mapped_column(Text, nullable=True)
    inbound_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class DiscountCode(Base):
    __tablename__ = "discount_codes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    amount: Mapped[str] = mapped_column(String(64), nullable=False)
    type_label: Mapped[str] = mapped_column(String(32), nullable=False)
    used_label: Mapped[str] = mapped_column(String(32), nullable=False)
    valid_until: Mapped[str] = mapped_column(String(32), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    discount_percent: Mapped[int | None] = mapped_column(Integer, nullable=True)
    discount_amount_rial: Mapped[int | None] = mapped_column(Integer, nullable=True)
    max_uses: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    used_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)


class BotSetting(Base):
    __tablename__ = "bot_settings"

    key: Mapped[str] = mapped_column(String(64), primary_key=True)
    value: Mapped[str] = mapped_column(Text, nullable=False, default="")


class FreeConnectConfig(Base):
    __tablename__ = "free_connect_config"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    coins_required: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    data_gb: Mapped[int] = mapped_column(Integer, nullable=False, default=10)
    panel_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("panels.id"), nullable=True)
    duration_days: Mapped[int] = mapped_column(Integer, nullable=False, default=30)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)
