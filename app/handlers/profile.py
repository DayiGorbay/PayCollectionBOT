from __future__ import annotations

from aiogram import F, Router
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.user_service import build_profile_text, can_earn_referral_rewards, get_user_by_telegram_id
from app.keyboards.main import back_menu_keyboard
from app.utils.callback_ui import edit_callback_message
from app.utils.security import main_cb

router = Router()


@router.callback_query(main_cb.filter(F.action == "profile"))
async def on_profile(callback: CallbackQuery, session: AsyncSession) -> None:
    user = await get_user_by_telegram_id(session, callback.from_user.id)
    if user is None:
        await edit_callback_message(callback, "ابتدا با /start وارد شوید.")
        await callback.answer()
        return

    if not can_earn_referral_rewards(user):
        await callback.answer("ابتدا حساب خود را احراز کنید.", show_alert=True)
        return

    await edit_callback_message(
        callback,
        build_profile_text(user),
        reply_markup=back_menu_keyboard(),
    )
    await callback.answer()


@router.callback_query(main_cb.filter(F.action == "referral"))
async def on_referral(callback: CallbackQuery, session: AsyncSession) -> None:
    user = await get_user_by_telegram_id(session, callback.from_user.id)
    if user is None:
        await edit_callback_message(callback, "ابتدا با /start وارد شوید.")
        await callback.answer()
        return

    if not can_earn_referral_rewards(user):
        await callback.answer("ابتدا حساب خود را احراز کنید.", show_alert=True)
        return

    bot_user = await callback.bot.get_me()
    referral_link = f"https://t.me/{bot_user.username}?start={user.referral_code}"
    text = (
        "🔗 لینک بالا رو برای دوستات بفرست و با اینوایت هر نفر 1 زیر مجموعه بگیر!\n\n"
        "❗️نکته مهم:\n"
        "زیر مجموعه ای که شما میارین حتما باید شماره ایران باشه و کپچا اول ربات رو حل کنه و جوین چنل مجموعه پِی بشه، در غیر این صورت کد رفرال شما ثبت نخواهد شد.\n\n"
        f"لینک اختصاصی شما:\n{referral_link}"
    )
    await edit_callback_message(callback, text, reply_markup=back_menu_keyboard())
    await callback.answer()
