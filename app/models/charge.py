from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from app.db.base import Base
from datetime import datetime

class Charge(Base):
    __tablename__ = "charges"

    id = Column(String, primary_key=True, index=True)  # Stripe charge ID
    
    amount = Column(Integer)
    amount_captured = Column(Integer)
    amount_refunded = Column(Integer)

    currency = Column(String(10))
    status = Column(String)
    paid = Column(Boolean)
    captured = Column(Boolean)
    disputed = Column(Boolean)
    refunded = Column(Boolean)

    created = Column(DateTime)
    livemode = Column(Boolean, default=False)

    payment_intent = Column(String, ForeignKey("payment_intents.id"), nullable=True)
    payment_method = Column(String)
    payment_intent_rel = relationship("PaymentIntent", backref="charges", foreign_keys=[payment_intent])
    receipt_url = Column(String)
    receipt_email = Column(String)
    receipt_number = Column(String)

    billing_details = Column(JSONB)
    outcome = Column(JSONB)
    payment_method_details = Column(JSONB)
    metadata = Column(JSONB, default=dict)
    fraud_details = Column(JSONB, default=dict)

    description = Column(String)
    statement_descriptor = Column(String)
    statement_descriptor_suffix = Column(String)

    balance_transaction = Column(String)

    invoice_id = Column(String, ForeignKey("invoices.id"), nullable=True)

