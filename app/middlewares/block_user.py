from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject

from app.services.user_service import get_user_by_telegram_id


class BlockUserMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        user_id = None
        if isinstance(event, Message) and event.from_user:
            user_id = event.from_user.id
        elif isinstance(event, CallbackQuery) and event.from_user:
            user_id = event.from_user.id

        if user_id is None:
            return await handler(event, data)

        session = data.get("session")
        if session is None:
            return await handler(event, data)

        user = await get_user_by_telegram_id(session, user_id)
        if user is not None and getattr(user, "is_blocked", False):
            text = "⛔️ حساب شما مسدود شده است. برای پیگیری با پشتیبانی تماس بگیرید."
            if isinstance(event, Message):
                await event.answer(text)
            elif isinstance(event, CallbackQuery):
                await event.answer(text, show_alert=True)
            return

        return await handler(event, data)
