import stripe
from app.db.session import SessionLocal
from app.models.invoice import Invoice
from app.transformers.invoice import stripe_invoice_to_model
from sqlalchemy.orm import Session
import os
from dotenv import load_dotenv

load_dotenv()
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

def sync_invoice():
    db: Session = SessionLocal()
    existing_ids = {x.id for x in db.query(Invoice.id).all()}

    count = 0
    for obj in stripe.Invoice.list(limit=100).auto_paging_iter():
        if obj["id"] not in existing_ids:
            model = stripe_invoice_to_model(obj)
            db.add(model)
            print(f"➕ Added invoice: {model.id}")
            count += 1
        else:
            print(f"✅ Skipped existing invoice: {obj['id']}")

    db.commit()
    db.close()
    print(f"✅ Synced {count} new invoices")

if __name__ == "__main__":
    sync_invoice()
