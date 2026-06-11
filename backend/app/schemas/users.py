from __future__ import annotations

from pydantic import BaseModel


class PanelUserOut(BaseModel):
    id: int
    name: str
    plan: str
    volume: str
    expiry: str
    status: str
