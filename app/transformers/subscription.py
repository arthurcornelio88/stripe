from app.models.subscription import Subscription
from datetime import datetime

def stripe_subscription_to_model(data: dict) -> Subscription:
    return Subscription(
        id=data["id"],
        status=data.get("status"),
        currency=data.get("currency"),
        customer_id=data.get("customer"),
        price_id=data["items"]["data"][0]["price"]["id"] if data.get("items", {}).get("data") else None,
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
        latest_invoice=data.get("latest_invoice")
    )
