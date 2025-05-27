from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from app.db.base import Base
from datetime import datetime

class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(String, primary_key=True, index=True)  # Stripe invoice ID
    customer_id = Column(String, ForeignKey("customers.id"))
    customer = relationship("Customer", backref="invoices")

    charges = relationship("Charge", backref="invoice", foreign_keys="Charge.invoice_id")
    

    status = Column(String)
    billing_reason = Column(String)
    collection_method = Column(String)

    currency = Column(String(10))
    amount_due = Column(Integer)
    amount_paid = Column(Integer)
    amount_remaining = Column(Integer)
    total = Column(Integer)
    subtotal = Column(Integer)

    created = Column(DateTime)
    period_start = Column(DateTime)
    period_end = Column(DateTime)

    livemode = Column(Boolean, default=False)
    auto_advance = Column(Boolean, default=False)
    attempted = Column(Boolean, default=False)
    attempt_count = Column(Integer, default=0)

    hosted_invoice_url = Column(String)
    invoice_pdf = Column(String)
    number = Column(String)
    receipt_number = Column(String)

    metadata = Column(JSONB, default=dict)
    lines = Column(JSONB, default=list)
    discounts = Column(JSONB, default=list)
    automatic_tax = Column(JSONB, nullable=True)
    payment_settings = Column(JSONB, nullable=True)
    shipping_cost = Column(JSONB, nullable=True)
    status_transitions = Column(JSONB, nullable=True)
