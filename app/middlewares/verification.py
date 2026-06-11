from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, TelegramObject

from app.database.session import AsyncSessionLocal
from app.services.user_service import can_earn_referral_rewards, get_user_by_telegram_id
from app.utils.security import main_cb, service_cb

PROTECTED_ACTIONS = frozenset({
    "profile",
    "referral",
    "my_services",
    "free_connect",
    "buy_service",
    "topup_balance",
    "select_product",
})

SERVICE_PROTECTED = frozenset({"view", "sub_link", "config_link", "delete", "renew", "back_list"})


class VerificationMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        if not isinstance(event, CallbackQuery) or not event.data:
            return await handler(event, data)

        action: str | None = None
        protected = False
        try:
            if event.data.startswith("pc:"):
                action = main_cb.parse(event.data).get("action")
                protected = action in PROTECTED_ACTIONS
            elif event.data.startswith("svc:"):
                action = service_cb.parse(event.data).get("action")
                protected = action in SERVICE_PROTECTED
        except Exception:
            return await handler(event, data)

        if not protected:
            return await handler(event, data)

        async with AsyncSessionLocal() as session:
            user = await get_user_by_telegram_id(session, event.from_user.id)

        if not can_earn_referral_rewards(user):
            await event.answer(
                "برای استفاده از این بخش ابتدا عضو کانال شوید و حساب خود را با ارسال شماره تأیید کنید.",
                show_alert=True,
            )
            return

        return await handler(event, data)
