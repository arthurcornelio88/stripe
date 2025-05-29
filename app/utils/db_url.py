# app/utils/db_url.py

import os

def get_database_url(db_override=None, port_override=None):
    ENV = os.getenv("ENV", "DEV").upper()
    ssl_mode = os.getenv("SSL_MODE", "disable" if ENV == "DEV" else "require")

    user = os.getenv("POSTGRES_USER")
    password = os.getenv("POSTGRES_PASSWORD")
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = port_override or os.getenv("POSTGRES_PORT", "5432")
    db = db_override or os.getenv("POSTGRES_DB")

    return f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}?sslmode={ssl_mode}"