from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.product import Product


async def list_active_products(session: AsyncSession) -> list[Product]:
    result = await session.execute(
        select(Product).where(Product.is_active.is_(True)).order_by(Product.id)
    )
    return list(result.scalars().all())


async def get_product(session: AsyncSession, product_id: int) -> Product | None:
    result = await session.execute(
        select(Product).where(Product.id == product_id, Product.is_active.is_(True))
    )
    return result.scalar_one_or_none()
