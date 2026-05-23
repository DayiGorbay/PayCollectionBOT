import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.dispatcher.fsm.storage.memory import MemoryStorage

from app.config import settings
from app.database.session import engine
from app.handlers import register_routers
from app.middlewares.force_join import ForceJoinMiddleware
from app.middlewares.rate_limit import RateLimitMiddleware
from app.models.user import Base

logging.basicConfig(
    level=settings.LOG_LEVEL,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


async def create_database() -> None:
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)


async def main() -> None:
    if not settings.BOT_TOKEN:
        logger.critical("BOT_TOKEN در .env تعریف نشده است")
        return

    bot = Bot(token=settings.BOT_TOKEN, parse_mode="HTML")
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    dp.message.middleware(RateLimitMiddleware())
    dp.callback_query.middleware(RateLimitMiddleware())
    dp.message.middleware(ForceJoinMiddleware())
    dp.callback_query.middleware(ForceJoinMiddleware())

    register_routers(dp)

    await create_database()
    logger.info("ربات با موفقیت راه‌اندازی شد")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
