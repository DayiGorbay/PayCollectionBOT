from __future__ import annotations

from sqlalchemy import Column, Integer, String

from app.models.user import Base


class DiscountCode(Base):
    __tablename__ = "discount_codes"

    id = Column(Integer, primary_key=True)
    code = Column(String(64), unique=True, nullable=False)
    amount = Column(String(64), nullable=False)
    type_label = Column(String(32), nullable=False)
    used_label = Column(String(32), nullable=False)
    valid_until = Column(String(32), nullable=False)
    status = Column(String(32), nullable=False)
    discount_percent = Column(Integer, nullable=True)
    discount_amount_rial = Column(Integer, nullable=True)
    max_uses = Column(Integer, nullable=False, default=0)
    used_count = Column(Integer, nullable=False, default=0)
