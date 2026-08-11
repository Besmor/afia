"""Tests for the GET /medications/autocomplete endpoint.

Same seeded in-memory SQLite fixture pattern as test_search.py.
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api import medications
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

    app.dependency_overrides[medications.get_session] = override_get_session
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def test_autocomplete_returns_matches(client: TestClient):
    response = client.get("/medications/autocomplete", params={"q": "para"})

    assert response.status_code == 200
    body = response.json()
    assert len(body) > 0
    assert all(row["inn"].lower().startswith("para") for row in body)
    assert {"id", "inn", "form", "strength"} <= body[0].keys()


def test_empty_query_returns_empty_list(client: TestClient):
    response = client.get("/medications/autocomplete", params={"q": ""})

    assert response.status_code == 200
    assert response.json() == []


def test_prefix_match_ranks_before_substring_match(client: TestClient):
    """A query that is an INN-prefix for one row must rank ahead of rows only
    matched by mid-string substring or brand name, per the ranking rule
    documented on the endpoint.
    """
    response = client.get("/medications/autocomplete", params={"q": "ci"})

    assert response.status_code == 200
    body = response.json()
    assert len(body) > 0
    # "Ciprofloxacin" is an INN-prefix match; anything matched only via brand
    # name or mid-string substring must come after it.
    assert body[0]["inn"] == "Ciprofloxacin"


def test_autocomplete_limits_to_ten_results(client: TestClient):
    # "o" is a broad substring hit across the synthetic catalogue's INNs.
    response = client.get("/medications/autocomplete", params={"q": "o"})

    assert response.status_code == 200
    assert len(response.json()) <= 10
