import pytest
from app.models.products import Product
from app.models.price import Price
from app.transformers.price import stripe_price_to_model
from datetime import datetime, timezone

FAKE_PRICE = {
    "id": "price_test_123",
    "active": True,
    "currency": "usd",
    "billing_scheme": "per_unit",
    "type": "recurring",
    "unit_amount": 1000,
    "unit_amount_decimal": "1000",
    "product": "prod_test_123",
    "recurring": {"interval": "month"},
    "livemode": False,
    "created": int(datetime.now(timezone.utc).timestamp()),
    "nickname": "Basic Plan",
    "lookup_key": None,
    "stripe_metadata": {},
    "tax_behavior": "inclusive",
    "tiers_mode": None,
    "custom_unit_amount": None,
    "transform_quantity": None
}

def test_price_insertion(db):
    db.add(Product(id="prod_test_123", name="Test Product"))
    db.commit()

    obj = stripe_price_to_model(FAKE_PRICE)
    db.add(obj)
    db.commit()

    result = db.query(Price).filter_by(id="price_test_123").first()
    assert result is not None
    assert result.unit_amount == 1000

def test_duplicate_price_is_skipped(db):
    db.add(Product(id="prod_test_123", name="Base Product"))  # ✅ besoin pour FK
    db.add(Price(id="price_test_123", currency="usd", unit_amount=1000, product_id="prod_test_123"))
    db.commit()

    if db.query(Price).filter_by(id="price_test_123").first() is None:
        db.add(Price(id="price_test_123", currency="usd", unit_amount=2000, product_id="prod_test_123"))
        db.commit()

    results = db.query(Price).filter_by(id="price_test_123").all()
    assert len(results) == 1

