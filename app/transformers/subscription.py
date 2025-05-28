from app.models.subscription import Subscription
from datetime import datetime

def stripe_subscription_to_model(data: dict) -> Subscription:
    """
    Transform Stripe subscription API data into a Subscription ORM object.

    Handles nested structures and optional fields safely.
    """
    # Handle customer: can be a dict or a string (ID)
    customer = data.get("customer")
    customer_id = customer["id"] if isinstance(customer, dict) else customer

    # Defensive extraction of subscription item and recurring plan info
    items = data.get("items", {}).get("data", [])
    first_item = items[0] if items else {}
    price = first_item.get("price", {}) if first_item else {}
    subscription_item_id = first_item.get("id")
    plan_interval = price.get("recurring", {}).get("interval")

    return Subscription(
        id=data["id"],
        status=data.get("status"),
        currency=data.get("currency"),
        customer_id=customer_id,
        price_id=price.get("id"),
        start_date=datetime.fromtimestamp(data["start_date"]),
        created=datetime.fromtimestamp(data["created"]),
        cancel_at=datetime.fromtimestamp(data["cancel_at"]) if data.get("cancel_at") else None,
        canceled_at=datetime.fromtimestamp(data["canceled_at"]) if data.get("canceled_at") else None,
        ended_at=datetime.fromtimestamp(data["ended_at"]) if data.get("ended_at") else None,
        cancel_at_period_end=data.get("cancel_at_period_end", False),
        livemode=data.get("livemode", False),
        stripe_metadata=data.get("metadata", {}),
        items=data.get("items", {}),
        invoice_settings=data.get("invoice_settings"),
        automatic_tax=data.get("automatic_tax"),
        payment_settings=data.get("payment_settings"),
        trial_settings=data.get("trial_settings"),
        latest_invoice=data.get("latest_invoice"),
        subscription_item_id=subscription_item_id,
        plan_interval=plan_interval
    )
