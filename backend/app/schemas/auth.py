from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class LoginRequest(BaseModel):
    username: str = Field(min_length=2, max_length=64)
    password: str = Field(min_length=1, max_length=128)


class AuthUserOut(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: int
    username: str
    display_name: str = Field(alias="displayName")
    role: str


class LoginResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    access_token: str = Field(alias="accessToken")
    expires_in: int = Field(alias="expiresIn")
    user: AuthUserOut


class MessageResponse(BaseModel):
    message: str
