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


def test_results_include_opening_hours_fields(client: TestClient):
    """Each result carries the pharmacy's opening-hours fields, needed for
    the OUVERTE/FERMÉE/De garde pills on the Results and Detail screens.
    """
    response = client.get("/search", params={"q": "paracetamol"})

    assert response.status_code == 200
    results = response.json()
    assert len(results) > 0
    for result in results:
        assert {"opens_at", "closes_at", "open_on_sunday"} <= result.keys()
        assert isinstance(result["opens_at"], str)
        assert isinstance(result["closes_at"], str)
        assert isinstance(result["open_on_sunday"], bool)


def test_ranking_favours_kaloum_pharmacies_near_kaloum_centroid(client: TestClient):
    """A search from the Kaloum centroid should surface Kaloum pharmacies first.

    Kaloum stock for paracetamol sits within ~1.4 km of the centroid, while
    the rest of the synthetic ecosystem's matches sit 4.9 km+ away, so the
    0.6-weighted distance factor should dominate the top of the ranking.
    Ranking design in `docs/decisions/ADR-006-ranking-weights.md`.
    """
    response = client.get(
        "/search",
        params={
            "q": "paracetamol",
            "user_lat": search.DEFAULT_USER_LAT,
            "user_lon": search.DEFAULT_USER_LON,
            "limit": 3,
        },
    )

    assert response.status_code == 200
    results = response.json()
    assert len(results) == 3
    assert all(result["district"] == "Kaloum" for result in results)
