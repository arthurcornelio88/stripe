from sqlalchemy import Column, String, Boolean, DateTime, JSON
from sqlalchemy.dialects.postgresql import JSONB
from app.db.base import Base
from datetime import datetime

class Product(Base):
    __tablename__ = "products"

    id = Column(String, primary_key=True, index=True)  # Stripe product ID, e.g. "prod_xxx"
    name = Column(String, nullable=False)
    description = Column(String)
    active = Column(Boolean, default=True)
    livemode = Column(Boolean, default=False)

    created = Column(DateTime)
    updated = Column(DateTime)

    default_price = Column(String)  # FK to prices.id (nullable if not expanded)
    tax_code = Column(String)
    unit_label = Column(String)
    statement_descriptor = Column(String)
    url = Column(String)

    images = Column(JSONB, default=list)
    marketing_features = Column(JSONB, default=list)
    stripe_metadata = Column(JSONB, default=dict)

    package_dimensions = Column(JSONB, nullable=True)
    shippable = Column(Boolean)
