from app.models.payment_intent import PaymentIntent
from datetime import datetime

def stripe_payment_intent_to_model(data: dict) -> PaymentIntent:
    return PaymentIntent(
        id=data["id"],
        status=data.get("status"),
        currency=data.get("currency"),
        amount=data.get("amount"),
        amount_capturable=data.get("amount_capturable"),
        amount_received=data.get("amount_received"),
        capture_method=data.get("capture_method"),
        confirmation_method=data.get("confirmation_method"),
        client_secret=data.get("client_secret"),
        created=datetime.fromtimestamp(data["created"]),
        canceled_at=datetime.fromtimestamp(data["canceled_at"]) if data.get("canceled_at") else None,
        cancellation_reason=data.get("cancellation_reason"),
        livemode=data.get("livemode", False),
        customer_id=data.get("customer"),
        payment_method=data.get("payment_method"),
        description=data.get("description"),
        receipt_email=data.get("receipt_email"),
        payment_method_types=data.get("payment_method_types", []),
        payment_method_options=data.get("payment_method_options"),
        amount_details=data.get("amount_details"),
        metadata=data.get("metadata", {}),
        next_action=data.get("next_action"),
        statement_descriptor=data.get("statement_descriptor"),
        statement_descriptor_suffix=data.get("statement_descriptor_suffix")
    )
