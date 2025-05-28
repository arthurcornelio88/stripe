# End-to-End Data Pipeline: Populate → Fetch → Ingest → Check

> Your complete walkthrough for setting up and verifying the OLTP layer using real Stripe API calls and custom test data.

---

## 🛠️ What This Flow Does

This workflow is designed to **populate the Stripe sandbox** with controlled test data, **fetch it** into structured JSON files, **ingest it** into your local PostgreSQL database using SQLAlchemy models, and finally **verify** that all data has been correctly populated.

We skip the official Stripe CLI fixtures and instead use our own `scripts/populate.py` for full transparency and reusability.

---

## 🧪 Step 1: Populate the Stripe Sandbox

We use a JSON fixture (`fixtures/stripe_batch_fixture.json`) to create:

* Customers
* Products with metadata
* Prices (e.g. EUR/month)
* Subscriptions (with default payment methods)

### 🔁 Smart Behavior:

* Detects and skips existing customers/products/prices
* Optionally deletes and recreates existing subscriptions (`--force` flag)

```bash
# Run once to populate fresh data
make populate

# Or force-delete subscriptions and recreate from scratch
make populate-force
```

📂 Fixture format example:

```json
{
  "customers": [{"email": "alice@example.com", "name": "Alice"}],
  "products": [{
    "name": "Premium Plan",
    "description": "Monthly access",
    "prices": [{"amount": 1200, "currency": "eur", "interval": "month"}]
  }],
  "subscriptions": [{"customer_email": "alice@example.com", "product_name": "Premium Plan"}]
}
```

---

## 📥 Step 2: Fetch Stripe Objects (JSON Dumps)

Two scripts handle the fetching:

1. **`fetch_stripe_data.sh`** (for core objects)
2. **`fetch_payment_methods.sh`** (per-customer enrichment)

```bash
# Downloads JSON data from Stripe's API into local files
make fetch
```

### 🔄 Resources Fetched:

* customers.json
* products.json
* prices.json
* subscriptions.json
* invoices.json
* payment\_intents.json
* charges.json
* payment\_methods.json *(merged from per-customer requests)*

> Output directory: `data/imported_stripe_data/`

🖼️ *\[Insert screenshots of JSON structure here]*

---

## 📦 Step 3: Ingest JSON to PostgreSQL

Each ingestion script handles one table (e.g. `ingest_customer.py`) and uses Pydantic validators + SQLAlchemy models to map raw Stripe objects into relational records.

We support two sources:

* `--source=api` (direct from Stripe)
* `--source=json` with `--file=...`

> All scripts are orchestrated by `scripts/ingest/ingest_all.py` and respect dependency order.

```bash
# Ingest all objects in dependency order from local JSON files
make ingest-all SOURCE=json JSON_DIR=data/imported_stripe_data
```

### ⚠️ Dependency-Safe Order

1. customer
2. payment\_method
3. products
4. price
5. subscription
6. invoice
7. payment\_intent
8. charge

🧩 Mapped using `TABLE_FILE_MAP` for script → file resolution.

🖼️ *\[Insert screenshots of ingestion logs + SQL output]*

---

## ✅ Step 4: Verify Data Integrity

Final check: compare counts between JSON files and live PostgreSQL tables.

```bash
make check-db
```

✔️ For each table:

* Count rows in `data/*.json`
* Count rows in database
* ✅ Matched or ❌ Missing

🖼️ *\[Insert screenshot of full table check summary]*

---

## 💡 Why This Flow?

* No reliance on Stripe CLI fixtures
* Fully scriptable and reproducible
* Easy to debug intermediate steps
* Works with any sandbox or test key

You’re now ready to move on to **OLAP modeling**, confident that your OLTP layer is stable and ACID-safe.

> 🧭 Tip: Everything above is also runnable via `make populate-all`
>
> ```bash
> make init-all && make populate-all
> ```

---

## 📎 Related Docs

* [`create-db-and-migrations.md`](create-db-and-migrations.md)
* [`schemas/schema_er.mmd`](../schemas/schema_er.mmd)

---

© 2025 — Built with 💙 by Arthur Cornélio
