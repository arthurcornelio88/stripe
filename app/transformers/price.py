from app.models.price import Price
from datetime import datetime
import json

def stripe_price_to_model(data: dict) -> Price:
    # product peut être une string ou un dict
    product = data.get("product")
    product_id = product.get("id") if isinstance(product, dict) else product

    return Price(
        id=data["id"],
        active=data.get("active", True),
        currency=data.get("currency"),
        billing_scheme=data.get("billing_scheme"),
        type=data.get("type"),
        unit_amount=data.get("unit_amount"),
        unit_amount_decimal=data.get("unit_amount_decimal"),
        product_id=product_id,
        recurring=json.dumps(data.get("recurring")) if data.get("recurring") else None,
        livemode=data.get("livemode", False),
        created=datetime.fromtimestamp(data["created"]),
        nickname=data.get("nickname"),
        lookup_key=data.get("lookup_key"),
        stripe_metadata=data.get("metadata", {}),
        tax_behavior=data.get("tax_behavior"),
        tiers_mode=data.get("tiers_mode"),
        custom_unit_amount=json.dumps(data.get("custom_unit_amount")) if data.get("custom_unit_amount") else None,
        transform_quantity=json.dumps(data.get("transform_quantity")) if data.get("transform_quantity") else None
    )
