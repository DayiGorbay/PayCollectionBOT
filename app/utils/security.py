from __future__ import annotations

import secrets

from aiogram.utils.callback_data import CallbackData

main_cb = CallbackData("pc", "action", "item_id")
service_cb = CallbackData("svc", "action", "service_id")


def generate_referral_code(length: int = 8) -> str:
    return secrets.token_urlsafe(length)[:length]
