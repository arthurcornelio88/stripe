import os
import json
from sqlalchemy import create_engine, text
from app.utils.env_loader import load_project_env

# Load correct .env (DEV or PROD)
ENV = load_project_env()

# DB config
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5434")
POSTGRES_DB = os.getenv("POSTGRES_DB")

DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
engine = create_engine(DATABASE_URL)

# JSON mapping
TABLE_JSON_MAPPING = {
    "customers": "customers.json",
    "payment_methods": "payment_methods.json",
    "products": "products.json",
    "prices": "prices.json",
    "subscriptions": "subscriptions.json",
    "invoices": "invoices.json",
    "payment_intents": "payment_intents.json",
    "charges": "charges.json"
}

JSON_DIR = "data/imported_stripe_data"

def get_json_object_count(filepath: str) -> int:
    with open(filepath, "r") as f:
        data = json.load(f)
        if isinstance(data, list):
            return len(data)
        elif isinstance(data, dict):
            if "data" in data and isinstance(data["data"], list):
                return len(data["data"])
            return 1 if "id" in data else 0
        return 0

def get_db_table_count(conn, table: str) -> int:
    result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
    return result.scalar()

def main():
    print(f"\n🔍 Comparing JSON fixture counts with DB (ENV={ENV})...\n")
    with engine.connect() as conn:
        for table, filename in TABLE_JSON_MAPPING.items():
            json_path = os.path.join(JSON_DIR, filename)
            try:
                json_count = get_json_object_count(json_path)
                db_count = get_db_table_count(conn, table)
                status = "✅" if json_count == db_count else "❌"
                print(f"{status} {table:<18} | JSON: {json_count:<3} vs DB: {db_count}")
            except Exception as e:
                print(f"❌ Error processing {table}: {e}")
    print("\n✅ Done.")

if __name__ == "__main__":
    main()
