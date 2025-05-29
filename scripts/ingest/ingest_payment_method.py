# scripts/ingest/ingest_payment_method.py
import argparse, json, os, stripe
from dotenv import load_dotenv
from app.db.session import SessionLocal
from app.models.payment_method import PaymentMethod
from app.transformers.payment_method import stripe_payment_method_to_model
from sqlalchemy.orm import Session
from utils import load_project_env

ENV = load_project_env()
stripe.api_key = os.getenv("STRIPE_API_KEY")

def validate_json_type(data, expected_type: str):
    if not data:
        raise ValueError("❌ JSON file is empty or invalid format")

    if isinstance(data, dict):
        objects = data.get("data", [])
    elif isinstance(data, list):
        objects = data
    else:
        raise ValueError("❌ Unrecognized JSON structure")

    if not objects:
        raise ValueError("❌ No objects found in 'data' array.")

    obj_type = objects[0].get("object")
    if obj_type != expected_type:
        raise ValueError(f"❌ Expected object type '{expected_type}', but got '{obj_type}'.")

    print(f"🔒 File validation passed: {len(objects)} object(s) of type '{expected_type}' ✔️")
    return objects

def ingest_from_api(db: Session):
    existing_ids = {x.id for x in db.query(PaymentMethod.id).all()}
    count = 0
    for obj in stripe.PaymentMethod.list(limit=100).auto_paging_iter():
        if obj["id"] not in existing_ids:
            db.add(stripe_payment_method_to_model(obj))
            print(f"➕ Added payment_method: {obj['id']}")
            count += 1
    return count

def ingest_from_file(db: Session, filepath: str):
    with open(filepath, "r") as f:
        raw = json.load(f)
    objects = validate_json_type(raw, expected_type="payment_method")

    existing_ids = {x.id for x in db.query(PaymentMethod.id).all()}
    count = 0
    for obj in objects:
        if obj["id"] not in existing_ids:
            db.add(stripe_payment_method_to_model(obj))
            print(f"📄 Added from file: {obj['id']}")
            count += 1
        else:
            print(f"✅ Skipped existing object: {obj['id']}")
    return count

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", choices=["api", "json"], required=True)
    parser.add_argument("--file", help="Path to JSON if source=json")
    args = parser.parse_args()
    db = SessionLocal()
    count = ingest_from_api(db) if args.source == "api" else ingest_from_file(db, args.file)
    db.commit(); db.close()
    print(f"✅ Ingested {count} payment methods.")

if __name__ == "__main__":
    main()
