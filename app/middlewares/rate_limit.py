from __future__ import annotations

import time
from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject

ENTRY_TTL_SECONDS = 3600


class RateLimitMiddleware(BaseMiddleware):
    def __init__(self, limit: float = 1.0, burst_limit: float = 3.0) -> None:
        self.limit = limit
        self.burst_limit = burst_limit
        self.timestamps: dict[int, float] = {}
        self.check_join_timestamps: dict[int, float] = {}

    def _prune(self, store: dict[int, float], now: float) -> None:
        stale = [uid for uid, ts in store.items() if now - ts > ENTRY_TTL_SECONDS]
        for uid in stale:
            del store[uid]

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        user_id = None
        is_check_join = False
        callback: CallbackQuery | None = None
        message: Message | None = None

        if isinstance(event, Message):
            message = event
            user_id = message.from_user.id if message.from_user else None
        elif isinstance(event, CallbackQuery):
            callback = event
            user_id = callback.from_user.id
            is_check_join = "check_join" in (callback.data or "")

        if user_id is None:
            return await handler(event, data)

        now = time.monotonic()
        self._prune(self.timestamps, now)
        self._prune(self.check_join_timestamps, now)

        if is_check_join and callback:
            last = self.check_join_timestamps.get(user_id, 0)
            if now - last < self.burst_limit:
                await callback.answer(
                    "لطفاً چند ثانیه صبر کنید و دوباره بررسی عضویت را بزنید.",
                    show_alert=True,
                )
                return
            self.check_join_timestamps[user_id] = now

        last = self.timestamps.get(user_id, 0)
        if now - last < self.limit:
            if callback:
                await callback.answer("لطفا کمی صبر کنید و دوباره تلاش کنید.", show_alert=True)
            elif message:
                await message.answer("لطفاً کمی صبر کنید و دوباره تلاش کنید.")
            return

        self.timestamps[user_id] = now
        return await handler(event, data)
