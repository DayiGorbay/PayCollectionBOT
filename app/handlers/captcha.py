from __future__ import annotations

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.handlers.start import START_TEXT, VERIFICATION_TEXT
from app.keyboards.main import (
    back_menu_keyboard,
    captcha_keyboard,
    contact_keyboard,
    join_channel_keyboard,
    main_menu_keyboard,
    remove_keyboard,
)
from app.services.user_service import (
    PhoneVerificationResult,
    get_user_by_telegram_id,
    mark_phone_verified,
    try_complete_referral,
)
from app.states.registration import RegistrationState
from app.utils.callback_ui import edit_callback_message
from app.utils.security import main_cb
from app.utils.telegram import get_channel_chat_id, is_channel_member

router = Router()


@router.callback_query(main_cb.filter(F.action == "solve_captcha"))
async def on_solve_captcha(
    callback: CallbackQuery,
    session: AsyncSession,
    state: FSMContext,
) -> None:
    user = await get_user_by_telegram_id(session, callback.from_user.id)
    if user is None:
        await edit_callback_message(callback, "ابتدا با /start وارد شوید.")
        await callback.answer()
        return

    if user.verified and user.phone_number and not user.is_suspicious:
        await callback.answer("حساب شما قبلاً تأیید شده است.", show_alert=True)
        return

    await edit_callback_message(
        callback,
        "برای تایید حساب، روی دکمه «ارسال شماره» در پایین صفحه کلیک کنید 👇",
        reply_markup=None,
    )
    await callback.message.answer(
        "👇",
        reply_markup=contact_keyboard(),
    )
    await state.set_state(RegistrationState.waiting_contact)
    await callback.answer()


@router.message(RegistrationState.waiting_contact, F.contact)
async def on_contact_received(
    message: Message,
    session: AsyncSession,
    state: FSMContext,
) -> None:
    if message.contact is None or message.contact.user_id != message.from_user.id:
        await message.answer("لطفا شماره همان حسابی که وارد شده است را ارسال کنید.")
        return

    user = await get_user_by_telegram_id(session, message.from_user.id)
    if user is None:
        await message.answer("ابتدا با /start وارد شوید.")
        await state.clear()
        return

    result = await mark_phone_verified(session, user, message.contact.phone_number)
    await session.refresh(user)

    if result == PhoneVerificationResult.ALREADY_VERIFIED:
        await message.answer("حساب شما قبلاً تأیید شده است.", reply_markup=remove_keyboard())
        await state.clear()
        return

    if result == PhoneVerificationResult.DUPLICATE:
        await message.answer(
            "شماره تلفن شما قبلا در سیستم ثبت شده است. حساب شما در وضعیت بررسی قرار گرفت.",
            reply_markup=remove_keyboard(),
        )
        await state.clear()
        return

    if result == PhoneVerificationResult.INVALID:
        await message.answer(
            "✅ حساب کاربری شما با موفقیت تایید شد.\n"
            "(به دلیل ایرانی نبودن شماره، زیرمجموعه‌ای برای دعوت‌کننده ثبت نشد) ❗️",
            reply_markup=remove_keyboard(),
        )
        await state.clear()
        return

    if user.invited_by is None:
        await message.answer(
            "حساب کاربری شما با موفقیت تایید شد ✅",
            reply_markup=remove_keyboard(),
        )
        await message.answer(START_TEXT, reply_markup=main_menu_keyboard())
        await state.clear()
        return

    channel_chat_id = get_channel_chat_id(
        settings.CHANNEL_ID,
        settings.CHANNEL_LINK,
        settings.CHANNEL_USERNAME,
    )
    channel_member = await is_channel_member(message.bot, channel_chat_id, user.telegram_id)
    if not channel_member:
        await message.answer(
            "برای تکمیل ثبت نام ابتدا باید عضو کانال شوید.",
            reply_markup=join_channel_keyboard(settings.CHANNEL_LINK),
        )
        await state.set_state(RegistrationState.waiting_channel_join)
        return

    if await try_complete_referral(session, user, channel_member=True):
        await message.answer(
            "حساب کاربری شما با موفقیت تایید شد ✅\nزیر مجموعه شما با موفقیت نهایی شد.",
            reply_markup=remove_keyboard(),
        )
    else:
        await message.answer("حساب کاربری شما با موفقیت تایید شد ✅", reply_markup=remove_keyboard())
    await message.answer(START_TEXT, reply_markup=main_menu_keyboard())
    await state.clear()


@router.message(RegistrationState.waiting_contact)
async def on_contact_invalid(message: Message) -> None:
    await message.answer("لطفا شماره خود را با استفاده از دکمه ارسال شماره ارسال کنید.")


@router.callback_query(main_cb.filter(F.action == "check_join"))
async def on_check_join(
    callback: CallbackQuery,
    session: AsyncSession,
    state: FSMContext,
) -> None:
    user = await get_user_by_telegram_id(session, callback.from_user.id)
    channel_chat_id = get_channel_chat_id(
        settings.CHANNEL_ID,
        settings.CHANNEL_LINK,
        settings.CHANNEL_USERNAME,
    )
    channel_member = await is_channel_member(callback.bot, channel_chat_id, callback.from_user.id)

    if user is None:
        if channel_member:
            await edit_callback_message(
                callback,
                VERIFICATION_TEXT,
                reply_markup=captcha_keyboard(),
            )
        else:
            await edit_callback_message(
                callback,
                "🚫 برای استفاده از ربات ابتدا باید عضو کانال ما شوید.\n\n"
                "برای ادامه ابتدا روی دکمه عضویت در کانال کلیک کنید و سپس بررسی عضویت را بزنید.",
                reply_markup=join_channel_keyboard(settings.CHANNEL_LINK),
            )
        await callback.answer()
        return

    if not user.verified:
        if channel_member:
            await edit_callback_message(
                callback,
                VERIFICATION_TEXT,
                reply_markup=captcha_keyboard(),
            )
        else:
            await edit_callback_message(
                callback,
                "شما هنوز عضو کانال نیستید. لطفاً ابتدا عضو شوید و سپس دوباره بررسی کنید.",
                reply_markup=join_channel_keyboard(settings.CHANNEL_LINK),
            )
        await callback.answer()
        return

    if user.is_suspicious:
        await callback.answer("حساب شما در حال بررسی است و امکان ثبت رفرال وجود ندارد.", show_alert=True)
        return

    if not channel_member:
        await edit_callback_message(
            callback,
            "شما هنوز عضو کانال نیستید. لطفاً ابتدا عضو شوید و سپس دوباره بررسی کنید.",
            reply_markup=join_channel_keyboard(settings.CHANNEL_LINK),
        )
        await callback.answer()
        return

    if user.referral_finalized or not user.invited_by:
        await edit_callback_message(callback, "عضویت شما در کانال تأیید شد. ✅", reply_markup=main_menu_keyboard())
        await state.clear()
        await callback.answer()
        return

    if await try_complete_referral(session, user, channel_member=True):
        await edit_callback_message(
            callback,
            "عضویت شما در کانال تایید شد و رفرال نهایی شد. ✅",
            reply_markup=main_menu_keyboard(),
        )
    else:
        await edit_callback_message(
            callback,
            "عضویت شما تأیید شد. رفرال قابل ثبت نبود (شرایط احراز یا سقف روزانه).",
            reply_markup=main_menu_keyboard(),
        )
    await state.clear()
    await callback.answer()
