import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.base import Base
from app.models.customer import Customer
from app.utils.env_loader import load_project_env
from app.utils.db_url import get_database_url

# Chargement de l'environnement (.env.dev par défaut)
ENV = load_project_env()

# Configuration spécifique à la base de test
POSTGRES_TEST_DB = os.getenv("POSTGRES_TEST_DB", "stripe_db_test")
POSTGRES_TEST_PORT = os.getenv("POSTGRES_TEST_PORT", "5435")

# Connexion SQLAlchemy à la DB de test
TEST_DB_URL = get_database_url(db_override=POSTGRES_TEST_DB, port_override=POSTGRES_TEST_PORT)
engine = create_engine(TEST_DB_URL, echo=(ENV == "DEV"))
TestingSessionLocal = sessionmaker(bind=engine)

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture()
def db():
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
