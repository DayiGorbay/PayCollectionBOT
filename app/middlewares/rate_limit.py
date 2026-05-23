from __future__ import annotations

import time

from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.types import CallbackQuery, Message, Update


class RateLimitMiddleware(BaseMiddleware):
    def __init__(self, limit: float = 1.0) -> None:
        self.limit = limit
        self.timestamps: dict[int, float] = {}
        super().__init__()

    async def __call__(self, handler, event, data):
        update: Update | None = data.get("update")
        if update is None:
            return await handler(event, data)

        user_id = None
        if update.message:
            user_id = update.message.from_user.id
        elif update.callback_query:
            user_id = update.callback_query.from_user.id

        if user_id is None:
            return await handler(event, data)

        now = time.monotonic()
        last = self.timestamps.get(user_id, 0)
        if now - last < self.limit:
            if update.callback_query:
                await update.callback_query.answer("لطفا کمی صبر کنید و دوباره تلاش کنید.", show_alert=True)
            elif update.message:
                await update.message.answer("لطفاً کمی صبر کنید و دوباره تلاش کنید.")
            return

        self.timestamps[user_id] = now
        return await handler(event, data)
