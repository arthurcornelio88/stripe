from sqlalchemy import Column, String, Boolean, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from app.db.base import Base
from datetime import datetime

class Price(Base):
    __tablename__ = "prices"

    id = Column(String, primary_key=True, index=True)  # e.g. "price_1MoBy5..."
    active = Column(Boolean, default=True)
    currency = Column(String(10))
    billing_scheme = Column(String)
    type = Column(String)
    unit_amount = Column(Integer)  # Stripe uses cents for USD, etc.
    unit_amount_decimal = Column(String)

    product_id = Column(String, ForeignKey("products.id"))
    product = relationship("Product", backref="prices")

    recurring = Column(JSONB, nullable=True)  # contains interval, usage_type, etc.

    livemode = Column(Boolean, default=False)
    created = Column(DateTime)

    nickname = Column(String)
    lookup_key = Column(String)
    metadata = Column(JSONB, default=dict)

    tax_behavior = Column(String)
    tiers_mode = Column(String)
    custom_unit_amount = Column(JSONB, nullable=True)
    transform_quantity = Column(JSONB, nullable=True)
