import pytest
from app.models.customer import Customer
from app.transformers.customer import stripe_customer_to_model
from datetime import datetime, timezone

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
    "created": int(datetime.now(timezone.utc).timestamp()),
    "invoice_prefix": "ABC123",
    "next_invoice_sequence": 1,
    "address": None,
    "shipping": None,
    "invoice_settings": {},
    "stripe_metadata": {},
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
    # Insertion 1
    obj1 = Customer(id="cus_test_123", email="first@example.com")
    db.add(obj1)
    db.commit()

    # Vérifie qu'il est en base
    assert db.query(Customer).filter_by(id="cus_test_123").count() == 1

    # Simulation du comportement d’un sync_*
    if db.query(Customer).filter_by(id="cus_test_123").first() is None:
        db.add(Customer(id="cus_test_123", email="duplicate@example.com"))
        db.commit()

    # On vérifie que rien n'a changé
    customers = db.query(Customer).filter_by(id="cus_test_123").all()
    assert len(customers) == 1
    assert customers[0].email == "first@example.com"

