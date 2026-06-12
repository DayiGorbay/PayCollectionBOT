from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject

from app.config import settings
from app.database.session import AsyncSessionLocal
from app.keyboards.main import force_join_keyboard
from app.services.user_service import get_or_create_user, mark_channel_joined
from app.utils.security import main_cb
from app.utils.telegram import get_channel_chat_id, is_channel_configured, is_channel_member


ALLOWED_ACTIONS = frozenset({"check_join", "solve_captcha", "help"})
ALLOWED_COMMANDS = frozenset({"/start", "/help"})


class ForceJoinMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: TelegramObject, data: dict[str, Any]):
        if isinstance(event, Message) and event.text:
            command = event.text.strip().split()[0]
            if command in ALLOWED_COMMANDS:
                return await handler(event, data)

        if isinstance(event, CallbackQuery):
            try:
                payload = main_cb.unpack(event.data or "")
                action = payload.action
            except Exception:
                action = None

            if action in ALLOWED_ACTIONS:
                return await handler(event, data)

        channel_chat_id = get_channel_chat_id(
            settings.CHANNEL_ID,
            settings.CHANNEL_LINK,
            settings.CHANNEL_USERNAME,
        )

        if not is_channel_configured(settings.CHANNEL_ID, settings.CHANNEL_LINK, settings.CHANNEL_USERNAME):
            if settings.REQUIRE_CHANNEL_JOIN:
                msg = "⚠️ ربات هنوز کانال اجباری را پیکربندی نکرده است. لطفاً بعداً تلاش کنید."
                if isinstance(event, Message):
                    await event.answer(msg)
                elif isinstance(event, CallbackQuery):
                    await event.answer(msg, show_alert=True)
                return
            return await handler(event, data)

        user_id = event.from_user.id if event.from_user else None
        tg_user = event.from_user
        bot = event.bot

        if not user_id or not tg_user or not bot:
            return await handler(event, data)

        async with AsyncSessionLocal() as session:
            user = await get_or_create_user(session, tg_user)
            is_member = await is_channel_member(bot, channel_chat_id, user_id)

            if is_member:
                if not user.joined_channel:
                    await mark_channel_joined(session, user)
                return await handler(event, data)

                prompt = (
            		"🚫 برای استفاده از ربات ابتدا باید عضو کانال ما شوید.\n\n"
            		"برای ادامه ابتدا روی دکمه عضویت در کانال کلیک کنید و سپس بررسی عضویت را بزنید."
       	 )
        if isinstance(event, Message):
            await event.answer(prompt, reply_markup=force_join_keyboard(settings.CHANNEL_LINK))
        elif isinstance(event, CallbackQuery) and event.message:
            await event.message.answer(prompt, reply_markup=force_join_keyboard(settings.CHANNEL_LINK))
            await event.answer()
