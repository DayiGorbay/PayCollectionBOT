import asyncio
import logging
import os

from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from app.config import settings
from app.handlers import register_routers
from app.middlewares.db_session import DbSessionMiddleware
from app.middlewares.force_join import ForceJoinMiddleware
from app.middlewares.rate_limit import RateLimitMiddleware
from app.middlewares.verification import VerificationMiddleware
from app.models.order import Order  # noqa: F401
from app.models.panel import Panel  # noqa: F401
from app.models.product import Product  # noqa: F401
from app.models.user import Base  # noqa: F401
from app.models.user_service import UserService  # noqa: F401
from app.telegram_client import check_telegram_connection, create_bot, verify_telegram_connection
from app.utils.proxy import redact_proxy_url

logging.basicConfig(
    level=settings.LOG_LEVEL,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

HEALTH_HOST = os.getenv("BOT_HEALTH_HOST", "0.0.0.0")
HEALTH_PORT = int(os.getenv("BOT_HEALTH_PORT", "8090"))

_bot: Bot | None = None


async def health_handler(_: web.Request) -> web.Response:
    if _bot is None:
        return web.json_response(
            {
                "status": "unavailable",
                "service": "bot",
                "telegram": {"ok": False, "error": "bot not initialized"},
                "proxy": {"enabled": settings.BOT_PROXY_ENABLED},
            },
            status=503,
        )

    telegram_ok, detail = await check_telegram_connection(_bot)
    payload = {
        "status": "ok" if telegram_ok else "degraded",
        "service": "bot",
        "telegram": {
            "ok": telegram_ok,
            "username": detail if telegram_ok else None,
            "error": None if telegram_ok else detail,
        },
        "proxy": {
            "enabled": settings.BOT_PROXY_ENABLED,
            "url": redact_proxy_url(settings.BOT_PROXY_URL) if settings.BOT_PROXY_ENABLED else None,
            "ok": telegram_ok if settings.BOT_PROXY_ENABLED else None,
        },
    }
    return web.json_response(payload, status=200 if telegram_ok else 503)


async def start_health_server() -> web.AppRunner:
    app = web.Application()
    app.router.add_get("/health", health_handler)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, HEALTH_HOST, HEALTH_PORT)
    await site.start()
    logger.info("Bot health server listening on %s:%s", HEALTH_HOST, HEALTH_PORT)
    return runner


async def main() -> None:
    global _bot

    if not settings.BOT_TOKEN:
        logger.critical("BOT_TOKEN در .env تعریف نشده است")
        return

    try:
        _bot = create_bot()
    except ValueError as exc:
        logger.critical("Bot configuration error: %s", exc)
        return

    telegram_ok, username = await verify_telegram_connection(_bot)
    if not telegram_ok:
        logger.critical("Cannot connect to Telegram API — bot will not start polling")
        await _bot.session.close()
        return

    logger.info("Telegram API connection verified (@%s)", username)

    dp = Dispatcher(storage=MemoryStorage())

    dp.message.middleware(DbSessionMiddleware())
    dp.callback_query.middleware(DbSessionMiddleware())
    dp.message.middleware(RateLimitMiddleware())
    dp.callback_query.middleware(RateLimitMiddleware())
    dp.message.middleware(ForceJoinMiddleware())
    dp.callback_query.middleware(ForceJoinMiddleware())
    dp.callback_query.middleware(VerificationMiddleware())

    register_routers(dp)

    health_runner = await start_health_server()
    logger.info("ربات با موفقیت راه‌اندازی شد")
    try:
        await dp.start_polling(_bot)
    finally:
        await health_runner.cleanup()
        await _bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
