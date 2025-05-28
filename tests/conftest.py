import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.base import Base
import os

TEST_DB_URL = os.getenv("TEST_DATABASE_URL", "postgresql://stripe_user:stripe_pass@localhost:5432/stripe_test")

engine = create_engine(TEST_DB_URL)
TestingSessionLocal = sessionmaker(bind=engine)

@pytest.fixture(scope="function", autouse=True)
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
