from __future__ import annotations

from aiogram import F, Router
from aiogram.dispatcher.depends import Depends
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.filters import Text
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database.session import get_session
from app.keyboards.main import contact_keyboard, join_channel_keyboard, remove_keyboard
from app.models.user import User
from app.services.user_service import (
    finalize_referral,
    get_user_by_id,
    get_user_by_telegram_id,
    mark_phone_verified,
)
from app.states.registration import RegistrationState
from app.utils.security import main_cb
from app.utils.telegram import get_channel_chat_id, is_channel_member

router = Router()


@router.callback_query(main_cb.filter(action="solve_captcha"))
async def on_solve_captcha(
    callback: CallbackQuery,
    session: AsyncSession = Depends(get_session),
    state: FSMContext = Depends(FSMContext),
) -> None:
    user = await get_user_by_telegram_id(session, callback.from_user.id)
    if user is None:
        await callback.message.answer("ابتدا با /start وارد شوید.")
        await callback.answer()
        return

    await callback.message.answer(
        "برای تایید حساب خود روی دکمه زیر کلیک کنید 👇",
        reply_markup=contact_keyboard(),
    )
    await state.set_state(RegistrationState.waiting_contact)
    await callback.answer()


@router.message(RegistrationState.waiting_contact, F.contact)
async def on_contact_received(
    message: Message,
    session: AsyncSession = Depends(get_session),
    state: FSMContext = Depends(FSMContext),
) -> None:
    if message.contact.user_id != message.from_user.id:
        await message.answer("لطفا شماره همان حسابی که وارد شده است را ارسال کنید.")
        return

    user = await get_user_by_telegram_id(session, message.from_user.id)
    if user is None:
        await message.answer("ابتدا با /start وارد شوید.")
        await state.clear()
        return

    await mark_phone_verified(session, user, message.contact.phone_number)

    if not user.is_iranian:
        await message.answer(
            "✅ حساب کاربری شما با موفقیت تایید شد.\n"
            "(به دلیل ایرانی نبودن شماره اکانت شما، زیر مجموعه ای برای دعوت کننده شما ثبت نشد) ❗️",
            reply_markup=remove_keyboard(),
        )
        await state.clear()
        return

    if user.is_suspicious:
        await message.answer(
            "شماره تلفن شما قبلا در سیستم ثبت شده است. حساب شما در وضعیت بررسی قرار گرفت.",
            reply_markup=remove_keyboard(),
        )
        await state.clear()
        return

    if user.invited_by is None:
        await message.answer(
            "حساب کاربری شما با موفقیت تایید شد ✅",
            reply_markup=remove_keyboard(),
        )
        await state.clear()
        return

    inviter = await get_user_by_id(session, user.invited_by)
    if inviter is None:
        await message.answer(
            "حساب کاربری شما با موفقیت تایید شد ✅",
            reply_markup=remove_keyboard(),
        )
        await state.clear()
        return

    channel_chat_id = get_channel_chat_id(
        settings.CHANNEL_ID,
        settings.CHANNEL_LINK,
        settings.CHANNEL_USERNAME,
    )
    channel_member = await is_channel_member(callback.bot, channel_chat_id, user.telegram_id)
    if not channel_member:
        await message.answer(
            "برای تکمیل ثبت نام ابتدا باید عضو کانال شوید.",
            reply_markup=join_channel_keyboard(settings.CHANNEL_LINK),
        )
        await state.set_state(RegistrationState.waiting_channel_join)
        return

    await finalize_referral(session, user, inviter)
    await message.answer(
        "حساب کاربری شما با موفقیت تایید شد ✅\n"
        "زیر مجموعه شما با موفقیت نهایی شد.",
        reply_markup=remove_keyboard(),
    )
    await state.clear()


@router.message(RegistrationState.waiting_contact)
async def on_contact_invalid(message: Message) -> None:
    await message.answer("لطفا شماره خود را با استفاده از دکمه ارسال شماره ارسال کنید.")


@router.callback_query(main_cb.filter(action="check_join"))
async def on_check_join(
    callback: CallbackQuery,
    session: AsyncSession = Depends(get_session),
    state: FSMContext = Depends(FSMContext),
) -> None:
    user = await get_user_by_telegram_id(session, callback.from_user.id)
    if user is None or not user.verified:
        await callback.message.answer("ابتدا باید حساب خود را با حل کپچا و ارسال شماره احراز کنید.")
        await callback.answer()
        return

    channel_chat_id = get_channel_chat_id(
        settings.CHANNEL_ID,
        settings.CHANNEL_LINK,
        settings.CHANNEL_USERNAME,
    )
    channel_member = await is_channel_member(callback.bot, channel_chat_id, user.telegram_id)
    if not channel_member:
        await callback.message.answer(
            "شما هنوز عضو کانال نیستید. لطفاً ابتدا عضو شوید و سپس دوباره بررسی کنید.",
            reply_markup=join_channel_keyboard(settings.CHANNEL_LINK),
        )
        await callback.answer()
        return

    user.joined_channel = True
    await session.commit()
    await session.refresh(user)

    if user.invited_by and user.is_iranian and not user.referral_finalized:
        inviter = await get_user_by_id(session, user.invited_by)
        if inviter:
            await finalize_referral(session, user, inviter)
            await callback.message.answer(
                "عضویت شما در کانال تایید شد و رفرال نهایی شد. ✅",
            )
            await state.clear()
            await callback.answer()
            return

    await callback.message.answer("عضویت شما در کانال تأیید شد. ✅")
    await state.clear()
    await callback.answer()
