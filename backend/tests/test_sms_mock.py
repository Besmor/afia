"""Tests for the SMS mock service (`app.services.sms_mock`).

Seeds a temporary in-memory SQLite database from the committed
`data/synthetic/` fixtures (same fixture pattern as test_search.py) and
exercises `respond` directly, without going through the HTTP layer.

Design in `docs/decisions/ADR-005-synthetic-ecosystem-data-model.md`.
"""
from __future__ import annotations

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.data.seed_db import SYNTHETIC_DIR, seed_all
from app.models.pharmacy import Base
from app.services.sms_mock import FALLBACK_MESSAGE, SMS_MAX_CHARS, respond


@pytest.fixture()
def session():
    """A fresh, seeded, in-memory SQLite session."""
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        seed_all(session, SYNTHETIC_DIR)
        session.commit()
        yield session


def test_medication_query_returns_formatted_pharmacy_response(session: Session):
    message = respond(session, "Where can I find paracetamol?")

    assert message.startswith("Afia — 3 pharmacies for Paracetamol:")
    assert "Stock:" in message
    assert "Price:" in message
    assert "km" in message


def test_brand_name_query_matches_via_brand_names(session: Session):
    message = respond(session, "Do you have doliprane?")

    assert message.startswith("Afia — 3 pharmacies for Paracetamol:")


def test_no_medication_match_returns_fallback(session: Session):
    message = respond(session, "hello there")

    assert message == FALLBACK_MESSAGE


def test_response_stays_under_sms_length_limit(session: Session):
    message = respond(session, "Where can I find paracetamol?")

    assert len(message) < SMS_MAX_CHARS
