from app.models.payment_method import PaymentMethod
from datetime import datetime

def stripe_payment_method_to_model(data: dict) -> PaymentMethod:
    return PaymentMethod(
        id=data["id"],
        type=data.get("type"),
        created=datetime.fromtimestamp(data["created"]),
        livemode=data.get("livemode", False),
        customer_id=data.get("customer"),
        billing_details=data.get("billing_details", {}),
        stripe_metadata=data.get("metadata", {}),
        us_bank_account=data.get("us_bank_account"),
        card=data.get("card")
    )
