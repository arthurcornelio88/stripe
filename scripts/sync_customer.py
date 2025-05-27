import stripe
from app.db.session import SessionLocal
from app.models.customer import Customer
from app.transformers.customer import stripe_customer_to_model
from sqlalchemy.orm import Session
import os
from dotenv import load_dotenv

load_dotenv()
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

def sync_customer():
    db: Session = SessionLocal()
    existing_ids = {x.id for x in db.query(Customer.id).all()}

    count = 0
    for obj in stripe.Customer.list(limit=100).auto_paging_iter():
        if obj["id"] not in existing_ids:
            model = stripe_customer_to_model(obj)
            db.add(model)
            print(f"➕ Added customer: {model.id}")
            count += 1
        else:
            print(f"✅ Skipped existing customer: {obj['id']}")

    db.commit()
    db.close()
    print(f"✅ Synced {count} new customers")

if __name__ == "__main__":
    sync_customer()
