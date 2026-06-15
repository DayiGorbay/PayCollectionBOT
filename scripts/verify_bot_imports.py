"""Static import check for the Telegram bot (no BOT_TOKEN required)."""

from __future__ import annotations

import importlib
import sys


MODULES = [
    "app.config",
    "app.database.session",
    "app.models.user",
    "app.models.order",
    "app.models.product",
    "app.models.user_service",
    "app.models.discount",
    "app.models.bot_setting",
    "app.models.panel",
    "app.services.backend_client",
    "app.services.user_service",
    "app.services.order_service",
    "app.services.product_service",
    "app.services.service_service",
    "app.services.discount_service",
    "app.services.bot_config_service",
    "app.handlers.start",
    "app.handlers.captcha",
    "app.handlers.free_connect",
    "app.handlers.shop",
    "app.handlers.services",
    "app.handlers.profile",
    "app.middlewares.db_session",
    "app.middlewares.block_user",
    "app.middlewares.rate_limit",
    "app.middlewares.force_join",
    "app.middlewares.verification",
    "app.keyboards.main",
    "app.keyboards.services",
    "app.states.registration",
    "app.states.shop",
    "app.states.free_connect",
    "app.utils.security",
    "app.utils.files",
    "app.utils.callback_ui",
    "app.utils.telegram",
    "app.telegram_client",
    "bot",
]

EXPECTED_ROUTERS = 6


def main() -> int:
    errors: list[str] = []
    for name in MODULES:
        try:
            importlib.import_module(name)
        except Exception as exc:  # noqa: BLE001
            errors.append(f"{name}: {exc}")

    from app.handlers import register_routers
    from aiogram import Dispatcher
    from aiogram.fsm.storage.memory import MemoryStorage

    dp = Dispatcher(storage=MemoryStorage())
    register_routers(dp)
    router_count = len(dp.sub_routers)
    if router_count != EXPECTED_ROUTERS:
        errors.append(f"Expected {EXPECTED_ROUTERS} routers, got {router_count}")

    from app.services import backend_client

    for fn_name in (
        "free_connect_via_api",
        "approve_order_via_api",
        "delete_user_service_via_api",
        "list_user_services_via_api",
        "get_user_service_via_api",
    ):
        if not callable(getattr(backend_client, fn_name, None)):
            errors.append(f"app.services.backend_client missing callable: {fn_name}")

    if errors:
        print("Bot import verification FAILED:")
        for err in errors:
            print(f"  - {err}")
        return 1

    print(f"Bot import verification OK ({router_count} routers registered)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
