from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from app.db.base import Base
from datetime import datetime

class PaymentIntent(Base):
    __tablename__ = "payment_intents"

    id = Column(String, primary_key=True, index=True)  # Stripe payment_intent ID
    status = Column(String)
    currency = Column(String(10))

    amount = Column(Integer)
    amount_capturable = Column(Integer)
    amount_received = Column(Integer)
    capture_method = Column(String)
    confirmation_method = Column(String)
    client_secret = Column(String)  # Optional; might not be stored for security

    created = Column(DateTime)
    canceled_at = Column(DateTime, nullable=True)
    cancellation_reason = Column(String, nullable=True)

    livemode = Column(Boolean, default=False)

    customer_id = Column(String, ForeignKey("customers.id"), nullable=True)
    customer = relationship("Customer", backref="payment_intents")

    payment_method = Column(String, ForeignKey("payment_methods.id"), nullable=True)
    payment_method_entity = relationship("PaymentMethod", backref="payment_intents", foreign_keys=[payment_method])

    description = Column(String, nullable=True)
    receipt_email = Column(String, nullable=True)

    payment_method_types = Column(JSONB, default=list)
    payment_method_options = Column(JSONB, nullable=True)
    amount_details = Column(JSONB, nullable=True)
    stripe_metadata = Column(JSONB, default=dict)
    next_action = Column(JSONB, nullable=True)
    statement_descriptor = Column(String, nullable=True)
    statement_descriptor_suffix = Column(String, nullable=True)

    card_brand = Column(String, nullable=True)
    card_funding = Column(String, nullable=True)
    setup_future_usage = Column(String, nullable=True)

