"""service sync fields and order link

Revision ID: 003_service_sync_fields
Revises: 002_admin_bot_features
Create Date: 2026-06-15

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "003_service_sync_fields"
down_revision: Union[str, None] = "002_admin_bot_features"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("user_services", sa.Column("user_id", sa.Integer(), nullable=True))
    op.add_column("user_services", sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("user_services", sa.Column("data_limit_bytes", sa.BigInteger(), nullable=True))
    op.add_column(
        "user_services",
        sa.Column("used_traffic_bytes", sa.BigInteger(), nullable=False, server_default="0"),
    )
    op.add_column("user_services", sa.Column("remaining_traffic_bytes", sa.BigInteger(), nullable=True))
    op.add_column("user_services", sa.Column("panel_user_status", sa.String(length=32), nullable=True))
    op.add_column("user_services", sa.Column("online_status", sa.String(length=32), nullable=True))
    op.add_column("user_services", sa.Column("last_online_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("user_services", sa.Column("last_synced_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("user_services", sa.Column("inbounds_cache", sa.Text(), nullable=True))
    op.create_foreign_key(
        "fk_user_services_user_id",
        "user_services",
        "users",
        ["user_id"],
        ["id"],
    )

    op.add_column("orders", sa.Column("service_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        "fk_orders_service_id",
        "orders",
        "user_services",
        ["service_id"],
        ["id"],
    )


def downgrade() -> None:
    op.drop_constraint("fk_orders_service_id", "orders", type_="foreignkey")
    op.drop_column("orders", "service_id")
    op.drop_constraint("fk_user_services_user_id", "user_services", type_="foreignkey")
    op.drop_column("user_services", "inbounds_cache")
    op.drop_column("user_services", "last_synced_at")
    op.drop_column("user_services", "last_online_at")
    op.drop_column("user_services", "online_status")
    op.drop_column("user_services", "panel_user_status")
    op.drop_column("user_services", "remaining_traffic_bytes")
    op.drop_column("user_services", "used_traffic_bytes")
    op.drop_column("user_services", "data_limit_bytes")
    op.drop_column("user_services", "updated_at")
    op.drop_column("user_services", "user_id")
