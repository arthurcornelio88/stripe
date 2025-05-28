import pytest
from app.models.customer import Customer
from app.models.invoice import Invoice
from app.models.payment_intent import PaymentIntent
from app.models.charge import Charge
from app.transformers.charge import stripe_charge_to_model
from datetime import datetime, timezone

FAKE_CHARGE = {
    "id": "ch_test_123",
    "amount": 1099,
    "amount_captured": 1099,
    "amount_refunded": 0,
    "currency": "usd",
    "status": "succeeded",
    "paid": True,
    "captured": True,
    "disputed": False,
    "refunded": False,
    "created": int(datetime.now(timezone.utc).timestamp()),
    "livemode": False,
    "payment_intent": "pi_test_123",
    "payment_method": "pm_test_123",
    "receipt_url": None,
    "receipt_email": None,
    "receipt_number": None,
    "billing_details": {"name": "John Doe"},
    "outcome": {"risk_level": "normal"},
    "payment_method_details": {"type": "card"},
    "stripe_metadata": {},
    "fraud_details": {},
    "description": None,
    "statement_descriptor": None,
    "statement_descriptor_suffix": None,
    "balance_transaction": None,
    "invoice": "inv_test_123"
}

def test_charge_insertion(db):
    db.add(Customer(id="cus_test_123", email="john@example.com"))
    db.add(Invoice(id="inv_test_123", customer_id="cus_test_123", status="draft"))
    db.add(PaymentIntent(id="pi_test_123", amount=2000, customer_id="cus_test_123"))
    db.commit()

    obj = stripe_charge_to_model(FAKE_CHARGE)
    db.add(obj)
    db.commit()

    result = db.query(Charge).filter_by(id="ch_test_123").first()
    assert result is not None
    assert result.amount == 1099

def test_duplicate_charge_is_skipped(db):
    db.add(Charge(id="ch_test_123", amount=1099))
    db.commit()

    if db.query(Charge).filter_by(id="ch_test_123").first() is None:
        db.add(Charge(id="ch_test_123", amount=1099))
        db.commit()

    results = db.query(Charge).filter_by(id="ch_test_123").all()
    assert len(results) == 1
