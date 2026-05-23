from __future__ import annotations

import secrets

from aiogram.utils.callback_data import CallbackData

main_cb = CallbackData("pc", "action")


def generate_referral_code(length: int = 8) -> str:
    return secrets.token_urlsafe(length)[:length]
