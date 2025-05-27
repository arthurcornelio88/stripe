from sqlalchemy import Column, String, Integer, Boolean, DateTime, JSON
from sqlalchemy.dialects.postgresql import JSONB
from app.db.base import Base
from datetime import datetime

class Customer(Base):
    __tablename__ = "customers"

    id = Column(String, primary_key=True, index=True)  # e.g. "cus_XXXX"
    email = Column(String)
    name = Column(String)
    description = Column(String)
    phone = Column(String)

    balance = Column(Integer)
    currency = Column(String(10))
    delinquent = Column(Boolean)
    livemode = Column(Boolean)
    created = Column(DateTime)  # You'll parse UNIX timestamp to datetime

    invoice_prefix = Column(String)
    next_invoice_sequence = Column(Integer)

    address = Column(JSONB, nullable=True)  # nested JSON
    shipping = Column(JSONB, nullable=True)
    invoice_settings = Column(JSONB, nullable=True)
    stripe_metadata = Column(JSONB, default=dict)

    tax_exempt = Column(String)  # e.g. "none", "exempt", "reverse"

    # Optional: test_clock = Column(String)  # ID if used
