from sqlalchemy import Column, String, DateTime, Boolean, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from app.db.base import Base
from datetime import datetime

class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(String, primary_key=True, index=True)  # Stripe subscription ID
    status = Column(String)
    currency = Column(String(10))

    customer_id = Column(String, ForeignKey("customers.id"))
    customer = relationship("Customer", backref="subscriptions")

    price_id = Column(String, ForeignKey("prices.id"))
    price = relationship("Price", backref="subscriptions")

    start_date = Column(DateTime)
    created = Column(DateTime)
    cancel_at = Column(DateTime, nullable=True)
    canceled_at = Column(DateTime, nullable=True)
    ended_at = Column(DateTime, nullable=True)

    cancel_at_period_end = Column(Boolean, default=False)
    livemode = Column(Boolean, default=False)

    stripe_metadata = Column(JSONB, default=dict)
    items = Column(JSONB, default=list)
    invoice_settings = Column(JSONB, nullable=True)
    automatic_tax = Column(JSONB, nullable=True)
    payment_settings = Column(JSONB, nullable=True)
    trial_settings = Column(JSONB, nullable=True)

    latest_invoice = Column(String, nullable=True)
