from __future__ import annotations

import logging

import httpx

from app.config import get_settings
from app.utils.qrcode_util import make_qr_png_bytes

logger = logging.getLogger(__name__)


async def send_telegram_text(telegram_id: int, text: str, *, parse_mode: str = "HTML") -> None:
    settings = get_settings()
    if not settings.BOT_TOKEN:
        logger.warning("BOT_TOKEN not set; skipping Telegram notification")
        return
    url = f"https://api.telegram.org/bot{settings.BOT_TOKEN}/sendMessage"
    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            await client.post(
                url,
                json={"chat_id": telegram_id, "text": text, "parse_mode": parse_mode},
            )
    except Exception as exc:
        logger.exception("Failed to notify user %s: %s", telegram_id, exc)


async def send_telegram_photo(
    telegram_id: int,
    *,
    photo_bytes: bytes,
    caption: str,
    parse_mode: str = "HTML",
) -> None:
    settings = get_settings()
    if not settings.BOT_TOKEN:
        logger.warning("BOT_TOKEN not set; skipping Telegram photo")
        return
    url = f"https://api.telegram.org/bot{settings.BOT_TOKEN}/sendPhoto"
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            await client.post(
                url,
                data={"chat_id": str(telegram_id), "caption": caption, "parse_mode": parse_mode},
                files={"photo": ("qr.png", photo_bytes, "image/png")},
            )
    except Exception as exc:
        logger.exception("Failed to send photo to user %s: %s", telegram_id, exc)


async def send_service_activation_message(
    telegram_id: int,
    *,
    username: str,
    data_gb: int,
    subscription_url: str,
    config_text: str | None = None,
) -> None:
    text = (
        "از اعتماد شما به مجموعه پِی سپاس گذاریم 🙏\n\n"
        "✨ اطلاعات سرویس شما به شرح زیر میباشد:\n\n"
        f"👤نام کاربری: <code>{username}</code>\n"
        f"🌐حجم سرویس: {data_gb} گیگابایت\n"
        "🔗 لینک سرویس:\n"
        f"<pre>{subscription_url}</pre>\n\n"
        "🔴 لینک سرویس خود را تحت هیچ عنوان برای دیگران به اشتراک نذارید❗️"
    )
    qr_target = subscription_url or config_text or ""
    if qr_target:
        caption = (
            "از اعتماد شما به مجموعه پِی سپاس گذاریم 🙏\n\n"
            f"👤 نام کاربری: {username}\n"
            f"🌐 حجم: {data_gb} گیگابایت\n"
            "QR لینک سابسکریپشن 👇"
        )
        await send_telegram_photo(
            telegram_id,
            photo_bytes=make_qr_png_bytes(qr_target),
            caption=caption,
        )
    await send_telegram_text(telegram_id, text)
