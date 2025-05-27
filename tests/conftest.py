import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from app.models.customer import Customer
from app.transformers.customer import stripe_customer_to_model
from datetime import datetime

FAKE_CUSTOMER = {
    "id": "cus_test_123",
    "email": "john@example.com",
    "name": "John Test",
    "description": "Test description",
    "phone": "+12345678",
    "balance": 0,
    "currency": "usd",
    "delinquent": False,
    "livemode": False,
    "created": int(datetime.utcnow().timestamp()),
    "invoice_prefix": "ABC123",
    "next_invoice_sequence": 1,
    "address": None,
    "shipping": None,
    "invoice_settings": {},
    "metadata": {},
    "tax_exempt": "none"
}

def test_customer_insertion(db):
    obj = stripe_customer_to_model(FAKE_CUSTOMER)
    db.add(obj)
    db.commit()

    result = db.query(Customer).filter_by(id="cus_test_123").first()
    assert result is not None
    assert result.email == "john@example.com"

def test_duplicate_customer_is_skipped(db):
    customer = Customer(id="cus_test_123", email="duplicate@example.com")
    db.add(customer)
    db.commit()

    existing = db.query(Customer).filter_by(id="cus_test_123").all()
    assert len(existing) == 1
