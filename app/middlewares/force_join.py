from __future__ import annotations

from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.types import CallbackQuery, Message, Update

from app.config import settings
from app.database.session import AsyncSessionLocal
from app.keyboards.main import force_join_keyboard
from app.services.user_service import get_or_create_user, mark_channel_joined
from app.utils.security import main_cb
from app.utils.telegram import get_channel_chat_id, is_channel_member


ALLOWED_ACTIONS = {"check_join", "solve_captcha", "help"}
ALLOWED_COMMANDS = {"/start", "/help"}


class ForceJoinMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        update: Update | None = data.get("update")
        if update is None:
            return await handler(event, data)

        user_id = None
        if update.message:
            user_id = update.message.from_user.id
            if update.message.text:
                command = update.message.text.strip().split()[0]
                if command in ALLOWED_COMMANDS:
                    return await handler(event, data)

        if update.callback_query:
            user_id = update.callback_query.from_user.id
            try:
                payload = main_cb.parse(update.callback_query.data or "")
                action = payload.get("action")
            except Exception:
                action = None

            if action in ALLOWED_ACTIONS:
                return await handler(event, data)

        if user_id is None:
            return await handler(event, data)

        async with AsyncSessionLocal() as session:
            user = await get_or_create_user(
                session,
                update.message.from_user if update.message else update.callback_query.from_user,
            )

            channel_chat_id = get_channel_chat_id(
                settings.CHANNEL_ID,
                settings.CHANNEL_LINK,
                settings.CHANNEL_USERNAME,
            )
            if not channel_chat_id:
                return await handler(event, data)

            is_member = await is_channel_member(
                update.message.bot if update.message else update.callback_query.bot,
                channel_chat_id,
                user_id,
            )

            if is_member:
                if not user.joined_channel:
                    await mark_channel_joined(session, user)
                return await handler(event, data)

            prompt = (
                "🚫 برای استفاده از ربات ابتدا باید عضو کانال ما شوید.\n\n"
                "برای ادامه ابتدا روی دکمه عضویت در کانال کلیک کنید و سپس بررسی عضویت را بزنید."
            )
            if update.message:
                await update.message.answer(
                    prompt,
                    reply_markup=force_join_keyboard(settings.CHANNEL_LINK),
                )
            elif update.callback_query and update.callback_query.message:
                await update.callback_query.message.answer(
                    prompt,
                    reply_markup=force_join_keyboard(settings.CHANNEL_LINK),
                )
                await update.callback_query.answer()

        return
