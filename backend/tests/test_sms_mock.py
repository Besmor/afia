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
from app.models.pharmacy import Base, District
from app.services.sms_mock import (
    FALLBACK_MESSAGE,
    SMS_MAX_CHARS,
    SYMPTOM_MESSAGE,
    _parse_district,
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
    """A brand outside the catalogue triggers the French fallback rather than an English default.

    DITL Reviewer 1 originally spotted this bug with 'mixtard' (which is now in the seed).
    Uses 'zoloft' (a real antidepressant brand deliberately not carried by the Afia catalogue,
    which is scoped to WHO EML essentials) to keep the assertion meaningful.
    """
    message = respond(session, "zoloft")

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


def test_district_parsing_matches_lowercase_name():
    stripped, district = _parse_district("paracetamol 500mg kaloum")

    assert district is District.KALOUM
    assert "kaloum" not in stripped.lower()


def test_district_parsing_is_case_insensitive():
    _, district = _parse_district("paracetamol 500mg RATOMA")

    assert district is District.RATOMA


def test_district_parsing_handles_preposition():
    _, district = _parse_district("paracetamol 500mg à Dixinn")

    assert district is District.DIXINN


def test_district_parsing_folds_accents_in_the_rest_of_the_query():
    """The district name itself is unaccented; this checks accented text
    elsewhere in the query does not stop the district match from being found."""
    _, district = _parse_district("paracétamol 500mg matam")

    assert district is District.MATAM


def test_district_parsing_falls_back_to_none_with_no_district(session: Session):
    stripped, district = _parse_district("paracetamol 500mg")

    assert district is None
    assert stripped == "paracetamol 500mg"


def test_district_parsing_falls_back_to_none_for_unknown_place_name():
    _, district = _parse_district("paracetamol 500mg unknowntown")

    assert district is None


def test_sms_query_with_district_ranks_that_districts_pharmacy_first(session: Session):
    """A district name in the SMS text changes the ranking origin (compare
    against the plain-query default below), matching what a PWA user with
    device geolocation already gets."""
    message = respond(session, "paracetamol 500mg kaloum")

    first_pharmacy_line = message.split("\n")[1]
    assert "(Kaloum)" in first_pharmacy_line


def test_sms_query_without_district_uses_conakry_wide_default(session: Session):
    """Backwards-compatible: no district word in the text keeps ranking
    against the Conakry-wide centroid, as before this change."""
    message = respond(session, "paracetamol 500mg")

    first_pharmacy_line = message.split("\n")[1]
    assert "(Kaloum)" not in first_pharmacy_line
