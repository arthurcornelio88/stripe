# scripts/ingest/ingest_all.py

import argparse
import os
import sys

# Tables to ingest in dependency-safe order
TABLES = [
    "customer",
    "payment_method",      # referenced by payment_intents
    "products",
    "price",
    "subscription",        # depends on customers + prices
    "invoice",             # depends on subscriptions
    "payment_intent",      # depends on customers + payment_methods
    "charge"               # depends on payment_intents/invoices
]

# Explicit map from table name to JSON filename
TABLE_FILE_MAP = {
    "customer": "customers.json",
    "payment_method": "payment_methods.json",
    "products": "products.json",
    "price": "prices.json",
    "subscription": "subscriptions.json",
    "invoice": "invoices.json",
    "payment_intent": "payment_intents.json",
    "charge": "charges.json"
}

def run_ingestion(table, source, json_dir=None):
    script_path = f"scripts/ingest/ingest_{table}.py"
    if not os.path.exists(script_path):
        print(f"❌ Script not found: {script_path}")
        return

    cmd = f"python {script_path} --source {source}"
    if source == "json":
        json_filename = TABLE_FILE_MAP.get(table)
        file_path = os.path.join(json_dir, json_filename)
        if not os.path.isfile(file_path):
            print(f"⚠️  File missing for {table}: {file_path}")
            return
        cmd += f" --file {file_path}"

    print(f"\n🚀 Ingesting {table} from {source}...")
    os.system(cmd)

def main():
    parser = argparse.ArgumentParser(description="Ingest all Stripe tables in order.")
    parser.add_argument("--source", choices=["api", "json"], required=True)
    parser.add_argument("--json-dir", help="Directory with JSON exports (required if source is json)")
    args = parser.parse_args()

    if args.source == "json" and not args.json_dir:
        print("❌ --json-dir is required when source is json")
        sys.exit(1)

    for table in TABLES:
        run_ingestion(table, args.source, args.json_dir)

if __name__ == "__main__":
    main()
