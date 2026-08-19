"""SMS mock service.

Simulates the SMS gateway channel described in README.md: a
raw inbound text arrives, gets matched against the medication catalogue,
and a plain-text reply is composed from the same ranked search + ranking
logic that backs `GET /search`. No real SMS provider is involved; this is a
local mock only (ethics/scope constraint). `scripts/sms_mock.py` is the CLI
entry point.
"""
from __future__ import annotations

import logging
import re
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.search import SearchResult, search_by_medication, search_medications
from app.models.pharmacy import District, Medication, MedicationForm
from app.services.ranking import walking_distance_m
from app.services.text import fold_accents

# backend/app/services/sms_mock.py -> parents[3] == repo root
REPO_ROOT = Path(__file__).resolve().parents[3]
LOG_DIR = REPO_ROOT / "logs"
LOG_PATH = LOG_DIR / "sms_mock.log"

# Conakry city centroid: default origin for an SMS query, which arrives with
# no device location attached (unlike a PWA request). Used when no district
# name is found in the query text (see `_parse_district`).
SMS_DEFAULT_LAT = 9.54
SMS_DEFAULT_LON = -13.68

# District centroids: midpoints of the bounding boxes in
# `backend/app/data/conakry_district_bounds.json`, precomputed the same way
# the frontend's `DISTRICT_BOUNDS`/`centroidOf` (`src/constants/districts.ts`)
# already does, so a district named in the SMS text narrows the search origin
# from the Conakry-wide default to that commune. "Unknown" is the backend's
# non-user-facing catch-all district and is deliberately not offered here,
# matching the frontend's district picker.
DISTRICT_CENTROIDS: dict[District, tuple[float, float]] = {
    District.KALOUM: (9.515, -13.705),
    District.DIXINN: (9.545, -13.680),
    District.RATOMA: (9.610, -13.615),
    District.MATAM: (9.540, -13.660),
    District.MATOTO: (9.580, -13.575),
}

# Matches any district name, case-insensitive and accent-folded (input is
# folded via `fold_accents` before this runs, so the pattern itself only
# needs the plain lower-case spellings). Word-boundaried so e.g. a longer
# place name sharing a prefix can't false-positive.
_DISTRICT_PATTERN = re.compile(
    r"\b(" + "|".join(fold_accents(district.value) for district in DISTRICT_CENTROIDS) + r")\b"
)
_DISTRICT_BY_FOLDED_NAME: dict[str, District] = {
    fold_accents(district.value): district for district in DISTRICT_CENTROIDS
}

SMS_RESULT_LIMIT = 3
SMS_MAX_CHARS = 500

# The two French ask-back/no-match branches are short by construction (one
# INN plus a handful of doses), but this caps them the same way SMS_MAX_CHARS
# caps the pharmacy-list branch, per the Block F brief (<= 320 chars total).
SMS_ASK_BACK_MAX_CHARS = 320

# Unknown-medication fallback: no INN or brand name matched at all (covers
# typos, e.g. "amoxicilin", and brands outside the catalogue, e.g.
# "mixtard"). French per DITL Reviewer 1 (P0): Doctor 1 saw the old English
# string on exactly these two cases.
FALLBACK_MESSAGE = (
    "Afia n'a pas reconnu ce médicament. Vérifiez l'orthographe ou "
    "envoyez le nom exact (ex: paracétamol). Afia ne remplace pas votre "
    "pharmacien."
)

# Symptom-query safety reply: shown instead of FALLBACK_MESSAGE when the text
# looks like a symptom description rather than an unrecognised medication
# name (see SYMPTOM_PATTERN). Ethics-critical per DITL Reviewer 1 (P0):
# Doctor 1 flagged that suggesting a medication for a symptom risks steering
# a user towards something contraindicated (e.g. pregnancy) or masking an
# underlying condition (e.g. hypertension headaches), so Afia must defer to
# a clinician rather than guess.
SYMPTOM_MESSAGE = (
    "Afia ne propose pas de médicament pour un symptôme. Consultez votre "
    "médecin ou pharmacien. Envoyez ensuite le nom du médicament prescrit "
    "pour vérifier les stocks."
)

# French symptom keywords (case-insensitive, word boundary), per the Block G
# fix brief. Both accented and unaccented spellings are listed since SMS
# input arrives without reliable accents (e.g. "jai mal tete").
SYMPTOM_KEYWORDS = (
    "mal", "douleur", "fièvre", "fievre", "tousse", "toux", "saigne",
    "saignement", "vomi", "vomissement", "nausée", "nausee", "diarrhée",
    "diarrhee", "brûlure", "brulure", "gorge", "ventre", "tête", "tete",
    "dos", "jambe", "oreille",
)
SYMPTOM_PATTERN = re.compile(
    r"\b(?:" + "|".join(re.escape(keyword) for keyword in SYMPTOM_KEYWORDS) + r")\b",
    re.IGNORECASE,
)

# Matches a dose token anywhere in the SMS text, e.g. "500mg", "0.5g",
# "500 MG", "120mcg", "100ui". Comma decimals ("0,5g") are also accepted
# since that is the standard decimal separator in French.
DOSE_PATTERN = re.compile(r"(\d+(?:[.,]\d+)?)\s*(mg|g|mcg|µg|ml|ui|iu)", re.IGNORECASE)

# French label prefixed onto a dose display when the form isn't a plain
# solid-oral dose (tablet/capsule read fine as a bare "500mg"; a syrup or
# drops dose needs its form spelled out to stay unambiguous, e.g. "sirop
# 120mg/5ml"). Judgement call: no such distinction is specified in the task
# brief's illustrative example, which only shows tablet-only doses.
_FORM_LABELS_FR: dict[MedicationForm, str] = {
    MedicationForm.SYRUP: "sirop",
    MedicationForm.INJECTION: "injection",
    MedicationForm.OINTMENT: "pommade",
    MedicationForm.DROPS: "gouttes",
    MedicationForm.SUPPOSITORY: "suppositoire",
    MedicationForm.SACHET: "sachet",
}

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


def _normalise_dose_token(value_str: str, unit: str) -> tuple[float, str]:
    """Normalise a raw (value, unit) regex match to a canonical (value, unit) pair.

    `g` is converted to `mg` (x1000) so a tablet strength recorded in either
    unit still compares equal; `mcg`/`µg` collapse to one spelling; `ui`/`iu`
    collapse to one spelling; comma decimals become dots.
    """
    value = float(value_str.replace(",", "."))
    unit_lower = unit.lower()
    if unit_lower == "g":
        value *= 1000
        unit_lower = "mg"
    elif unit_lower in ("mcg", "µg"):
        unit_lower = "mcg"
    elif unit_lower in ("ui", "iu"):
        unit_lower = "iu"
    return value, unit_lower


def _format_dose(value: float, unit: str) -> str:
    """Render a normalised (value, unit) pair compactly, e.g. (500.0, "mg") -> "500mg"."""
    value_str = str(int(value)) if value == int(value) else str(value).rstrip("0").rstrip(".")
    return f"{value_str}{unit}"


def parse_dose(text: str) -> tuple[str, tuple[float, str] | None]:
    """Extract a dose token from `text`.

    Returns `(text_with_token_removed, normalised_dose)`, or
    `(text, None)` if no dose token is present. The token is stripped before
    catalogue-matching so its digits/unit cannot interfere with INN matching.
    """
    match = DOSE_PATTERN.search(text)
    if match is None:
        return text, None

    dose = _normalise_dose_token(*match.groups())
    stripped = (text[: match.start()] + text[match.end() :]).strip()
    return stripped, dose


def _parse_district(text: str) -> tuple[str, District | None]:
    """Extract a Conakry district name from `text`.

    Returns `(text_with_district_removed, matched_district)`, or
    `(text, None)` if no district name is present. Matching is
    case-insensitive and accent-folded (`fold_accents`), so "Kaloum",
    "RATOMA", and "à Dixinn" all match; the district token is stripped
    before catalogue-matching, mirroring `parse_dose`. Folding never
    changes a French string's character count (verified for the accented
    Latin letters SMS text actually uses), so a match span found in the
    folded text lines up with the same span in `text`.
    """
    folded = fold_accents(text)
    match = _DISTRICT_PATTERN.search(folded)
    if match is None:
        return text, None

    district = _DISTRICT_BY_FOLDED_NAME[match.group(1)]
    stripped = (text[: match.start()] + text[match.end() :]).strip()
    return stripped, district


def _dose_from_strength(strength: str) -> tuple[float, str] | None:
    """Extract a comparable (value, unit) dose from a catalogue `Medication.strength` string.

    Uses the same `DOSE_PATTERN`/normalisation as `parse_dose`, so a user
    dose token and a catalogue strength are compared on equal footing (e.g.
    an SMS "1000mg" matches a catalogue "1 g"). Only the first number+unit in
    the strength string is used, so compound strengths like "20/120 mg" or
    plain percentages like "1%" (no matched unit) are matched loosely on
    that basis rather than exactly.
    """
    match = DOSE_PATTERN.search(strength)
    if match is None:
        return None
    return _normalise_dose_token(*match.groups())


def _display_dose(medication: Medication) -> str:
    """Compact display token for one catalogue row's strength, e.g. "500mg" or "sirop 120mg/5ml"."""
    compact = medication.strength.replace(" ", "")
    label = _FORM_LABELS_FR.get(medication.form)
    return f"{label} {compact}" if label else compact


def _medications_for_inn(session: Session, inn: str) -> list[Medication]:
    """All catalogue rows sharing `inn` exactly, ordered by id (the dose siblings of a match)."""
    stmt = select(Medication).where(Medication.inn == inn).order_by(Medication.id)
    return list(session.execute(stmt).scalars().all())


def match_medication(session: Session, text: str) -> Medication | None:
    """Find the medication whose INN or a brand name is a case-insensitive substring of `text`.

    Catalogue matching only, per the project's "NLP parser is intentionally
    light" principle: no tokenisation or fuzzy matching. Candidate names are
    checked longest-first so a short brand name can't pre-empt a longer, more
    specific match earlier in table order. Accents are folded on both sides
    (e.g. "paracétamol" matches catalogue "Paracetamol") since SMS input is
    French and accents are typed inconsistently on feature phones.
    """
    normalised = fold_accents(text)

    candidates: list[tuple[str, Medication]] = []
    for medication in session.execute(select(Medication)).scalars():
        candidates.append((fold_accents(medication.inn), medication))
        for brand in (medication.brand_names or "").split(","):
            brand = brand.strip()
            if brand:
                candidates.append((fold_accents(brand), medication))

    candidates.sort(key=lambda pair: len(pair[0]), reverse=True)
    for name, medication in candidates:
        if name in normalised:
            return medication
    return None


def format_response(
    medication_name: str,
    results: list[SearchResult],
    origin_lat: float = SMS_DEFAULT_LAT,
    origin_lon: float = SMS_DEFAULT_LON,
) -> str:
    """Format ranked search results as a plain-text SMS reply (French, user-facing).

    `origin_lat`/`origin_lon` is the point the displayed walking distance is
    measured from; defaults to the Conakry centroid, but `respond` passes a
    district centroid when `_parse_district` matched one, so the displayed
    distance stays consistent with the ranking origin used for `results`.
    """
    if not results:
        return f"Afia: aucune pharmacie n'a actuellement {medication_name} en stock."

    lines = [f"Afia - {len(results)} pharmacies pour {medication_name}:"]
    for result in results:
        distance_km = (
            walking_distance_m(origin_lat, origin_lon, result.latitude, result.longitude) / 1000
        )
        lines.append(f"{result.pharmacy_name} ({result.district})")
        lines.append(
            f"  Stock: {result.quantity} | Prix: {result.price_gnf} GNF | ~{distance_km:.1f} km"
        )
    return "\n".join(lines)


def _ask_for_dose_message(session: Session, medication: Medication) -> str:
    """French ask-back reply when an INN matched but no dose token was given."""
    siblings = _medications_for_inn(session, medication.inn)
    doses = ", ".join(_display_dose(m) for m in siblings)
    return f"{medication.inn}: {doses}. Répondez avec la dose pour voir les pharmacies."


def _no_match_for_dose_message(
    medication: Medication, dose: tuple[float, str], siblings: list[Medication]
) -> str:
    """French reply when a dose token was given but no catalogue row has that strength."""
    dose_display = _format_dose(*dose)
    doses = ", ".join(_display_dose(m) for m in siblings)
    return f"Aucune pharmacie pour {medication.inn} {dose_display}. Doses disponibles: {doses}."


def respond(session: Session, text: str) -> str:
    """Build the SMS reply for an inbound `text` query, logging the exchange.

    Matches `text` against the medication catalogue (after stripping any dose
    token, see `parse_dose`), then branches:

    - No INN matched, but the text looks like a symptom description (see
      `SYMPTOM_PATTERN`): `SYMPTOM_MESSAGE`. Checked before the generic
      fallback so a described symptom is never treated as a typo'd
      medication name (ethics-critical, see DITL Reviewer 1 P0).
    - No INN matched at all, and no symptom keyword either: `FALLBACK_MESSAGE`.
    - INN matched, no dose token: French ask-back listing the doses that
      exist for that INN.
    - INN matched, dose token given but it matches no catalogue row for that
      INN: French "no pharmacies" reply, also listing the doses that exist.
    - INN matched, dose token matches a catalogue row: the existing top-3
      pharmacy list (`format_response`), filtered to that exact INN+strength
      via `search_by_medication` rather than the free-text `search_medications`.

    A medication match always wins over a symptom-looking query (priority
    order: medication, then symptom, then generic unknown fallback), so e.g.
    "paracetamol" alone still asks for a dose rather than tripping the
    symptom branch just because "mal" also matches nothing here.

    A district name anywhere in `text` (see `_parse_district`) narrows the
    ranking origin from the Conakry-wide centroid to that district's
    centroid, e.g. "paracetamol 500mg kaloum" ranks against Kaloum rather
    than the city centre. No district name found falls back to the previous
    Conakry-wide default, so this is backwards-compatible.
    """
    logger = _get_logger()
    logger.info("REQUEST: %s", text)

    stripped_text, dose = parse_dose(text)
    stripped_text, district = _parse_district(stripped_text)
    origin_lat, origin_lon = DISTRICT_CENTROIDS.get(district, (SMS_DEFAULT_LAT, SMS_DEFAULT_LON))
    medication = match_medication(session, stripped_text)
    if medication is None:
        if SYMPTOM_PATTERN.search(text):
            logger.info("RESPONSE: %s", SYMPTOM_MESSAGE)
            return SYMPTOM_MESSAGE
        logger.info("RESPONSE: %s", FALLBACK_MESSAGE)
        return FALLBACK_MESSAGE

    if dose is None:
        message = _ask_for_dose_message(session, medication)
        _log_french_branch_length(logger, text, message)
        logger.info("RESPONSE: %s", message)
        return message

    siblings = _medications_for_inn(session, medication.inn)
    matched_row = next(
        (m for m in siblings if _dose_from_strength(m.strength) == dose), None
    )

    if matched_row is None:
        message = _no_match_for_dose_message(medication, dose, siblings)
        _log_french_branch_length(logger, text, message)
        logger.info("RESPONSE: %s", message)
        return message

    results = search_by_medication(
        session,
        medication_id=matched_row.id,
        strength=matched_row.strength,
        user_lat=origin_lat,
        user_lon=origin_lon,
        limit=SMS_RESULT_LIMIT,
    )
    message = format_response(medication.inn, results, origin_lat, origin_lon)

    if len(message) > SMS_MAX_CHARS:
        logger.warning(
            "Response for %r is %d chars, over the %d-char SMS-friendly limit",
            text,
            len(message),
            SMS_MAX_CHARS,
        )

    logger.info("RESPONSE: %s", message.replace("\n", " | "))
    return message


def _log_french_branch_length(logger: logging.Logger, text: str, message: str) -> None:
    """Warn if an ask-back/no-match reply exceeds the 320-char budget those branches target."""
    if len(message) > SMS_ASK_BACK_MAX_CHARS:
        logger.warning(
            "Response for %r is %d chars, over the %d-char ask-back budget",
            text,
            len(message),
            SMS_ASK_BACK_MAX_CHARS,
        )
