from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from app.db.base import Base
from datetime import datetime

class PaymentMethod(Base):
    __tablename__ = "payment_methods"

    id = Column(String, primary_key=True, index=True)  # Stripe payment method ID
    type = Column(String)  # e.g. "us_bank_account", "card"
    created = Column(DateTime)
    livemode = Column(Boolean, default=False)

    customer_id = Column(String, ForeignKey("customers.id"), nullable=True)
    customer = relationship("Customer", backref="payment_methods")

    billing_details = Column(JSONB)
    stripe_metadata = Column(JSONB, default=dict)

    # Optional: embed detailed method data
    us_bank_account = Column(JSONB, nullable=True)
    card = Column(JSONB, nullable=True)
