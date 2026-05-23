from __future__ import annotations

from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram.dispatcher.depends import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database.session import get_session
from app.services.user_service import build_profile_text, get_user_by_telegram_id
from app.utils.security import main_cb

router = Router()


@router.callback_query(main_cb.filter(action="profile"))
async def on_profile(callback: CallbackQuery, session: AsyncSession = Depends(get_session)) -> None:
    user = await get_user_by_telegram_id(session, callback.from_user.id)
    if user is None:
        await callback.message.answer("ابتدا با /start وارد شوید.")
        await callback.answer()
        return

    await callback.message.answer(build_profile_text(user))
    await callback.answer()


@router.callback_query(main_cb.filter(action="referral"))
async def on_referral(callback: CallbackQuery, session: AsyncSession = Depends(get_session)) -> None:
    user = await get_user_by_telegram_id(session, callback.from_user.id)
    if user is None:
        await callback.message.answer("ابتدا با /start وارد شوید.")
        await callback.answer()
        return

    bot_user = await callback.bot.get_me()
    referral_link = f"https://t.me/{bot_user.username}?start={user.referral_code}"
    text = (
        "🔗 لینک بالا رو برای دوستات بفرست و با اینوایت هر نفر 1 زیر مجموعه بگیر!\n\n"
        "❗️نکته مهم:\n"
        "زیر مجموعه ای که شما میارین حتما باید شماره ایران باشه و کپچا اول ربات رو حل کنه و جوین چنل مجموعه پِی بشه، در غیر این صورت کد رفرال شما ثبت نخواهد شد.\n\n"
        f"لینک اختصاصی شما:\n{referral_link}"
    )
    await callback.message.answer(text)
    await callback.answer()
