"""Medication catalogue autocomplete endpoint.

GET /medications/autocomplete backs the Landing page's search-bar dropdown
(Block F): as the caller types, it returns individual catalogue rows
(INN + form + strength) rather than search results, so the PWA can let the
user pick an exact medication before ever hitting `GET /search`. This is the
"lightweight NLP catalogue-matching" principle applied to autocomplete
rather than free-text search.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_session
from app.models.pharmacy import Medication
from app.services.text import fold_accents

router = APIRouter(tags=["medications"])

AUTOCOMPLETE_LIMIT = 10


class AutocompleteResult(BaseModel):
    """One catalogue row, distinct from a `SearchResult` in `app.api.search`.

    No pharmacy/stock data here: this is a catalogue lookup, used before the
    user has committed to a medication+dose to search for.
    """
    id: int
    inn: str
    form: str
    strength: str
    matched_brand: str | None = None


def _matched_brand(medication: Medication, normalised: str) -> str | None:
    """The specific brand name that matched `normalised`, or `None`.

    Case-preserving (returns the brand as spelled in the catalogue) so the
    dropdown can show the user why an INN-unrelated row surfaced, e.g. typing
    "lu" surfaces Metformin via its brand "Glucophage". Only called once the
    INN itself has already been ruled out as the match source, per
    `_rank_medications`.
    """
    for brand in (medication.brand_names or "").split(","):
        brand = brand.strip()
        if brand and normalised in fold_accents(brand):
            return brand
    return None


def _rank_medications(medications: list[Medication], normalised: str) -> list[Medication]:
    """Sort `medications` into 3 tiers: INN prefix, INN substring, brand substring.

    INN matches always outrank brand matches, at any tier, so a row is never
    shown above a more directly relevant INN hit just because it happened to
    match earlier alphabetically. Within a tier, rows keep their incoming
    (INN, strength) order.
    """
    tier1: list[Medication] = []
    tier2: list[Medication] = []
    tier3: list[Medication] = []
    for medication in medications:
        inn_folded = fold_accents(medication.inn)
        if inn_folded.startswith(normalised):
            tier1.append(medication)
        elif normalised in inn_folded:
            tier2.append(medication)
        else:
            tier3.append(medication)
    return [*tier1, *tier2, *tier3]


@router.get("/medications/autocomplete", response_model=list[AutocompleteResult])
def autocomplete(
    q: str = Query("", description="Partial medication name (INN or brand). Empty returns []."),
    session: Session = Depends(get_session),  # noqa: B008 (FastAPI's DI pattern requires this)
) -> list[AutocompleteResult]:
    """Up to `AUTOCOMPLETE_LIMIT` catalogue rows matching `q`.

    Ranking (see `_rank_medications`): INN prefix matches first, then INN
    substring matches, then brand substring matches. Accent-folded and
    case-insensitive on both sides, matching the SMS catalogue-matching
    behaviour in `app.services.sms_mock`. A row matched only via a brand
    name carries that brand in `matched_brand`, so the dropdown can show the
    user why it surfaced (per DITL Reviewer 1: patients search by brand,
    e.g. "Glucophage" for Metformin).
    """
    normalised = fold_accents(q.strip())
    if not normalised:
        return []

    all_medications = session.execute(
        select(Medication).order_by(Medication.inn, Medication.strength)
    ).scalars().all()

    matched = [
        m
        for m in all_medications
        if normalised in fold_accents(m.inn) or _matched_brand(m, normalised) is not None
    ]
    ranked = _rank_medications(matched, normalised)[:AUTOCOMPLETE_LIMIT]

    results: list[AutocompleteResult] = []
    for m in ranked:
        matched_via_inn = normalised in fold_accents(m.inn)
        brand = None if matched_via_inn else _matched_brand(m, normalised)
        results.append(
            AutocompleteResult(
                id=m.id, inn=m.inn, form=m.form.value, strength=m.strength, matched_brand=brand
            )
        )
    return results
