"""Tests for the SMS mock service (`app.services.sms_mock`).

Seeds a temporary in-memory SQLite database from the committed
`data/synthetic/` fixtures (same fixture pattern as test_search.py) and
exercises `respond` (and `parse_dose` directly for the regex-only cases)
without going through the HTTP layer.

Design in `docs/decisions/ADR-005-synthetic-ecosystem-data-model.md`. Dose
parsing and the three-branch reply policy are Block F (see
`docs/decisions/` for any related ADR, and the Block F task brief for the
exact wording of each branch).
"""
from __future__ import annotations

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.data.seed_db import SYNTHETIC_DIR, seed_all
from app.models.pharmacy import Base
from app.services.sms_mock import (
    FALLBACK_MESSAGE,
    SMS_MAX_CHARS,
    SYMPTOM_MESSAGE,
    parse_dose,
    respond,
)


@pytest.fixture()
def session():
    """A fresh, seeded, in-memory SQLite session."""
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        seed_all(session, SYNTHETIC_DIR)
        session.commit()
        yield session


def test_medication_and_dose_query_returns_formatted_pharmacy_response(session: Session):
    """A query with a matching dose token gets the existing top-3 pharmacy list."""
    message = respond(session, "Where can I find paracetamol 500mg?")

    assert message.startswith("Afia — 3 pharmacies pour Paracetamol:")
    assert "Stock:" in message
    assert "Prix:" in message
    assert "km" in message


def test_brand_name_and_dose_query_matches_via_brand_names(session: Session):
    message = respond(session, "Do you have doliprane 500mg?")

    assert message.startswith("Afia — 3 pharmacies pour Paracetamol:")


def test_no_medication_match_returns_french_fallback(session: Session):
    """Unrecognised text falls back to the French unknown-medication reply."""
    message = respond(session, "hello there")

    assert message == FALLBACK_MESSAGE


def test_typo_medication_returns_french_fallback(session: Session):
    """DITL Reviewer 1 bug: a typo'd medication name ("amoxicilin") no longer replies in English."""
    message = respond(session, "amoxicilin 500mg")

    assert message == FALLBACK_MESSAGE
    assert "médicament" in message


def test_unknown_brand_returns_french_fallback(session: Session):
    """DITL Reviewer 1 bug: a brand outside the catalogue ("mixtard") no longer replies in English."""
    message = respond(session, "mixtard")

    assert message == FALLBACK_MESSAGE


def test_symptom_query_with_accents_returns_safety_reply(session: Session):
    message = respond(session, "j'ai mal à la tête")

    assert message == SYMPTOM_MESSAGE


def test_symptom_query_unaccented_returns_safety_reply(session: Session):
    """Same safety reply when accents/apostrophes are dropped, as SMS input often is."""
    message = respond(session, "jai mal tete")

    assert message == SYMPTOM_MESSAGE


def test_medication_query_does_not_trigger_symptom_branch(session: Session):
    """Regression: a plain medication name must not be mistaken for a symptom query."""
    message = respond(session, "paracétamol")

    assert message != SYMPTOM_MESSAGE
    assert message.startswith("Paracetamol:")


def test_response_stays_under_sms_length_limit(session: Session):
    message = respond(session, "Where can I find paracetamol 500mg?")

    assert len(message) < SMS_MAX_CHARS


def test_dose_regex_extracts_bare_mg(session: Session):
    stripped, dose = parse_dose("paracetamol 500mg")

    assert dose == (500.0, "mg")
    assert "500" not in stripped
    assert "paracetamol" in stripped


def test_dose_regex_extracts_decimal_grams_as_mg(session: Session):
    _, dose = parse_dose("amoxicillin 0.5g")

    assert dose == (500.0, "mg")


def test_dose_regex_is_case_insensitive_and_ignores_whitespace(session: Session):
    _, dose = parse_dose("paracetamol 500 MG")

    assert dose == (500.0, "mg")


def test_no_dose_token_asks_for_dose_in_french(session: Session):
    """No dose given: French ask-back listing the doses that exist for that INN."""
    message = respond(session, "paracetamol")

    assert message.startswith("Paracetamol:")
    assert "500mg" in message
    assert "Répondez avec la dose" in message


def test_dose_with_no_matching_strength_lists_available_doses_in_french(session: Session):
    """Dose given but no catalogue row has it: French no-match reply with available doses."""
    message = respond(session, "paracetamol 250mg")

    assert message.startswith("Aucune pharmacie pour Paracetamol 250mg.")
    assert "Doses disponibles:" in message
    assert "500mg" in message
