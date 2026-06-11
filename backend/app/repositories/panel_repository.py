from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.catalog import Panel


class PanelRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, panel_id: int) -> Panel | None:
        return await self.session.get(Panel, panel_id)

    async def get_by_code(self, code: str) -> Panel | None:
        result = await self.session.execute(select(Panel).where(Panel.code_panel == code))
        return result.scalar_one_or_none()

    async def list_all(self) -> list[Panel]:
        result = await self.session.execute(select(Panel).order_by(Panel.id.desc()))
        return list(result.scalars().all())
