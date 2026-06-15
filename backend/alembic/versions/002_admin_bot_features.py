"""admin bot features

Revision ID: 002_admin_bot_features
Revises: 001_initial
Create Date: 2026-06-14

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "002_admin_bot_features"
down_revision: Union[str, None] = "001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("is_blocked", sa.Boolean(), nullable=False, server_default=sa.text("false")))

    op.add_column("orders", sa.Column("discount_code", sa.String(length=64), nullable=True))
    op.add_column("orders", sa.Column("discount_amount_rial", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("orders", sa.Column("original_amount_rial", sa.Integer(), nullable=True))
    op.add_column("orders", sa.Column("wallet_paid_rial", sa.Integer(), nullable=False, server_default="0"))

    op.add_column("discount_codes", sa.Column("discount_percent", sa.Integer(), nullable=True))
    op.add_column("discount_codes", sa.Column("discount_amount_rial", sa.Integer(), nullable=True))
    op.add_column("discount_codes", sa.Column("max_uses", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("discount_codes", sa.Column("used_count", sa.Integer(), nullable=False, server_default="0"))

    op.create_table(
        "bot_settings",
        sa.Column("key", sa.String(length=64), nullable=False),
        sa.Column("value", sa.Text(), nullable=False, server_default=""),
        sa.PrimaryKeyConstraint("key"),
    )

    op.create_table(
        "free_connect_config",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("coins_required", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("data_gb", sa.Integer(), nullable=False, server_default="10"),
        sa.Column("panel_id", sa.Integer(), nullable=True),
        sa.Column("duration_days", sa.Integer(), nullable=False, server_default="30"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.ForeignKeyConstraint(["panel_id"], ["panels.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.execute(
        "INSERT INTO free_connect_config (id, coins_required, data_gb, duration_days, is_active) VALUES (1, 5, 10, 30, false)"
    )


def downgrade() -> None:
    op.drop_table("free_connect_config")
    op.drop_table("bot_settings")
    op.drop_column("discount_codes", "used_count")
    op.drop_column("discount_codes", "max_uses")
    op.drop_column("discount_codes", "discount_amount_rial")
    op.drop_column("discount_codes", "discount_percent")
    op.drop_column("orders", "wallet_paid_rial")
    op.drop_column("orders", "original_amount_rial")
    op.drop_column("orders", "discount_amount_rial")
    op.drop_column("orders", "discount_code")
    op.drop_column("users", "is_blocked")
