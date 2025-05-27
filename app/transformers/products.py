from app.models.products import Product
from datetime import datetime

def stripe_product_to_model(data: dict) -> Product:
    return Product(
        id=data["id"],
        name=data.get("name"),
        description=data.get("description"),
        active=data.get("active", True),
        livemode=data.get("livemode", False),
        created=datetime.fromtimestamp(data["created"]),
        updated=datetime.fromtimestamp(data["updated"]),
        default_price=data.get("default_price"),
        tax_code=data.get("tax_code"),
        unit_label=data.get("unit_label"),
        statement_descriptor=data.get("statement_descriptor"),
        url=data.get("url"),
        images=data.get("images", []),
        marketing_features=data.get("marketing_features", []),
        stripe_metadata=data.get("metadata", {}),
        package_dimensions=data.get("package_dimensions"),
        shippable=data.get("shippable")
    )
