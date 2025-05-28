from sqlalchemy import Column, String, Integer, Boolean, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from app.db.base import Base

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
    deleted = Column(Boolean, default=False)  # ✅ NEW: allows deleted customers to exist
    created = Column(DateTime)  # parsed from UNIX timestamp

    invoice_prefix = Column(String)
    next_invoice_sequence = Column(Integer)

    address = Column(JSONB, nullable=True)           # nested object
    shipping = Column(JSONB, nullable=True)
    invoice_settings = Column(JSONB, nullable=True)
    stripe_metadata = Column(JSONB, default=dict)

    tax_exempt = Column(String)  # e.g. "none", "exempt", "reverse"

    default_payment_method_id = Column(String, nullable=True)

    test_clock = Column(String, nullable=True)  # Optional Stripe test_clock reference
