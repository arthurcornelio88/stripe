import os
import sys
import psycopg2
from sqlalchemy import create_engine
from dotenv import load_dotenv
from app.db.base import Base

import app.models  # imports all SQLAlchemy models via __init__.py


# ============ Load environment ============

ENV = os.getenv("ENV", "DEV").upper()
env_file = f".env.{ENV.lower()}"

if os.path.exists(env_file):
    load_dotenv(dotenv_path=env_file)
    print(f"🔧 Loaded environment from {env_file}")
else:
    print(f"❌ Environment file '{env_file}' not found.")
    sys.exit(1)


# ============ Config ============

POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", 5434)
POSTGRES_DB = os.getenv("POSTGRES_DB", "stripe_db")
POSTGRES_TEST_DB = os.getenv("POSTGRES_TEST_DB", "stripe_test")


# ============ Core Logic ============

def create_db_if_not_exists(dbname, conn_url):
    """Creates a PostgreSQL database if it doesn't exist (DEV only)."""
    conn = psycopg2.connect(conn_url)
    conn.set_session(autocommit=True)
    with conn.cursor() as cur:
        cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (dbname,))
        exists = cur.fetchone()
        if not exists:
            print(f"📦 Creating database '{dbname}'...")
            cur.execute(f'CREATE DATABASE "{dbname}"')
        else:
            print(f"✔️ Database '{dbname}' already exists.")
    conn.close()


def create_tables(database_url: str, label: str):
    """Creates SQLAlchemy tables in a target database."""
    print(f"🧱 Creating tables in {label}...")
    engine = create_engine(database_url)
    Base.metadata.create_all(engine)
    print(f"✅ Tables created in {label}")


# ============ Execution ============

if __name__ == "__main__":
    db_url = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
    test_url = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_TEST_DB}"
    admin_url = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/postgres"

    if ENV == "DEV":
        create_db_if_not_exists(POSTGRES_DB, admin_url)
        create_db_if_not_exists(POSTGRES_TEST_DB, admin_url)
        create_tables(db_url, POSTGRES_DB)
        create_tables(test_url, POSTGRES_TEST_DB)
    elif ENV == "PROD":
        print("🚀 Running in PROD: skipping database creation.")
        create_tables(db_url, POSTGRES_DB)
    else:
        print(f"❌ Unknown ENV: '{ENV}'. Please use ENV=DEV or ENV=PROD.")
        sys.exit(1)
