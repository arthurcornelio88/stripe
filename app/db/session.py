import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.utils.env_loader import load_project_env

# Charger .env.dev ou .env.prod selon ENV
ENV = load_project_env()

# Récupération des variables d'environnement
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", 5434)
POSTGRES_DB = os.getenv("POSTGRES_DB")

# Validation minimale
if not all([POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB]):
    raise ValueError("❌ Missing required database environment variables.")

DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

# SQLAlchemy engine & session
engine = create_engine(DATABASE_URL, echo=(ENV == "DEV"), future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
