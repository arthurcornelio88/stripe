from sqlalchemy import create_engine
from app.utils.env_loader import load_project_env
import os

ENV = load_project_env()
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_PORT = os.getenv("POSTGRES_PORT")
POSTGRES_DB = os.getenv("POSTGRES_DB")

# Détection dynamique du sslmode
SSL_MODE = os.getenv("SSL_MODE", "disable" if ENV == "DEV" else "require")

url = f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}?sslmode={SSL_MODE}"
engine = create_engine(url)

try:
    with engine.connect() as conn:
        print(f"✅ Connected to DB [{POSTGRES_DB}] via {POSTGRES_HOST}:{POSTGRES_PORT} (sslmode={SSL_MODE})")
except Exception as e:
    print(f"❌ Failed to connect: {e}")
