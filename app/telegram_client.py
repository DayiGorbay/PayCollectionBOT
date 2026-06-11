from __future__ import annotations

import logging

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.enums import ParseMode

from app.config import settings
from app.utils.proxy import redact_proxy_url, validate_proxy_url

logger = logging.getLogger(__name__)


def create_bot() -> Bot:
    session: AiohttpSession | None = None

    if settings.BOT_PROXY_ENABLED:
        if not settings.BOT_PROXY_URL:
            raise ValueError("BOT_PROXY_ENABLED=true but BOT_PROXY_URL is empty.")
        validate_proxy_url(settings.BOT_PROXY_URL)
        session = AiohttpSession(proxy=settings.BOT_PROXY_URL)
        logger.info(
            "Telegram proxy enabled — all Bot API requests use proxy (%s)",
            redact_proxy_url(settings.BOT_PROXY_URL),
        )
    else:
        logger.info("Telegram proxy disabled — direct Bot API connection")

    return Bot(
        token=settings.BOT_TOKEN,
        session=session,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )


async def check_telegram_connection(bot: Bot, *, log_failure: bool = False) -> tuple[bool, str | None]:
    try:
        me = await bot.get_me()
        return True, me.username
    except Exception as exc:
        if log_failure:
            if settings.BOT_PROXY_ENABLED:
                logger.error(
                    "Telegram API unreachable via proxy (%s): %s",
                    redact_proxy_url(settings.BOT_PROXY_URL),
                    exc,
                )
            else:
                logger.error("Telegram API unreachable: %s", exc)
        return False, str(exc)


async def verify_telegram_connection(bot: Bot) -> tuple[bool, str | None]:
    return await check_telegram_connection(bot, log_failure=True)
