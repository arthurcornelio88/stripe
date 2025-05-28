# scripts/ingest/ingest_price.py
import argparse, json, os, stripe
from dotenv import load_dotenv
from app.db.session import SessionLocal
from app.models.price import Price
from app.transformers.price import stripe_price_to_model
from sqlalchemy.orm import Session

load_dotenv()
stripe.api_key = os.getenv("STRIPE_API_KEY")

def ingest_from_api(db: Session):
    existing_ids = {x.id for x in db.query(Price.id).all()}
    count = 0
    for obj in stripe.Price.list(limit=100).auto_paging_iter():
        if obj["id"] not in existing_ids:
            db.add(stripe_price_to_model(obj))
            print(f"➕ Added price: {obj['id']}")
            count += 1
    return count

def ingest_from_file(db: Session, filepath: str):
    data = json.load(open(filepath))["data"]
    existing_ids = {x.id for x in db.query(Price.id).all()}
    count = 0
    for obj in data:
        if obj["id"] not in existing_ids:
            db.add(stripe_price_to_model(obj))
            print(f"📄 Added from file: {obj['id']}")
            count += 1
    return count

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", choices=["api", "json"], required=True)
    parser.add_argument("--file", help="Path to JSON if source=json")
    args = parser.parse_args()
    db = SessionLocal()
    count = ingest_from_api(db) if args.source == "api" else ingest_from_file(db, args.file)
    db.commit(); db.close()
    print(f"✅ Ingested {count} prices")

if __name__ == "__main__":
    main()
