"""Tests for the GET /search medication search endpoint.

Seeds a temporary in-memory SQLite database from the committed
`data/synthetic/` fixtures (same fixture pattern as test_seed_db.py) and
overrides the router's session dependency so requests are served from that
hermetic database rather than the on-disk `afia.db`.

Design in `docs/decisions/ADR-005-synthetic-ecosystem-data-model.md`.
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api import search
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

    app.dependency_overrides[search.get_session] = override_get_session
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def test_inn_match_returns_results(client: TestClient):
    response = client.get("/search", params={"q": "paracetamol"})

    assert response.status_code == 200
    assert len(response.json()) > 0


def test_brand_match_returns_results(client: TestClient):
    response = client.get("/search", params={"q": "doliprane"})

    assert response.status_code == 200
    assert len(response.json()) > 0


def test_no_match_returns_empty_list(client: TestClient):
    response = client.get("/search", params={"q": "xyzabc123"})

    assert response.status_code == 200
    assert response.json() == []


def test_search_is_case_insensitive(client: TestClient):
    lower = client.get("/search", params={"q": "paracetamol"})
    upper = client.get("/search", params={"q": "PARACETAMOL"})

    assert lower.status_code == 200
    assert upper.status_code == 200
    assert len(upper.json()) == len(lower.json())
    assert len(upper.json()) > 0
