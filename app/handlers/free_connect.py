from __future__ import annotations

import re

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.handlers.start import START_TEXT
from app.keyboards.main import back_menu_keyboard, cancel_payment_keyboard, main_menu_keyboard
from app.services.backend_client import free_connect_via_api
from app.services.user_service import can_earn_referral_rewards, get_user_by_telegram_id
from app.states.free_connect import FreeConnectState
from app.utils.callback_ui import edit_callback_message
from app.utils.security import main_cb

router = Router()

_USERNAME_INPUT_RE = re.compile(r"^[a-zA-Z0-9_]{3,24}$")


@router.callback_query(main_cb.filter(F.action == "free_connect"))
async def on_free_connect(callback: CallbackQuery, session: AsyncSession, state: FSMContext) -> None:
    user = await get_user_by_telegram_id(session, callback.from_user.id)
    if not can_earn_referral_rewards(user):
        await callback.answer("ابتدا حساب خود را تأیید کنید.", show_alert=True)
        return

    await state.set_state(FreeConnectState.waiting_username)
    await edit_callback_message(
        callback,
        "🎁 اتصال رایگان\n\n"
        "👤 نام کاربری دلخواه خود را وارد کنید:\n"
        "(فقط حروف انگلیسی، عدد و _ — ۳ تا ۲۴ کاراکتر)",
        reply_markup=cancel_payment_keyboard(),
    )
    await callback.answer()


@router.message(FreeConnectState.waiting_username, F.text)
async def on_free_connect_username(message: Message, session: AsyncSession, state: FSMContext) -> None:
    raw = (message.text or "").strip()
    if not _USERNAME_INPUT_RE.match(raw):
        await message.answer("نام کاربری نامعتبر است. فقط a-z، A-Z، 0-9 و _ (۳ تا ۲۴ کاراکتر).")
        return

    try:
        result = await free_connect_via_api(message.from_user.id, raw.lower())
    except RuntimeError as exc:
        await message.answer(str(exc), reply_markup=main_menu_keyboard())
        await state.clear()
        return

    await state.clear()
    username = result.get("username", raw.lower())
    await message.answer(
        f"✅ اتصال رایگان فعال شد.\n"
        f"👤 نام کاربری: <code>{username}</code>\n"
        "جزئیات سرویس در پیام بعدی ارسال می‌شود.",
        parse_mode="HTML",
        reply_markup=main_menu_keyboard(),
    )


@router.message(FreeConnectState.waiting_username)
async def on_free_connect_username_invalid(message: Message) -> None:
    await message.answer("لطفاً نام کاربری را به صورت متن انگلیسی ارسال کنید.")


@router.callback_query(main_cb.filter(F.action == "cancel_payment"), FreeConnectState.waiting_username)
async def on_free_connect_cancel(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await edit_callback_message(callback, START_TEXT, reply_markup=main_menu_keyboard())
    await callback.answer()
