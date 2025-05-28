## 🧱 OLTP.md – Models, Transformers, Sync & Testing for Stripe-Inspired Architecture

---

### 📌 Objective

Build a robust **PostgreSQL OLTP** system inspired by the Stripe API, including:

* a relational schema faithful to Stripe objects
* SQLAlchemy models with strict foreign key constraints
* **transformers** to convert Stripe JSON to ORM objects
* a **manual synchronization system** (no webhooks)
* stable, realistic **unit tests** using Pytest and a real PostgreSQL database

---

## 📁 Project Structure

```
app/
│
├── db/                      # Core database layer
│   ├── base.py              # Base SQLAlchemy declarative class
│   └── session.py           # Session factory

├── models/                  # All Stripe-mapped SQLAlchemy models
│   ├── charge.py
│   ├── customer.py
│   ├── invoice.py
│   ├── payment_intent.py
│   ├── payment_method.py
│   ├── price.py
│   ├── product.py
│   └── subscription.py

├── transformers/            # JSON to ORM transformers
│   ├── charge.py
│   ├── customer.py
│   ├── invoice.py
│   ├── payment_intent.py
│   ├── payment_method.py
│   ├── price.py
│   ├── product.py
│   └── subscription.py

scripts/                     # Manual ingestion scripts
│   ├── sync_all.py
│   ├── sync_charge.py
│   ├── sync_customer.py
│   ├── sync_invoice.py
│   ├── sync_payment_intent.py
│   ├── sync_payment_method.py
│   ├── sync_price.py
│   ├── sync_product.py
│   └── sync_subscription.py

tests/                       # ✅ Full Pytest-based test coverage
│   ├── conftest.py          # Session + DB lifecycle
│   ├── test_charge.py
│   ├── test_customer.py
│   ├── test_invoice.py
│   ├── test_payment_intent.py
│   ├── test_payment_method.py
│   ├── test_price.py
│   ├── test_product.py
│   ├── test_subscription.py
│   └── test_sync_customer.py

schemas/                     # ERD or Mermaid schema diagrams
init_db.py                   # Initialize PostgreSQL db in Docker container   
ini-test.sql                 # Initialize dedicated PostgreSQL db for test in Docker container
.env                         # PostgreSQL + Stripe secrets
docker-compose.yaml          # Database container
Makefile                     # `make test`, etc.
init
README.md

```

---

## 🗃️ 1. **OLTP Models**

Each Stripe object is mapped to a SQLAlchemy model with:

* 🧩 string primary keys (`id`) from Stripe
* 🔐 strict foreign key constraints (e.g. `price_id`, `customer_id`)
* 🧠 `JSONB` fields for nested or flexible data
* 🔁 `relationship(..., backref=...)` for bidirectional access

> Example: `Subscription` links both to `Customer` and `Price`.

✔️ Fully aligned with the Stripe schema
✔️ Models are safe for both operational use and OLAP exports

---

## 🔄 2. **Transformers: Stripe JSON → ORM**

Each entity has a function `stripe_*_to_model(data)` that:

* explicitly maps all relevant fields
* parses UNIX timestamps to Python `datetime`
* gracefully handles optional fields and nested objects
* prepares data for `add()` into the database session

> Example: `stripe_customer_to_model(data)` returns a valid `Customer` ORM object.

---

## 🔁 3. **Manual Sync (No Webhooks Required)**

> 🎯 Strategy: pull data manually via script, instead of listening to webhooks

Each `sync_*.py` script:

* pulls data via `stripe.<object>.list(...)`
* transforms each record with `stripe_*_to_model`
* checks for presence in the DB (by ID)
* inserts only new rows

`sync_all.py` orchestrates the full ingestion in one pass.

✔️ Ideal for batch ingestion, CRON jobs, or cold startups
✔️ Avoids infrastructure overhead (no web server required)

---

## 🧪 4. **Pytest-Based Testing (with PostgreSQL)**

Each model has its own test file `test_<object>.py`, with **two tests**:

### ✅ Test 1: Insertion via Transformer

```python
obj = stripe_customer_to_model(FAKE_CUSTOMER)
db.add(obj)
db.commit()
```

Confirms the object is persisted and properly parsed.

---

### ✅ Test 2: Duplicate Insertion Handling

```python
db.add(Customer(id="cus_123", ...))
db.commit()

# Simulate sync logic
if not db.query(Customer).filter_by(id="cus_123").first():
    db.add(Customer(id="cus_123", ...))
```

Confirms no duplicate row is inserted.

---

### 🧱 Test DB Setup

* dedicated PostgreSQL database: `stripe_test`
* managed by `conftest.py`
* complete `drop_all()` and `create_all()` at test start
* foreign key safety ensured by inserting required parents

---

## ✅ Final Test Result

```bash
$ make test
tests/test_*.py: 16 passed in 2.49s 🎉
```

---

## 🛠️ 5. Next Steps

### ✅ Already Done

* [x] Full OLTP model design
* [x] Clean and isolated transformers
* [x] Manual ingestion logic
* [x] Full test coverage for insertions and duplicates
* [x] DB and Alembic initialization, with automatization (Makefile, for CI/CI)

### 🧩 Still to Do

* [ ] Feed the db with real data (Strip fixtures)

---

## 🏁 Summary

This Stripe-inspired OLTP system is:

* 🔐 relationally safe (with proper constraints)
* 🛠️ testable and test-covered
* 🔁 ingestible in batch mode
* 💬 understandable for developers

> Ready to integrate with OLAP pipelines or dashboards
> Ready for production-grade ingestion with minor tweaks
