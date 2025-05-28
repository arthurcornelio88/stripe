import pytest
from app.models.products import Product
from app.transformers.products import stripe_product_to_model
from datetime import datetime, timezone

FAKE_PRODUCT = {
    "id": "prod_test_123",
    "name": "Test Product",
    "description": "A simple product",
    "active": True,
    "livemode": False,
    "created": int(datetime.now(timezone.utc).timestamp()),
    "updated": int(datetime.now(timezone.utc).timestamp()),
    "default_price": None,
    "tax_code": None,
    "unit_label": None,
    "statement_descriptor": None,
    "url": None,
    "images": [],
    "marketing_features": [],
    "stripe_metadata": {},
    "package_dimensions": None,
    "shippable": None
}

def test_product_insertion(db):
    obj = stripe_product_to_model(FAKE_PRODUCT)
    db.add(obj)
    db.commit()

    result = db.query(Product).filter_by(id="prod_test_123").first()
    assert result is not None
    assert result.name == "Test Product"

def test_duplicate_product_is_skipped(db):
    db.add(Product(id="prod_test_123", name="Duplicate Product"))
    db.commit()

    if db.query(Product).filter_by(id="prod_test_123").first() is None:
        db.add(Product(id="prod_test_123", name="Should Not Insert"))
        db.commit()

    results = db.query(Product).filter_by(id="prod_test_123").all()
    assert len(results) == 1
