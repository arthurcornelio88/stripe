from app.models.customer import Customer
from datetime import datetime

def stripe_customer_to_model(data: dict) -> Customer:
    return Customer(
        id=data["id"],
        email=data.get("email"),
        name=data.get("name"),
        description=data.get("description"),
        phone=data.get("phone"),
        balance=data.get("balance"),
        currency=data.get("currency"),
        delinquent=data.get("delinquent"),
        livemode=data.get("livemode", False),
        deleted=data.get("deleted", False),  # ✅ NEW: support deleted customers
        created=datetime.fromtimestamp(data["created"]) if data.get("created") else None,
        invoice_prefix=data.get("invoice_prefix"),
        next_invoice_sequence=data.get("next_invoice_sequence"),
        address=data.get("address"),
        shipping=data.get("shipping"),
        invoice_settings=data.get("invoice_settings"),
        stripe_metadata=data.get("metadata", {}),
        tax_exempt=data.get("tax_exempt"),
        default_payment_method_id=(
            data.get("invoice_settings", {})
                .get("default_payment_method", {})
                .get("id")
            if isinstance(data.get("invoice_settings"), dict)
            else None
        ),
        test_clock=data.get("test_clock")
    )
