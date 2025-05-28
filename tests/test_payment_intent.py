import pytest
from app.models.customer import Customer
from app.models.payment_method import PaymentMethod
from app.models.payment_intent import PaymentIntent
from app.transformers.payment_intent import stripe_payment_intent_to_model
from datetime import datetime, timezone

FAKE_PAYMENT_INTENT = {
    "id": "pi_test_123",
    "status": "requires_payment_method",
    "currency": "usd",
    "amount": 2000,
    "amount_capturable": 0,
    "amount_received": 0,
    "capture_method": "automatic",
    "confirmation_method": "automatic",
    "client_secret": "secret",
    "created": int(datetime.now(timezone.utc).timestamp()),
    "canceled_at": None,
    "cancellation_reason": None,
    "livemode": False,
    "customer": "cus_test_123",
    "payment_method": "pm_test_123",
    "description": None,
    "receipt_email": None,
    "payment_method_types": ["card"],
    "payment_method_options": None,
    "amount_details": None,
    "stripe_metadata": {},
    "next_action": None,
    "statement_descriptor": None,
    "statement_descriptor_suffix": None
}

def test_payment_intent_insertion(db):
    db.add(Customer(id="cus_test_123", email="x@example.com"))
    db.add(PaymentMethod(id="pm_test_123", type="card", customer_id="cus_test_123"))
    db.commit()

    obj = stripe_payment_intent_to_model(FAKE_PAYMENT_INTENT)
    db.add(obj)
    db.commit()

    result = db.query(PaymentIntent).filter_by(id="pi_test_123").first()
    assert result is not None
    assert result.amount == 2000

def test_duplicate_payment_intent_is_skipped(db):
    db.add(Customer(id="cus_test_123", email="x@example.com"))
    db.add(PaymentIntent(id="pi_test_123", amount=2000, customer_id="cus_test_123"))
    db.commit()

    if db.query(PaymentIntent).filter_by(id="pi_test_123").first() is None:
        db.add(PaymentIntent(id="pi_test_123", amount=2000, customer_id="cus_test_123"))
        db.commit()

    results = db.query(PaymentIntent).filter_by(id="pi_test_123").all()
    assert len(results) == 1
