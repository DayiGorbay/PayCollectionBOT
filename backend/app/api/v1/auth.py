from __future__ import annotations

from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_admin
from app.database import get_db
from app.models.admin_user import AdminUser
from app.schemas.auth import AuthUserOut, LoginRequest, LoginResponse, MessageResponse
from app.services.auth_service import authenticate_admin

router = APIRouter(prefix="/auth", tags=["auth"])


def _client_ip(request: Request) -> str:
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    if request.client:
        return request.client.host
    return "unknown"


@router.post("/login", response_model=LoginResponse, response_model_by_alias=True)
async def login(
    payload: LoginRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> LoginResponse | JSONResponse:
    try:
        return await authenticate_admin(
            db,
            username=payload.username.strip(),
            password=payload.password,
            client_ip=_client_ip(request),
        )
    except ValueError as exc:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"message": str(exc), "code": "invalid_credentials"},
        )


@router.post("/logout", response_model=MessageResponse)
async def logout(_: AdminUser = Depends(get_current_admin)) -> MessageResponse:
    return MessageResponse(message="خروج با موفقیت انجام شد.")


@router.get("/me", response_model=AuthUserOut, response_model_by_alias=True)
async def me(admin: AdminUser = Depends(get_current_admin)) -> AuthUserOut:
    return AuthUserOut(
        id=admin.id,
        username=admin.username,
        display_name=admin.display_name,
        role=admin.role,
    )
