from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_admin_role
from app.database import get_db
from app.models.admin_user import AdminUser
from app.models.catalog import Panel, Product
from app.schemas.products import ProductCreate, ProductOut, ProductUpdate

router = APIRouter(prefix="/products", tags=["products"])


def _format_price_label(rial: int) -> str:
    return f"{rial:,}".replace(",", "،") + " ت"


def _format_duration_label(days: int) -> str:
    return f"{days} روز"


def _product_out(row: Product) -> ProductOut:
    return ProductOut(
        id=row.id,
        name=row.name,
        price=row.price_label,
        duration_days=row.duration_days,
        duration=row.duration,
        panel=row.panel,
        panel_id=row.panel_id,
        code=row.code,
        category=row.category,
        is_active=row.is_active,
    )


@router.get("", response_model=list[ProductOut], response_model_by_alias=True)
async def list_products(
    _: AdminUser = Depends(require_admin_role),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Product).order_by(Product.id.desc()))
    return [_product_out(row) for row in result.scalars().all()]


@router.post("", response_model=ProductOut, response_model_by_alias=True, status_code=status.HTTP_201_CREATED)
async def create_product(
    payload: ProductCreate,
    _: AdminUser = Depends(require_admin_role),
    db: AsyncSession = Depends(get_db),
):
    existing = await db.execute(select(Product).where(Product.code == payload.code))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="کد محصول تکراری است.")

    panel = await db.get(Panel, payload.panel_id)
    if panel is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="پنل انتخاب‌شده یافت نشد.")

    product = Product(
        name=payload.name,
        price_label=_format_price_label(payload.price),
        price_rial=payload.price,
        duration_days=payload.duration_days,
        duration=_format_duration_label(payload.duration_days),
        panel_id=panel.id,
        panel=panel.name,
        code=payload.code,
        category=payload.category,
        is_active=True,
    )
    db.add(product)
    await db.flush()
    await db.refresh(product)
    return _product_out(product)


@router.patch("/{product_id}", response_model=ProductOut, response_model_by_alias=True)
async def update_product(
    product_id: int,
    payload: ProductUpdate,
    _: AdminUser = Depends(require_admin_role),
    db: AsyncSession = Depends(get_db),
):
    product = await db.get(Product, product_id)
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="محصول یافت نشد.")

    data = payload.model_dump(exclude_unset=True, by_alias=True)
    if "price" in data:
        product.price_rial = data["price"]
        product.price_label = _format_price_label(data["price"])
    if "duration_days" in data:
        product.duration_days = data["duration_days"]
        product.duration = _format_duration_label(data["duration_days"])
    if "panel_id" in data:
        panel = await db.get(Panel, data["panel_id"])
        if panel is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="پنل انتخاب‌شده یافت نشد.")
        product.panel_id = panel.id
        product.panel = panel.name
    if "name" in data:
        product.name = data["name"]
    if "category" in data:
        product.category = data["category"]
    if "is_active" in data:
        product.is_active = data["is_active"]

    await db.flush()
    await db.refresh(product)
    return _product_out(product)


@router.delete("/{product_id}")
async def delete_product(
    product_id: int,
    _: AdminUser = Depends(require_admin_role),
    db: AsyncSession = Depends(get_db),
):
    product = await db.get(Product, product_id)
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="محصول یافت نشد.")
    await db.delete(product)
    return {"message": "محصول حذف شد."}
