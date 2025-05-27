import stripe
from app.db.session import SessionLocal
from app.models.subscription import Subscription
from app.transformers.subscription import stripe_subscription_to_model
from sqlalchemy.orm import Session
import os
from dotenv import load_dotenv

load_dotenv()
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

def sync_subscription():
    db: Session = SessionLocal()
    existing_ids = {x.id for x in db.query(Subscription.id).all()}

    count = 0
    for obj in stripe.Subscription.list(limit=100).auto_paging_iter():
        if obj["id"] not in existing_ids:
            model = stripe_subscription_to_model(obj)
            db.add(model)
            print(f"➕ Added subscription: {model.id}")
            count += 1
        else:
            print(f"✅ Skipped existing subscription: {obj['id']}")

    db.commit()
    db.close()
    print(f"✅ Synced {count} new subscriptions")

if __name__ == "__main__":
    sync_subscription()
