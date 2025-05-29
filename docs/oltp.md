# 🏠 Stripe OLTP Data Pipeline

> End-to-end system to populate, fetch, ingest and verify transactional Stripe data in a controlled PostgreSQL environment. This README documents **everything from scripts to schema**, giving full reproducibility, safety, and insight into your OLTP foundation.

---

## 🌐 Environment-Safe Design

This pipeline is explicitly **environment-aware**. By default, everything is run in:

* `ENV=DEV`: full feature access
* `ENV=PROD`: blocks destructive/populating commands

```bash
make populate                # allowed in DEV
make populate ENV=PROD       # ❌ blocked
```

---

## 📂 Project Structure

Here's how the OLTP layer is organized, combining database models, transformers, and ingestion logic:

```
app/
├── db/
│   ├── base.py              # Base SQLAlchemy class
│   └── session.py           # DB session factory
├── models/                  # ORM classes mapping to Stripe
├── transformers/            # Stripe JSON to model converters
scripts/
├── ingest/                 # Per-table ingestion scripts
├── fetch_*.sh              # Bash scripts for Stripe API fetch
├── populate.py             # Populates sandbox using fixtures
├── check_db_integrity.py   # Validates row counts
```

The design ensures modularity, testability, and adherence to Stripe’s schema.

---

## 📆 Step 1: Create Databases & Tables

### `make init-db` runs:

* Docker Compose boot
* `init_db.py` connects via psycopg2 to create `stripe_db` and `stripe_db_test`
* Table creation via `Base.metadata.create_all`

```python
create_db_if_not_exists("stripe_db_test", admin_url)
Base.metadata.create_all(engine)  # applied to both DBs
```

The **test database** (`stripe_db_test`) is used by CI and Pytest for isolated evaluation.

📸 *Result after boot:*

<img src="img/make1.png" alt="make 1" width="500"/>
<img src="img/make1_2.png" alt="make 1.2" width="500"/>

---

## 🧪 Unified Dev + Test Setup

The OLTP pipeline is now fully **Dev + Test + Prod ready**.

* ✅ `ENV=DEV` uses two isolated databases: `stripe_db_dev` (port 5434) and `stripe_db_test` (port 5435)
* ✅ Both databases are defined in **`.env.dev`**, no need for `.env.test`
* ✅ Containers are fully isolated using Docker Compose services: `stripe_db_dev` and `stripe_db_test`
* ✅ `init_db.py` creates both DBs and their schemas in one go

```bash
docker-compose up -d        # spins up both DB containers
make init-db                # creates stripe_db_dev + stripe_db_test
```

**Postgres architecture:**

| Container        | Port | DB Name          | Use         |
| ---------------- | ---- | ---------------- | ----------- |
| `stripe_db_dev`  | 5434 | `stripe_db_dev`  | Main ingest |
| `stripe_db_test` | 5435 | `stripe_db_test` | Pytest CI   |

### ✅ Running tests

Tests run on a completely separate DB (`stripe_db_test`) via `make test`:

```bash
make test
```

Tests use:

* SQLAlchemy fixture-based setup
* Auto table reset between functions
* Transactional rollbacks per test

📸 Result:

<img src="img/make7.png" alt="make test result" width="500"/>

---

### ✅ What the Tests Actually Validate

All unit tests pass successfully and validate core ingest and transformation logic. Some examples:

---

#### 🧱 Customer placeholder logic

**`test_ensure_deleted_customer_placeholder_created`**: simulates the creation of a synthetic "deleted" Stripe customer
Verifies placeholder flags, null fields, and Stripe metadata for ghost objects (`cus_DELETEDxxx`)

---

#### 👤 Customer ingestion

**`test_customer_insertion`**: ingests a valid Customer object from fake Stripe JSON
Checks persistence and field mapping (`email`, `created`, `livemode`, etc.)

**`test_duplicate_customer_is_skipped`**: simulates a second ingestion and ensures the first version is preserved
Verifies idempotency by counting only one row for the same `customer.id`

---

#### 💳 Charge ingestion

**`test_charge_insertion`**: inserts a valid Charge linked to mock `Customer`, `Invoice`, and `PaymentIntent`
Checks amount fields, foreign keys, and charge-specific metadata (`paid`, `captured`, `receipt_*`)

**`test_duplicate_charge_is_skipped`**: inserts a Charge that already exists and ensures no duplicate is stored
Asserts that the table contains only one instance of the charge ID

---

#### 🧪 Isolation & cleanup

All tests use a `db` fixture linked to `stripe_db_test`
The test DB is wiped and rebuilt before each session (`drop_all → create_all`)

Each test runs in an isolated SQLAlchemy session
Tables are cleaned between tests to ensure full transactional independence

---

### 🔁 Stripe Sync Scripts (Live Ingestion)

A full set of `sync_*` ingestion scripts maps Stripe live API objects into normalized Postgres tables.
Each script follows the correct dependency graph to maintain referential integrity.

| Step | Resource        | Script name             | Depends on                    |
| ---- | --------------- | ----------------------- | ----------------------------- |
| 1    | Products        | `sync_products()`       | –                             |
| 2    | Prices          | `sync_price()`          | `products`                    |
| 3    | Customers       | *(covered in tests)*    | –                             |
| 4    | Payment Methods | `sync_payment_method()` | `customers`                   |
| 5    | Subscriptions   | `sync_subscription()`   | `customers`, `prices`         |
| 6    | Payment Intents | `sync_payment_intent()` | `customers`, `invoices`       |
| 7    | Invoices        | `sync_invoice()`        | `customers`, `prices`         |
| 8    | Charges         | *(covered in tests)*    | `payment_intents`, `invoices` |

Each script:

* Authenticates via `STRIPE_SECRET_KEY` from `.env.dev`
* Lists remote Stripe objects via `.list().auto_paging_iter()`
* Skips existing rows using a local `existing_ids` set
* Transforms via `stripe_*_to_model()`, and persists new records

```python
if obj["id"] not in existing_ids:
    model = stripe_invoice_to_model(obj)
    db.add(model)
```

Scripts print concise ingestion output:

* `➕ Added invoice: ...`
* `✅ Skipped existing invoice: ...`

---

💡 You now have a fully production-ready ingestion chain, fully validated through unit tests and live API data — reliable, idempotent, and scalable.

Souhaites-tu aussi que je fasse une passe de clean-up globale ou que je t’assemble le `oltp.md` complet prêt à push ?


---

## 🔖 Step 2: Migrations (Alembic)

```bash
make init-migration
```

Migrations are either:

* Created via `alembic revision --autogenerate`
* Skipped if already present

Output shown:

<img src="img/make2.png" alt="make 2" width="500"/>

---

## 🚀 Step 3: Populate Stripe Sandbox

```bash
make populate
make populate-force  # resets subscriptions
```

### Highlights from `populate.py`:

* ✅ **Idempotent**: skips duplicates using `stripe.Customer.list(email=...)`
* ⚖️ Custom metadata tagging for products
* ⚖️ Price matching by value+interval+currency
* ⚡ Automatic subscription creation with tokenized card (`tok_visa`)

```python
if subscription_exists(): continue
stripe.PaymentMethod.attach(...)
stripe.Customer.modify(...)
stripe.Subscription.create(...)
```

<img src="img/make3.png" alt="make 3" width="500"/>

---

## 📥 Step 4: Fetch JSON from Stripe

```bash
make fetch
```

### Scripts used:

* `fetch_stripe_data.sh`
* `fetch_payment_methods.sh`

These use `curl` to:

* Expand nested objects (e.g., customer.invoice\_settings)
* Merge all customer-linked `payment_methods` into a unified file

<img src="img/make4.png" alt="make 4" width="500"/>

---

## 🧰 Step 5: Ingest to PostgreSQL

```bash
make ingest-all SOURCE=json JSON_DIR=data/imported_stripe_data
```

Each table is ingested through a three-step pipeline:

> **`ingest_{table}.py` ➔ transformer ➔ SQLAlchemy model**

This ensures:

* Clear mapping logic in transformer layer
* Clean data validation and flattening
* Separation of concerns between API data and DB models

```python
if obj["id"] not in existing_ids:
    db.add(stripe_customer_to_model(obj))
```

You can ingest:

* **All tables**: via `ingest_all.py`
* **Single table**: `make ingest-customer SOURCE=json FILE=data/imported_stripe_data/customers.json`

<img src="img/make5.png" alt="make 5" width="500"/>
<img src="img/make5_1.png" alt="make 5_1" width="500"/>

---

## 🔎 Step 6: Verify JSON vs DB Integrity

```bash
make check-db
```

`check_db_integrity.py` compares row counts between JSON exports and PostgreSQL tables:

```python
SELECT COUNT(*) FROM {table}
```

<img src="img/make6.png" alt="make 6" width="500"/>

---

## 🧪 Schema Coverage (ex.: Customer)

Each `ingest_{table}.py` script is part of a well-structured ingestion chain:

> **`ingest_* → transformer_* → model`**

* The ingestion script parses raw JSON and **calls a transformer**.
* The transformer **maps Stripe's JSON into SQLAlchemy-compatible objects**.
* The ORM object is then added to the DB session using `db.add(...)`.

This pipeline ensures:

* Full decoupling from external schemas
* Proper field typing and JSON flattening
* High readability and maintainability

### Model: `app/models/customer.py`

```python
class Customer(Base):
    ...
    deleted = Column(Boolean, default=False)  # supports stripe deletion
    address = Column(JSONB)
    test_clock = Column(String)
```

Supports:

* Nested fields like `address`, `shipping`, `invoice_settings`
* Optional and nullable fields
* Stripe-specific metadata (`livemode`, `deleted`, etc.)

### Transformer: `stripe_customer_to_model()`

```python
default_payment_method_id = (
    data.get("invoice_settings", {}).get("default_payment_method", {}).get("id")
)
```

The transformer:

* Validates structure
* Handles optional nested keys
* Converts UNIX timestamps to Python `datetime`

---

## 📊 Summary: What You Get

| Layer    | Tool       | Behavior                        |
| -------- | ---------- | ------------------------------- |
| Infra    | Docker     | Compose PostgreSQL + volumes    |
| Schema   | Alembic    | Migrations auto-managed         |
| Populate | Stripe SDK | Custom idempotent API calls     |
| Fetch    | cURL/bash  | Expanded + batched object pulls |
| Ingest   | SQLAlchemy | Per-table validators + mappers  |
| Verify   | Python     | Row-count diff checker          |

---

## 📜 Appendix: Scripts Glossary

| File                       | Description                         |
| -------------------------- | ----------------------------------- |
| `init_db.py`               | Creates databases via psycopg2      |
| `populate.py`              | Populates Stripe sandbox w/ fixture |
| `fetch_stripe_data.sh`     | Fetches core Stripe objects         |
| `fetch_payment_methods.sh` | Fetches customer-linked methods     |
| `ingest/ingest_{table}.py` | Table-specific JSON ingestion       |
| `ingest_all.py`            | Ingests all in dependency order     |
| `check_db_integrity.py`    | Compares row counts (JSON vs DB)    |

---

To go further with schema diagrams and OLAP extensions, see the [main README](../README.md) or `docs/`.
