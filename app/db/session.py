import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.utils.env_loader import load_project_env
from app.utils.db_url import get_database_url

# Charger .env.dev ou .env.prod selon ENV
ENV = load_project_env()
engine = create_engine(get_database_url(), echo=(ENV == "DEV"), future=True)

# SQLAlchemy engine & session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
