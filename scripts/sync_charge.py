import stripe
from app.db.session import SessionLocal
from app.models.charge import Charge
from app.transformers.charge import stripe_charge_to_model
from sqlalchemy.orm import Session
import os
from dotenv import load_dotenv

load_dotenv()
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

def sync_charge():
    db: Session = SessionLocal()
    existing_ids = {x.id for x in db.query(Charge.id).all()}

    count = 0
    for obj in stripe.Charge.list(limit=100).auto_paging_iter():
        if obj["id"] not in existing_ids:
            model = stripe_charge_to_model(obj)
            db.add(model)
            print(f"➕ Added charge: {model.id}")
            count += 1
        else:
            print(f"✅ Skipped existing charge: {obj['id']}")

    db.commit()
    db.close()
    print(f"✅ Synced {count} new charges")

if __name__ == "__main__":
    sync_charge()
