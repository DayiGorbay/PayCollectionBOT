from __future__ import annotations

import re
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.discount import DiscountCode
from app.utils.files import format_rial


def _calculate_discount(row: DiscountCode, amount_rial: int) -> int:
    if row.type_label == "درصدی":
        percent = row.discount_percent
        if percent is None:
            digits = re.sub(r"\D", "", row.amount)
            percent = int(digits) if digits else 0
        return min(amount_rial, amount_rial * percent // 100)
    fixed = row.discount_amount_rial
    if fixed is None:
        digits = re.sub(r"\D", "", row.amount)
        fixed = int(digits) if digits else 0
    return min(amount_rial, fixed)


async def validate_discount_code(session: AsyncSession, code: str, amount_rial: int) -> tuple[DiscountCode, int]:
    normalized = code.strip().upper()
    result = await session.execute(select(DiscountCode).where(DiscountCode.code == normalized))
    row = result.scalar_one_or_none()
    if row is None:
        raise ValueError("کد تخفیف یافت نشد.")
    if row.status != "فعال":
        raise ValueError("کد تخفیف غیرفعال است.")
    if row.max_uses and row.used_count >= row.max_uses:
        raise ValueError("سقف استفاده از این کد تکمیل شده است.")
    discount_rial = _calculate_discount(row, amount_rial)
    if discount_rial <= 0:
        raise ValueError("کد تخفیف برای این مبلغ قابل اعمال نیست.")
    return row, discount_rial


async def mark_discount_used(session: AsyncSession, row: DiscountCode) -> None:
    row.used_count = (row.used_count or 0) + 1
    max_uses = row.max_uses or None
    row.used_label = f"{row.used_count}/{max_uses}" if max_uses else f"{row.used_count}/∞"
    await session.commit()
