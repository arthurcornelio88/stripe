import stripe
from app.db.session import SessionLocal
from app.models.products import Product
from app.transformers.products import stripe_products_to_model
from sqlalchemy.orm import Session
import os
from dotenv import load_dotenv

load_dotenv()
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

def sync_products():
    db: Session = SessionLocal()
    existing_ids = {x.id for x in db.query(Product.id).all()}

    count = 0
    for obj in stripe.Product.list(limit=100).auto_paging_iter():
        if obj["id"] not in existing_ids:
            model = stripe_products_to_model(obj)
            db.add(model)
            print(f"➕ Added products: {model.id}")
            count += 1
        else:
            print(f"✅ Skipped existing products: {obj['id']}")

    db.commit()
    db.close()
    print(f"✅ Synced {count} new productss")

if __name__ == "__main__":
    sync_products()
