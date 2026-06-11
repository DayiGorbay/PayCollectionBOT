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
                    callback_data=service_cb.new(action="view", service_id=str(svc.id)),
                )
            ]
        )
    rows.append([InlineKeyboardButton(text="« بازگشت", callback_data=main_cb.new(action="back_menu"))])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def service_detail_keyboard(service_id: int) -> InlineKeyboardMarkup:
    sid = str(service_id)
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🔗 لینک سابسکریپشن",
                    callback_data=service_cb.new(action="sub_link", service_id=sid),
                ),
                InlineKeyboardButton(
                    text="⚙️ کانفیگ",
                    callback_data=service_cb.new(action="config_link", service_id=sid),
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🔄 تمدید",
                    callback_data=service_cb.new(action="renew", service_id=sid),
                ),
                InlineKeyboardButton(
                    text="🗑 حذف",
                    callback_data=service_cb.new(action="delete", service_id=sid),
                ),
            ],
            [
                InlineKeyboardButton(
                    text="« لیست سرویس‌ها",
                    callback_data=service_cb.new(action="back_list", service_id="0"),
                )
            ],
        ]
    )
