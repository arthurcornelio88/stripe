import argparse
import json
import os
import stripe
from dotenv import load_dotenv
from app.db.session import SessionLocal
from app.models.customer import Customer
from app.transformers.customer import stripe_customer_to_model
from sqlalchemy.orm import Session

load_dotenv()
stripe.api_key = os.getenv("STRIPE_API_KEY")

def ingest_from_api(db: Session):
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
    return count

def ingest_from_file(db: Session, filepath: str):
    with open(filepath, "r") as f:
        data = json.load(f)["data"]

    existing_ids = {x.id for x in db.query(Customer.id).all()}
    count = 0
    for obj in data:
        if obj["id"] not in existing_ids:
            model = stripe_customer_to_model(obj)
            db.add(model)
            print(f"📄 Added from file: {model.id}")
            count += 1
        else:
            print(f"✅ Skipped existing customer from file: {obj['id']}")
    return count

def main():
    parser = argparse.ArgumentParser(description="Ingest Stripe customers.")
    parser.add_argument("--source", choices=["api", "json"], required=True)
    parser.add_argument("--file", help="Path to JSON file if source is 'json'")
    args = parser.parse_args()

    db = SessionLocal()
    if args.source == "api":
        print("📡 Fetching from Stripe API...")
        count = ingest_from_api(db)
    elif args.source == "json":
        if not args.file:
            raise ValueError("--file is required when source is 'json'")
        print(f"📂 Ingesting from local file: {args.file}")
        count = ingest_from_file(db, args.file)
    db.commit()
    db.close()
    print(f"✅ Ingested {count} new customers")

if __name__ == "__main__":
    main()
