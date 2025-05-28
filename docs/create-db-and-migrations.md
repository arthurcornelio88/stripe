# 🧱 Creating and Managing Databases & Migrations

This guide explains how the OLTP pipeline is initialized and managed — from spinning up the database to generating Alembic migrations. It documents everything behind the `make init-all` and `make reset-all` commands.

---

## 📦 Step-by-Step: First-Time Setup

These steps ensure you have both the database **and** the migration system correctly initialized.

```bash
# 1. Clone the repo and navigate into it
git clone https://github.com/arthurcornelio88/stripe.git
cd stripe

# 2. Sync dependencies using uv
uv sync

# 3. Activate the virtual environment
source .venv/bin/activate

# 4. Initialize everything (Docker, databases, tables, Alembic)
make init-all
````

What this does:

* Starts the PostgreSQL container via Docker
* Creates `stripe_db` and `stripe_test` if they don't exist
* Initializes tables in both using your SQLAlchemy models
* Verifies creation via `psql \dt`
* Applies Alembic migrations only if needed

---

## 🔄 Development Reset: Nuking Everything

If you're testing changes or want to reset everything cleanly, use:

```bash
make reset-all
```

This will:

* Stop and remove all Docker containers and volumes
* Delete all Alembic migration files
* Recreate `stripe_db` and `stripe_test`
* Rebuild tables
* Reapply a clean migration

---

## 🛠 Makefile Commands Reference

| Command                | Description                                                           |
| ---------------------- | --------------------------------------------------------------------- |
| `make init-db`         | Starts DB container, creates both databases, and builds tables        |
| `make init-migration`  | Creates and applies first Alembic migration (only if none exists)     |
| `make init-all`        | Safe full setup — databases, tables, and initial migration            |
| `make migrate m="..."` | Creates a new migration based on changes in the models                |
| `make upgrade-db`      | Applies all unapplied migrations                                      |
| `make reset-migration` | Destroys and regenerates migrations + re-applies them                 |
| `make reset-db`        | Stops Docker, deletes volumes, and reinitializes databases and tables |
| `make reset-all`       | Full reset: database + migration — for development clean slates       |

---

## 📜 Alembic Workflow Logic

The Alembic integration uses the `env.py` script to dynamically build the database URL from `.env`:

```python
from dotenv import load_dotenv
load_dotenv()

SQLALCHEMY_DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
config.set_main_option("sqlalchemy.url", SQLALCHEMY_DATABASE_URL)
```

All models are imported in `app/models/__init__.py`, so Alembic can detect schema changes automatically.

---

## ✅ Table Verification

After initialization, the following tables should exist:

* `customers`
* `products`
* `prices`
* `subscriptions`
* `invoices`
* `charges`
* `payment_methods`
* `payment_intents`

You’ll see visual confirmation in the terminal via `psql -c "\dt"`.

---

## 💡 Tips

* Your test database (`stripe_test`) is created with the same schema — perfect for CI or isolated testing.
* Never run `reset-all` unless you’re sure you want to destroy all data.
* You can add more environments (staging, prod) using `.env` profiles and different Docker configs.

---