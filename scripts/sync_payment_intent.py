import stripe
from app.db.session import SessionLocal
from app.models.payment_intent import PaymentIntent
from app.transformers.payment_intent import stripe_payment_intent_to_model
from sqlalchemy.orm import Session
import os
from dotenv import load_dotenv

load_dotenv()
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

def sync_payment_intent():
    db: Session = SessionLocal()
    existing_ids = {x.id for x in db.query(PaymentIntent.id).all()}

    count = 0
    for obj in stripe.PaymentIntent.list(limit=100).auto_paging_iter():
        if obj["id"] not in existing_ids:
            model = stripe_payment_intent_to_model(obj)
            db.add(model)
            print(f"➕ Added payment_intent: {model.id}")
            count += 1
        else:
            print(f"✅ Skipped existing payment_intent: {obj['id']}")

    db.commit()
    db.close()
    print(f"✅ Synced {count} new payment_intents")

if __name__ == "__main__":
    sync_payment_intent()
