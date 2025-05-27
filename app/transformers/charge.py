from app.models.charge import Charge
from datetime import datetime

def stripe_charge_to_model(data: dict) -> Charge:
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
        payment_intent=data.get("payment_intent"),
        payment_method=data.get("payment_method"),
        receipt_url=data.get("receipt_url"),
        receipt_email=data.get("receipt_email"),
        receipt_number=data.get("receipt_number"),
        billing_details=data.get("billing_details", {}),
        outcome=data.get("outcome"),
        payment_method_details=data.get("payment_method_details"),
        stripe_metadata=data.get("metadata", {}),
        fraud_details=data.get("fraud_details", {}),
        description=data.get("description"),
        statement_descriptor=data.get("statement_descriptor"),
        statement_descriptor_suffix=data.get("statement_descriptor_suffix"),
        balance_transaction=data.get("balance_transaction"),
        invoice_id=data.get("invoice")  # if invoice object present
    )
