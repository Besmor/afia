"""Tests for the GET /pharmacies/{pharmacy_id} standalone lookup endpoint.

Same seeded in-memory SQLite fixture pattern as test_search.py.
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api import pharmacies
from app.data.seed_db import SYNTHETIC_DIR, seed_all
from app.main import app
from app.models.pharmacy import Base


@pytest.fixture()
def client():
    """A TestClient wired to a fresh, seeded, in-memory SQLite database."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    session_local = sessionmaker(bind=engine)

    with session_local() as session:
        seed_all(session, SYNTHETIC_DIR)
        session.commit()

    def override_get_session():
        session = session_local()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[pharmacies.get_session] = override_get_session
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def test_valid_pharmacy_id_returns_200(client: TestClient):
    response = client.get("/pharmacies/Pharmacy_01")

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == "Pharmacy_01"
    assert "name" in body
    assert "opens_at" in body


def test_valid_pharmacy_id_excludes_stock_fields(client: TestClient):
    response = client.get("/pharmacies/Pharmacy_01")

    assert response.status_code == 200
    body = response.json()
    assert "stock_items" not in body
    assert "medications" not in body


def test_invalid_pharmacy_id_returns_404(client: TestClient):
    response = client.get("/pharmacies/Pharmacy_does_not_exist")

    assert response.status_code == 404
