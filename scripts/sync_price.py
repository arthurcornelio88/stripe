import stripe
from app.db.session import SessionLocal
from app.models.price import Price
from app.transformers.price import stripe_price_to_model
from sqlalchemy.orm import Session
import os
from dotenv import load_dotenv

load_dotenv()
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

def sync_price():
    db: Session = SessionLocal()
    existing_ids = {x.id for x in db.query(Price.id).all()}

    count = 0
    for obj in stripe.Price.list(limit=100).auto_paging_iter():
        if obj["id"] not in existing_ids:
            model = stripe_price_to_model(obj)
            db.add(model)
            print(f"➕ Added price: {model.id}")
            count += 1
        else:
            print(f"✅ Skipped existing price: {obj['id']}")

    db.commit()
    db.close()
    print(f"✅ Synced {count} new prices")

if __name__ == "__main__":
    sync_price()
