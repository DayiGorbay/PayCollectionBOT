"""Static import check for the Telegram bot (no BOT_TOKEN required)."""

from __future__ import annotations

import importlib
import sys


MODULES = [
    "app.handlers.start",
    "app.handlers.captcha",
    "app.handlers.shop",
    "app.handlers.services",
    "app.handlers.profile",
    "app.middlewares.db_session",
    "app.middlewares.rate_limit",
    "app.middlewares.force_join",
    "app.middlewares.verification",
    "app.keyboards.main",
    "app.keyboards.services",
    "app.states.registration",
    "app.states.shop",
    "app.utils.security",
    "app.utils.files",
    "app.telegram_client",
]


def main() -> int:
    errors: list[str] = []
    for name in MODULES:
        try:
            importlib.import_module(name)
        except Exception as exc:  # noqa: BLE001
            errors.append(f"{name}: {exc}")

    from aiogram.filters.callback_data import CallbackData

    if hasattr(CallbackData, "parse"):
        errors.append("aiogram.CallbackData still exposes deprecated .parse() — review usage")

    from app.handlers import register_routers
    from aiogram import Dispatcher
    from aiogram.fsm.storage.memory import MemoryStorage

    dp = Dispatcher(storage=MemoryStorage())
    register_routers(dp)
    router_count = len(dp.sub_routers)
    if router_count != 5:
        errors.append(f"Expected 5 routers, got {router_count}")

    if errors:
        print("Bot import verification FAILED:")
        for err in errors:
            print(f"  - {err}")
        return 1

    print(f"Bot import verification OK ({router_count} routers registered)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
