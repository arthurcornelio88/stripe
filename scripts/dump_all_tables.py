import os
import json
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from app.db.base import Base
from app.models import (
    customer,
    invoice,
    charge,
    payment_intent,
    payment_method,
    price,
    products,
    subscription
)

# ============ ENVIRONMENT SETUP ============

ENV = os.getenv("ENV", "DEV").upper()
env_file = f".env.{ENV.lower()}"

if os.path.exists(env_file):
    load_dotenv(dotenv_path=env_file)
    print(f"🔧 Loaded environment from {env_file}")
else:
    print(f"❌ Environment file '{env_file}' not found.")
    exit(1)

# ============ DATABASE CONFIG ============

POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", 5434)
POSTGRES_DB = os.getenv("POSTGRES_DB")

DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

# ============ SQLAlchemy ============

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

MODELS = [
    customer.Customer,
    invoice.Invoice,
    charge.Charge,
    payment_intent.PaymentIntent,
    payment_method.PaymentMethod,
    price.Price,
    products.Product,
    subscription.Subscription
]

# ============ DUMP LOGIC ============

def serialize(model_obj):
    return {
        c.name: getattr(model_obj, c.name)
        for c in model_obj.__table__.columns
    }

def dump_to_json():
    session = SessionLocal()
    dump_data = {}
    try:
        for model in MODELS:
            table_name = model.__tablename__
            records = session.query(model).all()
            dump_data[table_name] = [serialize(r) for r in records]
    finally:
        session.close()

    # Output folder
    dump_dir = os.path.join("data", "db_dump")
    os.makedirs(dump_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = os.path.join(dump_dir, f"db_dump_{timestamp}.json")

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(dump_data, f, indent=2, default=str)

    print(f"✅ Dump saved to: {filename}")

# ============ RUN ============

if __name__ == "__main__":
    print(f"🚀 Running database dump in ENV={ENV}")
    dump_to_json()
