import os
import sys
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.base import Base
from app.utils.env_loader import load_project_env
from app.utils.db_url import get_database_url

# Ajoute le chemin racine au sys.path (utile hors Makefile)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Charge .env.dev ou .env.prod selon ENV
ENV = load_project_env()

# Récupère les infos de test
POSTGRES_TEST_DB = os.getenv("POSTGRES_TEST_DB", "stripe_db_test")
POSTGRES_TEST_PORT = os.getenv("POSTGRES_TEST_PORT", "5435")

# Connexion SQLAlchemy vers DB de test
TEST_DB_URL = get_database_url(db_override=POSTGRES_TEST_DB, port_override=POSTGRES_TEST_PORT)
engine = create_engine(TEST_DB_URL, echo=(ENV == "DEV"))
TestingSessionLocal = sessionmaker(bind=engine)

# Crée/Détruit les tables avant chaque test
@pytest.fixture(scope="function", autouse=True)
def setup_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

# Session SQLAlchemy injectable dans tests
@pytest.fixture()
def db():
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
