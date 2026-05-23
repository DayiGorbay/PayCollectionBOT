from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import CallbackQuery, Message
from aiogram.dispatcher.depends import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database.session import get_session
from app.keyboards.main import captcha_keyboard, force_join_keyboard, main_menu_keyboard
from app.services.user_service import get_or_create_user, mark_channel_joined, register_referral
from app.utils.security import main_cb
from app.utils.telegram import get_channel_chat_id, is_channel_member

router = Router()

START_TEXT = (
    "✨ به مجموعه پِی خوش آمدید!\n\n"
    "🍊دیگه پولی برای برای کانفیگ نده!\n"
    "🎁با دعوت چند تا از دوستات کانفیگ رایگان هدیه بگیر\n"
    "✅ تضمین امنیت ارتباطات شما\n"
    "📞 پشتیبانی حرفه‌ای 24/7\n\n"
    "از منوی زیر بخش مورد نظر خود را انتخاب کنید."
)

HELP_TEXT = (
    "❄️ تمامی چیز هایی که باید در مورد ربات مجموعه پِی بدونید:\n\n"
    "🥊 با دعوت کردن 5 نفر از دوستان یا خانوادتون با کد رفرالتون میتونید کانفیگ رایگان از ما دریافت کنید!\n\n"
    "⚠️ برای اینکه تقلبی تو کار نباشه کسانی که با کد رفرالتون دعوت میشن باید شماره ایران داشته باشند، هنگام استارت ربات باید کپچا رو انجام بدن و وارد چنل ما بشن در غیر این صورت زیر مجموعه شما حساب نمیشن!\n\n"
    "🔥 بعد از اینکه زیر مجموعه کافی گرفتی، میتونی با زدن روی دکمه (( اتصال رایگان )) کانفیگ رایگانت رو دریافت کنی!\n\n"
    "😱 یچیز دیگه برای مواقعی که حواست نیست و یهو حجمت تموم نشه، پیشنهاد میکنم حتما دو کانفیگ رایگان داشته باشی!"
)


@router.message(CommandStart())
async def on_start(
    message: Message,
    session: AsyncSession = Depends(get_session),
) -> None:
    payload = ""
    if message.text:
        parts = message.text.split(maxsplit=1)
        if len(parts) > 1:
            payload = parts[1].strip()

    user = await get_or_create_user(session, message.from_user)
    if payload:
        await register_referral(session, user, payload)

    channel_chat_id = get_channel_chat_id(
        settings.CHANNEL_ID,
        settings.CHANNEL_LINK,
        settings.CHANNEL_USERNAME,
    )
    channel_member = await is_channel_member(message.bot, channel_chat_id, user.telegram_id)
    if not channel_member:
        await message.answer(
            "🚫 برای استفاده از ربات ابتدا باید عضو کانال ما شوید.\n\n"
            "برای ادامه ابتدا روی دکمه عضویت در کانال کلیک کنید و سپس بررسی عضویت را بزنید.",
            reply_markup=force_join_keyboard(settings.CHANNEL_LINK),
        )
        return

    if not user.joined_channel:
        await mark_channel_joined(session, user)

    await message.answer(START_TEXT, reply_markup=main_menu_keyboard())

    if not user.verified:
        await message.answer(
            "برای تایید حساب خود روی دکمه زیر کلیک کنید 👇",
            reply_markup=captcha_keyboard(),
        )


@router.message(Command(commands=["help"]))
async def on_help(message: Message) -> None:
    await message.answer(HELP_TEXT)


@router.callback_query(main_cb.filter(action="help"))
async def on_help_callback(callback: CallbackQuery) -> None:
    await callback.message.answer(HELP_TEXT)
    await callback.answer()


@router.callback_query(main_cb.filter(action="free_connect"))
async def on_free_connect(callback: CallbackQuery) -> None:
    await callback.answer("این بخش فعلاً در حال آماده‌سازی است.", show_alert=True)


@router.callback_query(main_cb.filter(action="my_services"))
async def on_my_services(callback: CallbackQuery) -> None:
    await callback.message.answer("سرویس های شما در آینده فعال خواهد شد.")
    await callback.answer()
