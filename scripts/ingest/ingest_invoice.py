# scripts/ingest/ingest_invoice.py
import argparse, json, os, stripe
from dotenv import load_dotenv
from app.db.session import SessionLocal
from app.models.invoice import Invoice
from app.transformers.invoice import stripe_invoice_to_model
from app.utils.stripe_helpers import ensure_customer_exists
from sqlalchemy.orm import Session
from app.utils.env_loader import load_project_env

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
    existing_ids = {x.id for x in db.query(Invoice.id).all()}
    count = 0
    for obj in stripe.Invoice.list(limit=100).auto_paging_iter():
        if obj["id"] not in existing_ids:
            db.add(stripe_invoice_to_model(obj))
            print(f"➕ Added invoice: {obj['id']}")
            count += 1
    return count

def ingest_from_file(db: Session, filepath: str):
    with open(filepath, "r") as f:
        raw = json.load(f)
    objects = validate_json_type(raw, expected_type="invoice")

    existing_ids = {x.id for x in db.query(Invoice.id).all()}
    count = 0
    for obj in objects:
        if obj["id"] in existing_ids:
            print(f"✅ Skipped existing object: {obj['id']}")
            continue

        customer_id = obj.get("customer")
        if isinstance(customer_id, dict):
            customer_id = customer_id.get("id")
        ensure_customer_exists(db, customer_id)

        db.add(stripe_invoice_to_model(obj))
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
    print(f"✅ Ingested {count} invoices")

if __name__ == "__main__":
    main()
