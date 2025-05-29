import os
import sys
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.base import Base
from app.utils.env_loader import load_project_env

# Ajoute le chemin racine au sys.path (utile hors Makefile)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Charge .env.dev ou .env.prod selon ENV
ENV = load_project_env()

# Récupération des variables pour la DB de test (dans .env.dev)
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_TEST_DB = os.getenv("POSTGRES_TEST_DB", "stripe_test")
POSTGRES_TEST_PORT = os.getenv("POSTGRES_TEST_PORT", "5435")

# Connexion SQLAlchemy
TEST_DB_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_TEST_PORT}/{POSTGRES_TEST_DB}"
engine = create_engine(TEST_DB_URL, echo=False)
TestingSessionLocal = sessionmaker(bind=engine)

# Crée/détruit les tables avant/entre chaque test
@pytest.fixture(scope="function", autouse=True)
def setup_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

# Session SQLAlchemy injectable
@pytest.fixture()
def db():
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
