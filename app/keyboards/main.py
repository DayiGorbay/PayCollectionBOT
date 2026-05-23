from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove

from app.utils.security import main_cb


def _build_channel_url(channel_link: str) -> str:
    cleaned = channel_link.strip()
    if cleaned.startswith("https://") or cleaned.startswith("http://"):
        return cleaned
    if cleaned.startswith("@"):
        return f"https://t.me/{cleaned.lstrip('@')}"
    return f"https://t.me/{cleaned}"


def main_menu_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(InlineKeyboardButton(text="اتصال رایگان", callback_data=main_cb.new(action="free_connect")))
    keyboard.add(
        InlineKeyboardButton(text="حساب کاربری", callback_data=main_cb.new(action="profile")),
        InlineKeyboardButton(text="سرویس های من", callback_data=main_cb.new(action="my_services")),
    )
    keyboard.add(
        InlineKeyboardButton(text="راهنما", callback_data=main_cb.new(action="help")),
        InlineKeyboardButton(text="زیر مجموعه گیری", callback_data=main_cb.new(action="referral")),
    )
    return keyboard


def captcha_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(text="حل کپچا", callback_data=main_cb.new(action="solve_captcha")))
    return keyboard


def join_channel_keyboard(channel_link: str) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton(text="عضویت در کانال", url=_build_channel_url(channel_link))
    )
    keyboard.add(InlineKeyboardButton(text="بررسی مجدد عضویت", callback_data=main_cb.new(action="check_join")))
    return keyboard


def force_join_keyboard(channel_link: str) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton(text="عضویت در کانال", url=_build_channel_url(channel_link))
    )
    keyboard.add(InlineKeyboardButton(text="بررسی عضویت ✅", callback_data=main_cb.new(action="check_join")))
    return keyboard


def contact_keyboard() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    keyboard.add(KeyboardButton(text="ارسال شماره", request_contact=True))
    return keyboard


def remove_keyboard() -> ReplyKeyboardRemove:
    return ReplyKeyboardRemove()
