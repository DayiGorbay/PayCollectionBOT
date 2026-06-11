"""Deprecated: use Alembic migrations in backend/alembic/ instead."""

from __future__ import annotations

import logging

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

logger = logging.getLogger(__name__)


async def run_migrations(engine: AsyncEngine) -> None:
    async with engine.begin() as conn:
        await _migrate_users_columns(conn)
        await _migrate_products_columns(conn)
        await _migrate_orders_table(conn)
        await _migrate_panels_table(conn)
        await _migrate_products_panel_link(conn)
        await _migrate_orders_username(conn)
        await _migrate_user_services_table(conn)
        await _migrate_panels_provider_fields(conn)


async def _migrate_users_columns(conn) -> None:
    statements = [
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS referral_finalized_at TIMESTAMPTZ",
    ]
    for stmt in statements:
        try:
            await conn.execute(text(stmt))
        except Exception as exc:
            logger.debug("Migration skip: %s (%s)", stmt, exc)


async def _migrate_products_columns(conn) -> None:
    statements = [
        "ALTER TABLE products ADD COLUMN IF NOT EXISTS price_rial INTEGER DEFAULT 0",
        "ALTER TABLE products ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE",
    ]
    for stmt in statements:
        try:
            await conn.execute(text(stmt))
        except Exception as exc:
            logger.debug("Migration skip: %s (%s)", stmt, exc)


async def _migrate_orders_table(conn) -> None:
    """جدول orders قدیمی (seed) را به schema جدید تبدیل می‌کند."""
    check = await conn.execute(
        text(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_name = 'orders' AND column_name = 'telegram_user_id'"
        )
    )
    if check.first() is not None:
        return

    has_old = await conn.execute(
        text(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_name = 'orders' AND column_name = 'user_label'"
        )
    )
    if has_old.first() is not None:
        await conn.execute(text("DROP TABLE IF EXISTS orders CASCADE"))
        logger.info("Dropped legacy orders table for migration")

    await conn.execute(
        text(
            """
            CREATE TABLE IF NOT EXISTS orders (
                id SERIAL PRIMARY KEY,
                telegram_user_id BIGINT NOT NULL,
                user_label VARCHAR(128) NOT NULL,
                order_type VARCHAR(32) NOT NULL,
                product_id INTEGER REFERENCES products(id),
                product_name VARCHAR(255) NOT NULL,
                amount VARCHAR(64) NOT NULL,
                amount_rial INTEGER NOT NULL DEFAULT 0,
                method VARCHAR(64) DEFAULT 'کارت به کارت',
                status VARCHAR(32) DEFAULT 'در انتظار',
                receipt_path VARCHAR(512),
                receipt_file_id VARCHAR(256),
                admin_note TEXT,
                created_at TIMESTAMPTZ DEFAULT NOW(),
                processed_at TIMESTAMPTZ
            )
            """
        )
    )
    await conn.execute(text("CREATE INDEX IF NOT EXISTS ix_orders_telegram_user_id ON orders (telegram_user_id)"))
    await conn.execute(text("CREATE INDEX IF NOT EXISTS ix_orders_status ON orders (status)"))


async def _migrate_panels_table(conn) -> None:
    """ارتقای جدول panels برای Marzban و x-ui."""
    check = await conn.execute(
        text(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_name = 'panels' AND column_name = 'code_panel'"
        )
    )
    if check.first() is not None:
        return

    has_old = await conn.execute(
        text("SELECT 1 FROM information_schema.tables WHERE table_name = 'panels'")
    )
    if has_old.first() is not None:
        await conn.execute(text("DROP TABLE IF EXISTS panels CASCADE"))
        logger.info("Dropped legacy panels table for migration")

    await conn.execute(
        text(
            """
            CREATE TABLE IF NOT EXISTS panels (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                code_panel VARCHAR(64) NOT NULL UNIQUE,
                api_url VARCHAR(512) NOT NULL,
                panel_type VARCHAR(32) NOT NULL,
                username_panel VARCHAR(128) NOT NULL,
                password_panel VARCHAR(255) NOT NULL,
                status VARCHAR(32) NOT NULL DEFAULT 'فعال',
                last_sync_at TIMESTAMPTZ,
                datelogin TEXT,
                version_panel VARCHAR(16) DEFAULT 'legacy',
                inbounds TEXT,
                proxies TEXT,
                on_hold_test BOOLEAN DEFAULT FALSE,
                connection_mode VARCHAR(32) DEFAULT 'offconecton',
                inbound_id INTEGER,
                created_at TIMESTAMPTZ DEFAULT NOW()
            )
            """
        )
    )
    await conn.execute(text("CREATE INDEX IF NOT EXISTS ix_panels_code_panel ON panels (code_panel)"))


async def _migrate_orders_username(conn) -> None:
    try:
        await conn.execute(text("ALTER TABLE orders ADD COLUMN IF NOT EXISTS requested_username VARCHAR(64)"))
    except Exception as exc:
        logger.debug("Migration skip: requested_username (%s)", exc)


async def _migrate_user_services_table(conn) -> None:
    await conn.execute(
        text(
            """
            CREATE TABLE IF NOT EXISTS user_services (
                id SERIAL PRIMARY KEY,
                telegram_user_id BIGINT NOT NULL,
                order_id INTEGER REFERENCES orders(id),
                product_id INTEGER REFERENCES products(id),
                panel_id INTEGER REFERENCES panels(id),
                panel_type VARCHAR(32) NOT NULL,
                panel_username VARCHAR(128) NOT NULL,
                subscription_url VARCHAR(1024),
                config_text TEXT,
                data_gb INTEGER NOT NULL DEFAULT 10,
                expire_at TIMESTAMPTZ,
                status VARCHAR(32) DEFAULT 'active',
                created_at TIMESTAMPTZ DEFAULT NOW()
            )
            """
        )
    )
    await conn.execute(
        text("CREATE INDEX IF NOT EXISTS ix_user_services_telegram_user_id ON user_services (telegram_user_id)")
    )
    await conn.execute(text("CREATE INDEX IF NOT EXISTS ix_user_services_status ON user_services (status)"))


async def _migrate_panels_provider_fields(conn) -> None:
    statements = [
        "ALTER TABLE panels ADD COLUMN IF NOT EXISTS auth_mode VARCHAR(32) DEFAULT 'bearer'",
        "ALTER TABLE panels ADD COLUMN IF NOT EXISTS api_token VARCHAR(512)",
        "ALTER TABLE panels ADD COLUMN IF NOT EXISTS auth_cache TEXT",
    ]
    for stmt in statements:
        try:
            await conn.execute(text(stmt))
        except Exception as exc:
            logger.debug("Migration skip: %s (%s)", stmt, exc)
    try:
        await conn.execute(
            text(
                "UPDATE panels SET auth_cache = datelogin "
                "WHERE auth_cache IS NULL AND datelogin IS NOT NULL"
            )
        )
    except Exception as exc:
        logger.debug("Migration skip auth_cache copy (%s)", exc)


async def _migrate_products_panel_link(conn) -> None:
    statements = [
        "ALTER TABLE products ADD COLUMN IF NOT EXISTS panel_id INTEGER REFERENCES panels(id)",
        "ALTER TABLE products ADD COLUMN IF NOT EXISTS duration_days INTEGER DEFAULT 30",
        "ALTER TABLE products ADD COLUMN IF NOT EXISTS code VARCHAR(64)",
    ]
    for stmt in statements:
        try:
            await conn.execute(text(stmt))
        except Exception as exc:
            logger.debug("Migration skip: %s (%s)", stmt, exc)
