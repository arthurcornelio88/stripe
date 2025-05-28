import pytest
from app.models.customer import Customer
from app.models.payment_method import PaymentMethod
from app.transformers.payment_method import stripe_payment_method_to_model
from datetime import datetime, timezone

FAKE_PAYMENT_METHOD = {
    "id": "pm_test_123",
    "type": "card",
    "created": int(datetime.now(timezone.utc).timestamp()),
    "livemode": False,
    "customer": "cus_test_123",
    "billing_details": {"name": "John Doe"},
    "stripe_metadata": {},
    "us_bank_account": None,
    "card": {"brand": "visa", "last4": "4242"}
}

def test_payment_method_insertion(db):
    db.add(Customer(id="cus_test_123", email="john@example.com"))
    db.commit()

    obj = stripe_payment_method_to_model(FAKE_PAYMENT_METHOD)
    db.add(obj)
    db.commit()

    result = db.query(PaymentMethod).filter_by(id="pm_test_123").first()
    assert result is not None
    assert result.type == "card"

def test_duplicate_payment_method_is_skipped(db):
    db.add(Customer(id="cus_test_123", email="base@example.com"))
    db.add(PaymentMethod(id="pm_test_123", type="card", customer_id="cus_test_123"))
    db.commit()

    if db.query(PaymentMethod).filter_by(id="pm_test_123").first() is None:
        db.add(PaymentMethod(id="pm_test_123", type="card", customer_id="cus_test_123"))
        db.commit()

    results = db.query(PaymentMethod).filter_by(id="pm_test_123").all()
    assert len(results) == 1
