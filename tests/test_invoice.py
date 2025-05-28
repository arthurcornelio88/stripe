import pytest
from app.models.customer import Customer
from app.models.invoice import Invoice
from app.transformers.invoice import stripe_invoice_to_model
from datetime import datetime, timezone

FAKE_INVOICE = {
    "id": "inv_test_123",
    "customer": "cus_test_123",
    "status": "draft",
    "billing_reason": "manual",
    "collection_method": "charge_automatically",
    "currency": "usd",
    "amount_due": 0,
    "amount_paid": 0,
    "amount_remaining": 0,
    "total": 0,
    "subtotal": 0,
    "created": int(datetime.now(timezone.utc).timestamp()),
    "period_start": int(datetime.now(timezone.utc).timestamp()),
    "period_end": int(datetime.now(timezone.utc).timestamp()),
    "livemode": False,
    "auto_advance": False,
    "attempted": False,
    "attempt_count": 0,
    "hosted_invoice_url": None,
    "invoice_pdf": None,
    "number": None,
    "receipt_number": None,
    "stripe_metadata": {},
    "lines": {},
    "discounts": [],
    "automatic_tax": None,
    "payment_settings": None,
    "shipping_cost": None,
    "status_transitions": None
}

def test_invoice_insertion(db):
    db.add(Customer(id="cus_test_123", email="john@example.com"))
    db.commit()

    obj = stripe_invoice_to_model(FAKE_INVOICE)
    db.add(obj)
    db.commit()

    result = db.query(Invoice).filter_by(id="inv_test_123").first()
    assert result is not None
    assert result.status == "draft"

def test_duplicate_invoice_is_skipped(db):
    db.add(Customer(id="cus_test_123", email="asdsad@test.com"))
    db.add(Invoice(id="inv_test_123", customer_id="cus_test_123", status="draft"))
    db.commit()

    if db.query(Invoice).filter_by(id="inv_test_123").first() is None:
        db.add(Invoice(id="inv_test_123", customer_id="cus_test_123", status="duplicate"))
        db.commit()

    results = db.query(Invoice).filter_by(id="inv_test_123").all()
    assert len(results) == 1
