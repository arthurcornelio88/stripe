import json
from datetime import datetime
from app.models.charge import Charge

def stripe_charge_to_model(data: dict) -> Charge:
    """
    Transforms a raw Stripe charge object into a SQLAlchemy Charge model.
    Ensures all dict fields are JSON-serialized for storage.
    """

    def serialize(value):
        """Safely serialize dicts/lists to JSON strings."""
        return json.dumps(value) if isinstance(value, (dict, list)) else value

    def extract_payment_intent(obj):
        """Handles payment_intent being a string or an embedded object."""
        return obj.get("payment_intent", {}).get("id") if isinstance(obj.get("payment_intent"), dict) else obj.get("payment_intent")

    return Charge(
        id=data["id"],
        amount=data.get("amount"),
        amount_captured=data.get("amount_captured"),
        amount_refunded=data.get("amount_refunded"),
        currency=data.get("currency"),
        status=data.get("status"),
        paid=data.get("paid", False),
        captured=data.get("captured", False),
        disputed=data.get("disputed", False),
        refunded=data.get("refunded", False),
        created=datetime.fromtimestamp(data["created"]),
        livemode=data.get("livemode", False),
        payment_intent=extract_payment_intent(data),
        payment_method=data.get("payment_method"),
        receipt_url=data.get("receipt_url"),
        receipt_email=data.get("receipt_email"),
        receipt_number=data.get("receipt_number"),
        description=data.get("description"),
        statement_descriptor=data.get("statement_descriptor"),
        statement_descriptor_suffix=data.get("statement_descriptor_suffix"),
        balance_transaction=data.get("balance_transaction"),
        invoice_id=data.get("invoice"),

        # ✅ JSON fields, must be serialized to strings before insert
        billing_details=serialize(data.get("billing_details", {})),
        outcome=serialize(data.get("outcome")),
        fraud_details=serialize(data.get("fraud_details", {})),
        payment_method_details=serialize(data.get("payment_method_details")),
        stripe_metadata=serialize(data.get("metadata", {})),
    )
