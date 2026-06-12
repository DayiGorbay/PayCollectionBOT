from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.models.user_service import UserService
from app.utils.security import main_cb, service_cb


def services_list_keyboard(services: list[UserService]) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []
    for svc in services:
        label = f"{svc.panel_username} — {svc.data_gb}GB"
        rows.append(
            [
                InlineKeyboardButton(
                    text=label,
                    callback_data=service_cb(action="view", service_id=str(svc.id)).pack(),
                )
            ]
        )

    rows.append(
        [
            InlineKeyboardButton(
                text="« بازگشت",
                callback_data=main_cb(action="back_menu").pack(),
            )
        ]
    )

    return InlineKeyboardMarkup(inline_keyboard=rows)


def service_detail_keyboard(service_id: int) -> InlineKeyboardMarkup:
    sid = str(service_id)
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🔗 لینک سابسکریپشن",
                    callback_data=service_cb(action="sub_link", service_id=sid).pack(),
                ),
                InlineKeyboardButton(
                    text="⚙️ کانفیگ",
                    callback_data=service_cb(action="config_link", service_id=sid).pack(),
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🔄 تمدید",
                    callback_data=service_cb(action="renew", service_id=sid).pack(),
                ),
                InlineKeyboardButton(
                    text="🗑 حذف",
                    callback_data=service_cb(action="delete", service_id=sid).pack(),
                ),
            ],
            [
                InlineKeyboardButton(
                    text="« لیست سرویس‌ها",
                    callback_data=service_cb(action="back_list", service_id="0").pack(),
                )
            ],
        ]
    )
