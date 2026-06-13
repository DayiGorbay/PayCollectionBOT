"""initial schema

Revision ID: 001_initial
Revises:
Create Date: 2026-05-24

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("telegram_id", sa.BigInteger(), nullable=False),
        sa.Column("first_name", sa.String(length=128), nullable=True),
        sa.Column("last_name", sa.String(length=128), nullable=True),
        sa.Column("username", sa.String(length=64), nullable=True),
        sa.Column("phone_number", sa.String(length=32), nullable=True),
        sa.Column("is_iranian", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("verified", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("joined_channel", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("referral_code", sa.String(length=32), nullable=False),
        sa.Column("invited_by", sa.Integer(), nullable=True),
        sa.Column("invited_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("coins", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("balance", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("referral_finalized", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("referral_finalized_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_suspicious", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["invited_by"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("phone_number"),
        sa.UniqueConstraint("referral_code"),
        sa.UniqueConstraint("telegram_id"),
    )
    op.create_index("ix_users_telegram_id", "users", ["telegram_id"], unique=False)

    op.create_table(
        "admin_users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("username", sa.String(length=64), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("display_name", sa.String(length=128), nullable=False),
        sa.Column("role", sa.String(length=32), nullable=False, server_default="admin"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("failed_login_attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("locked_until", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("username"),
    )
    op.create_index("ix_admin_users_username", "admin_users", ["username"], unique=False)

    op.create_table(
        "panels",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("code_panel", sa.String(length=64), nullable=False),
        sa.Column("api_url", sa.String(length=512), nullable=False),
        sa.Column("panel_type", sa.String(length=32), nullable=False),
        sa.Column("username_panel", sa.String(length=128), nullable=False),
        sa.Column("password_panel", sa.String(length=255), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="فعال"),
        sa.Column("last_sync_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("auth_mode", sa.String(length=32), nullable=False, server_default="bearer"),
        sa.Column("api_token", sa.String(length=512), nullable=True),
        sa.Column("auth_cache", sa.Text(), nullable=True),
        sa.Column("datelogin", sa.Text(), nullable=True),
        sa.Column("inbounds", sa.Text(), nullable=True),
        sa.Column("proxies", sa.Text(), nullable=True),
        sa.Column("inbound_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code_panel"),
    )
    op.create_index("ix_panels_code_panel", "panels", ["code_panel"], unique=False)

    op.create_table(
        "products",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("price_label", sa.String(length=64), nullable=False),
        sa.Column("price_rial", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("duration_days", sa.Integer(), nullable=False, server_default="30"),
        sa.Column("duration", sa.String(length=64), nullable=False, server_default="30 روز"),
        sa.Column("size", sa.String(length=64), nullable=False, server_default="—"),
        sa.Column("panel_id", sa.Integer(), nullable=True),
        sa.Column("panel", sa.String(length=128), nullable=False, server_default="—"),
        sa.Column("code", sa.String(length=64), nullable=False),
        sa.Column("category", sa.String(length=64), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.ForeignKeyConstraint(["panel_id"], ["panels.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
    )

    op.create_table(
        "orders",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("telegram_user_id", sa.BigInteger(), nullable=False),
        sa.Column("user_label", sa.String(length=128), nullable=False),
        sa.Column("order_type", sa.String(length=32), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=True),
        sa.Column("product_name", sa.String(length=255), nullable=False),
        sa.Column("requested_username", sa.String(length=64), nullable=True),
        sa.Column("amount", sa.String(length=64), nullable=False),
        sa.Column("amount_rial", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("method", sa.String(length=64), nullable=False, server_default="کارت به کارت"),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="در انتظار"),
        sa.Column("receipt_path", sa.String(length=512), nullable=True),
        sa.Column("receipt_file_id", sa.String(length=256), nullable=True),
        sa.Column("admin_note", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("processed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_orders_status", "orders", ["status"], unique=False)
    op.create_index("ix_orders_telegram_user_id", "orders", ["telegram_user_id"], unique=False)

    op.create_table(
        "user_services",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("telegram_user_id", sa.BigInteger(), nullable=False),
        sa.Column("order_id", sa.Integer(), nullable=True),
        sa.Column("product_id", sa.Integer(), nullable=True),
        sa.Column("panel_id", sa.Integer(), nullable=True),
        sa.Column("panel_type", sa.String(length=32), nullable=False),
        sa.Column("panel_username", sa.String(length=128), nullable=False),
        sa.Column("subscription_url", sa.String(length=1024), nullable=True),
        sa.Column("config_text", sa.Text(), nullable=True),
        sa.Column("data_gb", sa.Integer(), nullable=False, server_default="10"),
        sa.Column("expire_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="active"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["order_id"], ["orders.id"]),
        sa.ForeignKeyConstraint(["panel_id"], ["panels.id"]),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_user_services_status", "user_services", ["status"], unique=False)
    op.create_index("ix_user_services_telegram_user_id", "user_services", ["telegram_user_id"], unique=False)

    op.create_table(
        "transactions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("user_label", sa.String(length=128), nullable=False),
        sa.Column("hash_value", sa.String(length=64), nullable=False),
        sa.Column("amount", sa.String(length=64), nullable=False),
        sa.Column("method", sa.String(length=64), nullable=False),
        sa.Column("date_label", sa.String(length=64), nullable=False),
        sa.Column("type_label", sa.String(length=32), nullable=False),
        sa.Column("panel", sa.String(length=128), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "discount_codes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(length=64), nullable=False),
        sa.Column("amount", sa.String(length=64), nullable=False),
        sa.Column("type_label", sa.String(length=32), nullable=False),
        sa.Column("used_label", sa.String(length=32), nullable=False),
        sa.Column("valid_until", sa.String(length=32), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
    )


def downgrade() -> None:
    op.drop_table("discount_codes")
    op.drop_table("transactions")
    op.drop_index("ix_user_services_telegram_user_id", table_name="user_services")
    op.drop_index("ix_user_services_status", table_name="user_services")
    op.drop_table("user_services")
    op.drop_index("ix_orders_telegram_user_id", table_name="orders")
    op.drop_index("ix_orders_status", table_name="orders")
    op.drop_table("orders")
    op.drop_table("products")
    op.drop_index("ix_panels_code_panel", table_name="panels")
    op.drop_table("panels")
    op.drop_index("ix_admin_users_username", table_name="admin_users")
    op.drop_table("admin_users")
    op.drop_index("ix_users_telegram_id", table_name="users")
    op.drop_table("users")
