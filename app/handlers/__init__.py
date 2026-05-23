from aiogram import Dispatcher

from .captcha import router as captcha_router
from .profile import router as profile_router
from .start import router as start_router


def register_routers(dp: Dispatcher) -> None:
    dp.include_router(start_router)
    dp.include_router(captcha_router)
    dp.include_router(profile_router)
