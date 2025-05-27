from app.models.invoice import Invoice
from datetime import datetime

def stripe_invoice_to_model(data: dict) -> Invoice:
    return Invoice(
        id=data["id"],
        customer_id=data.get("customer"),
        status=data.get("status"),
        billing_reason=data.get("billing_reason"),
        collection_method=data.get("collection_method"),
        currency=data.get("currency"),
        amount_due=data.get("amount_due"),
        amount_paid=data.get("amount_paid"),
        amount_remaining=data.get("amount_remaining"),
        total=data.get("total"),
        subtotal=data.get("subtotal"),
        created=datetime.fromtimestamp(data["created"]),
        period_start=datetime.fromtimestamp(data["period_start"]),
        period_end=datetime.fromtimestamp(data["period_end"]),
        livemode=data.get("livemode", False),
        auto_advance=data.get("auto_advance", False),
        attempted=data.get("attempted", False),
        attempt_count=data.get("attempt_count", 0),
        hosted_invoice_url=data.get("hosted_invoice_url"),
        invoice_pdf=data.get("invoice_pdf"),
        number=data.get("number"),
        receipt_number=data.get("receipt_number"),
        stripe_metadata=data.get("metadata", {}),
        lines=data.get("lines", {}),
        discounts=data.get("discounts", []),
        automatic_tax=data.get("automatic_tax"),
        payment_settings=data.get("payment_settings"),
        shipping_cost=data.get("shipping_cost"),
        status_transitions=data.get("status_transitions")
    )
