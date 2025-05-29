# scripts/init_db.py

import os, sys, psycopg2
from sqlalchemy import create_engine
from app.db.base import Base
from app.utils.env_loader import load_project_env
from app.utils.db_url import get_database_url
import app.models  # loads models

# ============ Load env ============

ENV = load_project_env()

POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", 5434)
POSTGRES_DB = os.getenv("POSTGRES_DB", "stripe_db")
POSTGRES_TEST_DB = os.getenv("POSTGRES_TEST_DB", "stripe_test")
POSTGRES_TEST_PORT = os.getenv("POSTGRES_TEST_PORT", 5435)


# ============ Helpers ============

def create_db_if_not_exists(dbname, host, port, user, password):
    """Connecte à postgres pour créer une base si absente."""
    conn_url = f"postgresql://{user}:{password}@{host}:{port}/postgres"
    conn = psycopg2.connect(conn_url)
    conn.set_session(autocommit=True)
    with conn.cursor() as cur:
        cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (dbname,))
        if not cur.fetchone():
            print(f"📦 Creating database '{dbname}'...")
            cur.execute(f'CREATE DATABASE "{dbname}"')
        else:
            print(f"✔️ Database '{dbname}' already exists.")
    conn.close()

def create_tables(url: str, label: str):
    print(f"🧱 Creating tables in {label}...")
    engine = create_engine(url)
    Base.metadata.create_all(engine)
    print(f"✅ Tables created in {label}")


# ============ Main Logic ============

if __name__ == "__main__":
    if ENV == "DEV":
        # Create both databases
        create_db_if_not_exists(POSTGRES_DB, POSTGRES_HOST, POSTGRES_PORT, POSTGRES_USER, POSTGRES_PASSWORD)
        create_db_if_not_exists(POSTGRES_TEST_DB, POSTGRES_HOST, POSTGRES_TEST_PORT, POSTGRES_USER, POSTGRES_PASSWORD)

        # Create tables in both
        create_tables(get_database_url(), POSTGRES_DB)
        create_tables(get_database_url(db_override=POSTGRES_TEST_DB, port_override=POSTGRES_TEST_PORT), POSTGRES_TEST_DB)

    elif ENV == "PROD":
        print("🚀 Running in PROD: skipping database creation.")
        create_tables(get_database_url(), POSTGRES_DB)

    else:
        print(f"❌ Unknown ENV: '{ENV}'")
        sys.exit(1)
