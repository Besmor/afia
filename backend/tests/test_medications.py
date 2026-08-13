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


def test_brand_only_match_surfaces_matched_brand(client: TestClient):
    """"gluco" matches only Metformin's brand "Glucophage", not its INN, so
    the row must carry the matched brand for the dropdown to explain itself.
    """
    response = client.get("/medications/autocomplete", params={"q": "gluco"})

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["inn"] == "Metformin"
    assert body[0]["matched_brand"] == "Glucophage"


def test_inn_prefix_match_has_no_matched_brand(client: TestClient):
    response = client.get("/medications/autocomplete", params={"q": "ci"})

    assert response.status_code == 200
    body = response.json()
    assert body[0]["inn"] == "Ciprofloxacin"
    assert body[0]["matched_brand"] is None


def test_inn_substring_match_has_no_matched_brand(client: TestClient):
    # "soluble" (part of "Insulin (soluble, human)") is a mid-string INN
    # match, not a prefix and not a brand match.
    response = client.get("/medications/autocomplete", params={"q": "soluble"})

    assert response.status_code == 200
    body = response.json()
    assert len(body) > 0
    row = next(r for r in body if r["inn"] == "Insulin (soluble, human)")
    assert row["matched_brand"] is None


def test_inn_substring_ranks_before_brand_substring(client: TestClient):
    """"lu" is an INN-substring match on "Artemether + Lumefantrine" (and
    "Insulin (soluble, human)") and a brand-substring match on Metformin
    (via "Glucophage"). INN matches must rank first regardless of tier.
    """
    response = client.get("/medications/autocomplete", params={"q": "lu"})

    assert response.status_code == 200
    body = response.json()
    inns = [row["inn"] for row in body]
    assert "Metformin" in inns
    assert "Artemether + Lumefantrine" in inns

    metformin_rank = inns.index("Metformin")
    inn_match_rank = inns.index("Artemether + Lumefantrine")
    assert inn_match_rank < metformin_rank

    metformin_row = next(r for r in body if r["inn"] == "Metformin")
    assert metformin_row["matched_brand"] == "Glucophage"
