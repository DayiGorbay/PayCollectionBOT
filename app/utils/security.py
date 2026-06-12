from __future__ import annotations

import secrets
from typing import Optional

from aiogram.filters.callback_data import CallbackData


class MainCallback(CallbackData, prefix="pc"):
    action: str
    item_id: Optional[str] = None


class ServiceCallback(CallbackData, prefix="svc"):
    action: str
    service_id: str


main_cb = MainCallback
service_cb = ServiceCallback


def generate_referral_code(length: int = 8) -> str:
    return secrets.token_urlsafe(length)[:length]
