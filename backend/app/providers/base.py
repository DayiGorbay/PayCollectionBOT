from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Awaitable, Callable

from app.providers.models import (
    PanelInbound,
    PanelNode,
    PanelSystemStats,
    PanelTestResult,
    PanelUser,
    PanelUserCreate,
    PanelUserList,
    PanelUserUpdate,
)

AuthCacheCallback = Callable[[dict], Awaitable[None]]


class PanelProvider(ABC):
    """اینترفیس یکپارچه برای Marzban و 3X-UI."""

    @abstractmethod
    async def test_connection(self) -> PanelTestResult: ...

    @abstractmethod
    async def create_user(self, data: PanelUserCreate) -> PanelUser: ...

    @abstractmethod
    async def update_user(self, username: str, data: PanelUserUpdate) -> PanelUser: ...

    @abstractmethod
    async def delete_user(self, username: str) -> None: ...

    @abstractmethod
    async def get_user(self, username: str) -> PanelUser: ...

    @abstractmethod
    async def get_users(self, *, offset: int = 0, limit: int = 50) -> PanelUserList: ...

    @abstractmethod
    async def reset_traffic(self, username: str) -> PanelUser: ...

    @abstractmethod
    async def get_inbounds(self) -> list[PanelInbound]: ...

    @abstractmethod
    async def get_nodes(self) -> list[PanelNode]: ...

    @abstractmethod
    async def get_system_stats(self) -> PanelSystemStats: ...

    @abstractmethod
    async def user_exists(self, username: str) -> bool: ...
