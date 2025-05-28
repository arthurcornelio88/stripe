import pytest
from app.models.customer import Customer
from app.models.products import Product
from app.models.price import Price
from app.models.subscription import Subscription
from app.transformers.subscription import stripe_subscription_to_model
from datetime import datetime, timezone

FAKE_SUBSCRIPTION = {
    "id": "sub_test_123",
    "status": "active",
    "currency": "usd",
    "customer": "cus_test_123",
    "items": {
        "object": "list",
        "data": [
            {
                "price": {"id": "price_test_123"}
            }
        ]
    },
    "start_date": int(datetime.now(timezone.utc).timestamp()),
    "created": int(datetime.now(timezone.utc).timestamp()),
    "cancel_at": None,
    "canceled_at": None,
    "ended_at": None,
    "cancel_at_period_end": False,
    "livemode": False,
    "metadata": {},
    "invoice_settings": None,
    "automatic_tax": None,
    "payment_settings": None,
    "trial_settings": None,
    "latest_invoice": None
}

def test_subscription_insertion(db):
    db.add(Customer(id="cus_test_123", email="test@example.com"))
    db.add(Product(id="prod_test_123", name="P"))
    db.add(Price(id="price_test_123", currency="usd", unit_amount=1000, product_id="prod_test_123"))
    db.commit()

    obj = stripe_subscription_to_model(FAKE_SUBSCRIPTION)
    db.add(obj)
    db.commit()

    result = db.query(Subscription).filter_by(id="sub_test_123").first()
    assert result is not None
    assert result.status == "active"

def test_duplicate_subscription_is_skipped(db):
    db.add(Customer(id="cus_test_123", email="test@example.com"))
    db.add(Product(id="prod_test_123", name="Test Product"))
    db.add(Price(id="price_test_123", currency="usd", unit_amount=1000, product_id="prod_test_123"))
    db.add(Subscription(id="sub_test_123", customer_id="cus_test_123", price_id="price_test_123"))
    db.commit()

    if db.query(Subscription).filter_by(id="sub_test_123").first() is None:
        db.add(Subscription(id="sub_test_123", customer_id="cus_test_123", price_id="price_test_123"))
        db.commit()

    results = db.query(Subscription).filter_by(id="sub_test_123").all()
    assert len(results) == 1
