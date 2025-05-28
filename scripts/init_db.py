import os
import psycopg2
from sqlalchemy import create_engine, text
from app.db.base import Base
from dotenv import load_dotenv

import app.models  # Triggers __init__.py which imports all

load_dotenv()

def create_db_if_not_exists(dbname, conn_url):
    conn = psycopg2.connect(conn_url)
    conn.set_session(autocommit=True)  # ✅ clé ici !
    with conn.cursor() as cur:
        cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (dbname,))
        exists = cur.fetchone()
        if not exists:
            print(f"📦 Creating database '{dbname}'...")
            cur.execute(f'CREATE DATABASE "{dbname}"')  # met le nom entre guillemets pour éviter les problèmes de casse
        else:
            print(f"✔️ Database '{dbname}' already exists.")
    conn.close()


def create_tables(database_url: str, label: str):
    print(f"🧱 Creating tables in {label}...")
    engine = create_engine(database_url)
    Base.metadata.create_all(engine)
    print(f"✅ Tables created in {label}")

if __name__ == "__main__":
    POSTGRES_USER = os.getenv("POSTGRES_USER")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
    POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT = os.getenv("POSTGRES_PORT", 5434)
    POSTGRES_DB = os.getenv("POSTGRES_DB", "stripe_db")
    POSTGRES_TEST_DB = os.getenv("POSTGRES_TEST_DB", "stripe_test")

    # Connexion à postgres pour créer les bases
    admin_url = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/postgres"
    create_db_if_not_exists(POSTGRES_DB, admin_url)
    create_db_if_not_exists(POSTGRES_TEST_DB, admin_url)

    # Création des tables dans les deux bases
    db_url = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
    test_url = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_TEST_DB}"

    create_tables(db_url, POSTGRES_DB)
    create_tables(test_url, POSTGRES_TEST_DB)
