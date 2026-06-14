from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove

from app.utils.security import main_cb


def _cb(action: str, item_id: str = "0") -> str:
    return main_cb(action=action, item_id=item_id).pack()


def _build_channel_url(channel_link: str) -> str:
    cleaned = channel_link.strip()
    if cleaned.startswith("https://") or cleaned.startswith("http://"):
        return cleaned
    if cleaned.startswith("@"):
        return f"https://t.me/{cleaned.lstrip('@')}"
    return f"https://t.me/{cleaned}"


def back_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="« بازگشت به منو", callback_data=_cb("back_menu"))]]
    )


def main_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="اتصال رایگان", callback_data=_cb("free_connect"))],
            [
                InlineKeyboardButton(text="خرید سرویس", callback_data=_cb("buy_service")),
                InlineKeyboardButton(text="افزایش موجودی", callback_data=_cb("topup_balance")),
            ],
            [
                InlineKeyboardButton(text="حساب کاربری", callback_data=_cb("profile")),
                InlineKeyboardButton(text="سرویس های من", callback_data=_cb("my_services")),
            ],
            [
                InlineKeyboardButton(text="راهنما", callback_data=_cb("help")),
                InlineKeyboardButton(text="زیر مجموعه گیری", callback_data=_cb("referral")),
            ],
        ]
    )


def products_keyboard(products) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []
    for product in products:
        duration = getattr(product, "duration", None) or (
            f"{product.duration_days} روز" if getattr(product, "duration_days", None) else ""
        )
        label = f"{product.name} — {product.price_label}"
        if duration:
            label += f" / {duration}"
        rows.append(
            [
                InlineKeyboardButton(
                    text=label,
                    callback_data=_cb("select_product", str(product.id)),
                )
            ]
        )

    rows.append([InlineKeyboardButton(text="« بازگشت", callback_data=_cb("back_menu"))])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def cancel_payment_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="❌ انصراف", callback_data=_cb("cancel_payment"))]]
    )


def captcha_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="حل کپچا", callback_data=_cb("solve_captcha"))]]
    )


def join_channel_keyboard(channel_link: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="عضویت در کانال", url=_build_channel_url(channel_link))],
            [InlineKeyboardButton(text="بررسی مجدد عضویت", callback_data=_cb("check_join"))],
        ]
    )


def force_join_keyboard(channel_link: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="عضویت در کانال", url=_build_channel_url(channel_link))],
            [InlineKeyboardButton(text="بررسی عضویت ✅", callback_data=_cb("check_join"))],
        ]
    )


def contact_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="ارسال شماره", request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def remove_keyboard() -> ReplyKeyboardRemove:
    return ReplyKeyboardRemove()
