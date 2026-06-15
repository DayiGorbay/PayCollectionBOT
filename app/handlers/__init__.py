from aiogram import Dispatcher

from .captcha import router as captcha_router
from .free_connect import router as free_connect_router
from .profile import router as profile_router
from .services import router as services_router
from .shop import router as shop_router
from .start import router as start_router


def register_routers(dp: Dispatcher) -> None:
    dp.include_router(start_router)
    dp.include_router(captcha_router)
    dp.include_router(free_connect_router)
    dp.include_router(shop_router)
    dp.include_router(services_router)
    dp.include_router(profile_router)
