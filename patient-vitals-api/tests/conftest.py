"""
Test fixtures.

Key idea: tests must NOT touch your real database. We spin up a fresh in-memory
SQLite DB per test, create the tables, and override the app's get_db dependency to
use it. Fast, isolated, no Postgres needed.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app


@pytest.fixture()
def db_session():
    # StaticPool + shared in-memory DB so every connection sees the same tables.
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client(db_session):
    # Point the app's get_db at the test session for the duration of the test.
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture()
def sample_patient(client):
    """Creates and returns one patient dict for tests that need an existing patient."""
    resp = client.post("/patients", json={
        "identifier": "MRN-TEST-1",
        "family_name": "Doe",
        "given_name": "Jane",
        "birth_date": "1990-05-01",
        "gender": "female",
    })
    assert resp.status_code == 201
    return resp.json()
