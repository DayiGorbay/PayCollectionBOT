from __future__ import annotations

from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery, InlineKeyboardMarkup


async def edit_callback_message(
    callback: CallbackQuery,
    text: str,
    *,
    reply_markup: InlineKeyboardMarkup | None = None,
    parse_mode: str | None = None,
) -> None:
    """Edit the callback's source message instead of sending a new one."""
    message = callback.message
    if message is None:
        return

    kwargs: dict = {}
    if reply_markup is not None:
        kwargs["reply_markup"] = reply_markup
    if parse_mode is not None:
        kwargs["parse_mode"] = parse_mode

    try:
        if message.text is not None:
            await message.edit_text(text, **kwargs)
            return
        if message.caption is not None:
            await message.edit_caption(caption=text, **kwargs)
            return
    except TelegramBadRequest as exc:
        if "message is not modified" in str(exc).lower():
            return
        raise

    await message.answer(text, **kwargs)
