"""SMS mock service.

Simulates the SMS gateway channel described in CLAUDE.md and README.md: a
raw inbound text arrives, gets matched against the medication catalogue,
and a plain-text reply is composed from the same ranked search + ranking
logic that backs `GET /search`. No real SMS provider is involved; this is a
local mock only (ethics/scope constraint). `scripts/sms_mock.py` is the CLI
entry point.
"""
from __future__ import annotations

import logging
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.search import SearchResult, search_medications
from app.models.pharmacy import Medication
from app.services.ranking import walking_distance_m

# backend/app/services/sms_mock.py -> parents[3] == repo root
REPO_ROOT = Path(__file__).resolve().parents[3]
LOG_DIR = REPO_ROOT / "logs"
LOG_PATH = LOG_DIR / "sms_mock.log"

# Conakry city centroid: default origin for an SMS query, which arrives with
# no device location attached (unlike a PWA request).
SMS_DEFAULT_LAT = 9.54
SMS_DEFAULT_LON = -13.68

SMS_RESULT_LIMIT = 3
SMS_MAX_CHARS = 500

FALLBACK_MESSAGE = (
    "Afia: type a medication name (e.g. 'paracetamol') to find nearby "
    "pharmacies with stock."
)

_logger = logging.getLogger("afia.sms_mock")


def _get_logger() -> logging.Logger:
    """Return the SMS mock's logger, attaching its file handler on first use.

    Lazy so importing this module has no side effects on disk (mirrors the
    TD-001 fix in `app.db.session`); `logs/` is created the first time a
    request is actually logged.
    """
    if not _logger.handlers:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        handler = logging.FileHandler(LOG_PATH, encoding="utf-8")
        handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
        _logger.addHandler(handler)
        _logger.setLevel(logging.INFO)
    return _logger


def match_medication(session: Session, text: str) -> Medication | None:
    """Find the medication whose INN or a brand name is a case-insensitive substring of `text`.

    Catalogue matching only, per CLAUDE.md's "NLP parser is intentionally
    light" principle: no tokenisation or fuzzy matching. Candidate names are
    checked longest-first so a short brand name can't pre-empt a longer, more
    specific match earlier in table order.
    """
    normalised = text.lower()

    candidates: list[tuple[str, Medication]] = []
    for medication in session.execute(select(Medication)).scalars():
        candidates.append((medication.inn.lower(), medication))
        for brand in (medication.brand_names or "").split(","):
            brand = brand.strip().lower()
            if brand:
                candidates.append((brand, medication))

    candidates.sort(key=lambda pair: len(pair[0]), reverse=True)
    for name, medication in candidates:
        if name in normalised:
            return medication
    return None


def format_response(medication_name: str, results: list[SearchResult]) -> str:
    """Format ranked search results as a plain-text SMS reply."""
    if not results:
        return f"Afia: no pharmacies currently have {medication_name} in stock."

    lines = [f"Afia — {len(results)} pharmacies for {medication_name}:"]
    for result in results:
        distance_km = (
            walking_distance_m(
                SMS_DEFAULT_LAT, SMS_DEFAULT_LON, result.latitude, result.longitude
            )
            / 1000
        )
        lines.append(f"{result.pharmacy_name} ({result.district})")
        lines.append(
            f"  Stock: {result.quantity} | Price: {result.price_gnf} GNF | ~{distance_km:.1f} km"
        )
    return "\n".join(lines)


def respond(session: Session, text: str) -> str:
    """Build the SMS reply for an inbound `text` query, logging the exchange.

    Matches `text` against the medication catalogue, then reuses
    `search_medications` (the DB-level function behind `GET /search`) with
    the Conakry-centroid default origin and a 3-result limit. Falls back to
    a help message when no medication is matched.
    """
    logger = _get_logger()
    logger.info("REQUEST: %s", text)

    medication = match_medication(session, text)
    if medication is None:
        logger.info("RESPONSE: %s", FALLBACK_MESSAGE)
        return FALLBACK_MESSAGE

    results = search_medications(
        session,
        q=medication.inn,
        user_lat=SMS_DEFAULT_LAT,
        user_lon=SMS_DEFAULT_LON,
        limit=SMS_RESULT_LIMIT,
    )
    message = format_response(medication.inn, results)

    if len(message) > SMS_MAX_CHARS:
        logger.warning(
            "Response for %r is %d chars, over the %d-char SMS-friendly limit",
            text,
            len(message),
            SMS_MAX_CHARS,
        )

    logger.info("RESPONSE: %s", message.replace("\n", " | "))
    return message
