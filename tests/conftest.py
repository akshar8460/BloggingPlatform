import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config import *
from db_connector import Base, get_db
from main import app
from models import User

client = TestClient(app)

SQLALCHEMY_DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_SERVER}:5432/{DB_TEST_NAME}"
engine = create_engine(SQLALCHEMY_DATABASE_URL)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session")
def db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="module")
def client(db):
    def override_get_db():
        try:
            db = TestingSessionLocal()
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    yield client


@pytest.fixture(scope="module")
def initialize_sample_data(request, db):
    """Initializing testing database with sample records"""
    if not hasattr(request.module, "_sample_data_initialized"):
        test_data = {"name": "john_doe", "email": "admin@test.com", "password": "admin"}
        user = User(**test_data)
        db.add(user)
        db.commit()
        request.module._sample_data_initialized = True
    yield