from __future__ import annotations

import logging
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.api.v1.router import api_router
from app.bootstrap import bootstrap_application
from app.config import get_settings
from app.database import AsyncSessionLocal, engine
from app.middleware.security_headers import SecurityHeadersMiddleware

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(name)s | %(message)s")
    settings = get_settings()
    logger.info("Starting %s [%s]", settings.APP_NAME, settings.ENVIRONMENT)

    async with AsyncSessionLocal() as session:
        await bootstrap_application(session)
        await session.commit()

    yield
    await engine.dispose()
    logger.info("Shutting down API")


async def check_database() -> tuple[bool, str | None]:
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return True, None
    except Exception as exc:
        logger.warning("health_db_failed: %s", exc)
        return False, str(exc)


async def check_bot() -> tuple[bool, str | None]:
    settings = get_settings()
    if not settings.BOT_HEALTH_URL:
        return True, "skipped"
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(settings.BOT_HEALTH_URL)
            if response.status_code != 200:
                return False, f"bot health HTTP {response.status_code}"
            data = response.json()
            if data.get("status") != "ok":
                return False, data.get("telegram", {}).get("error") or "bot unhealthy"
            telegram = data.get("telegram") or {}
            if telegram.get("ok") is False:
                return False, telegram.get("error") or "telegram API unreachable"
            return True, None
    except Exception as exc:
        logger.warning("health_bot_failed: %s", exc)
        return False, str(exc)


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title=settings.APP_NAME,
        version="1.0.0",
        docs_url="/docs" if not settings.is_production else None,
        redoc_url=None,
        openapi_url="/openapi.json" if not settings.is_production else None,
        lifespan=lifespan,
    )

    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(GZipMiddleware, minimum_size=500)

    if settings.is_production:
        app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.trusted_host_list)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "X-Requested-With"],
        max_age=600,
    )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(_: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"message": "داده ورودی نامعتبر است.", "detail": jsonable_encoder(exc.errors())},
        )

    @app.get("/health/live")
    async def health_live():
        """Liveness probe — database only (used by Docker/installer)."""
        db_ok, db_error = await check_database()
        payload = {
            "status": "ok" if db_ok else "unavailable",
            "api": "ok",
            "database": {"ok": db_ok, "error": db_error},
        }
        return JSONResponse(
            status_code=status.HTTP_200_OK if db_ok else status.HTTP_503_SERVICE_UNAVAILABLE,
            content=payload,
        )

    @app.get("/health")
    async def health():
        db_ok, db_error = await check_database()
        bot_ok, bot_error = await check_bot()
        overall = db_ok and bot_ok
        payload = {
            "status": "ok" if overall else "degraded",
            "api": "ok",
            "database": {"ok": db_ok, "error": db_error},
            "bot": {"ok": bot_ok, "error": bot_error},
        }
        return JSONResponse(
            status_code=status.HTTP_200_OK if overall else status.HTTP_503_SERVICE_UNAVAILABLE,
            content=payload,
        )

    app.include_router(api_router, prefix=settings.API_V1_PREFIX)

    return app


app = create_app()
