from app.models.price import Price
from datetime import datetime

def stripe_price_to_model(data: dict) -> Price:
    return Price(
        id=data["id"],
        active=data.get("active", True),
        currency=data.get("currency"),
        billing_scheme=data.get("billing_scheme"),
        type=data.get("type"),
        unit_amount=data.get("unit_amount"),
        unit_amount_decimal=data.get("unit_amount_decimal"),
        product_id=data.get("product"),
        recurring=data.get("recurring"),
        livemode=data.get("livemode", False),
        created=datetime.fromtimestamp(data["created"]),
        nickname=data.get("nickname"),
        lookup_key=data.get("lookup_key"),
        stripe_metadata=data.get("metadata", {}),
        tax_behavior=data.get("tax_behavior"),
        tiers_mode=data.get("tiers_mode"),
        custom_unit_amount=data.get("custom_unit_amount"),
        transform_quantity=data.get("transform_quantity")
    )
