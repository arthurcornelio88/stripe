import argparse
import os
import sys

# Tables to ingest, in dependency-safe order
TABLES = [
    "customers",
    "payment_methods",  # referenced by payment_intents
    "products",
    "prices",
    "subscriptions",    # depends on customers + prices
    "invoices",         # depends on subscriptions
    "charges",          # depends on invoices/payment_intents
    "payment_intents"   # depends on customers + payment_methods
]

def run_ingestion(table, source, json_dir=None):
    script_path = f"scripts/ingest/ingest_{table}.py"
    if not os.path.exists(script_path):
        print(f"❌ Script not found: {script_path}")
        return

    cmd = f"python {script_path} --source {source}"
    if source == "json":
        file_path = os.path.join(json_dir, f"{table}.json")
        if not os.path.isfile(file_path):
            print(f"⚠️  File missing for {table}: {file_path}")
            return
        cmd += f" --file {file_path}"

    print(f"\n🚀 Ingesting {table} from {source}...")
    os.system(cmd)

def main():
    parser = argparse.ArgumentParser(description="Ingest all Stripe tables in order.")
    parser.add_argument("--source", choices=["api", "json"], required=True)
    parser.add_argument("--json-dir", help="Directory with JSON exports (required for JSON source)")
    args = parser.parse_args()

    if args.source == "json" and not args.json_dir:
        print("❌ --json-dir is required when source is json")
        sys.exit(1)

    for table in TABLES:
        run_ingestion(table, args.source, args.json_dir)

if __name__ == "__main__":
    main()
