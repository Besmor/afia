"""Medication catalogue autocomplete endpoint.

GET /medications/autocomplete backs the Landing page's search-bar dropdown
(Block F): as the caller types, it returns individual catalogue rows
(INN + form + strength) rather than search results, so the PWA can let the
user pick an exact medication before ever hitting `GET /search`. This is the
"lightweight NLP catalogue-matching" principle from CLAUDE.md applied to
autocomplete rather than free-text search.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.db.session import get_session
from app.models.pharmacy import Medication

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


@router.get("/medications/autocomplete", response_model=list[AutocompleteResult])
def autocomplete(
    q: str = Query("", description="Partial medication name (INN or brand). Empty returns []."),
    session: Session = Depends(get_session),  # noqa: B008 (FastAPI's DI pattern requires this)
) -> list[AutocompleteResult]:
    """Up to `AUTOCOMPLETE_LIMIT` catalogue rows matching `q`.

    Ranking: rows whose INN starts with `q` come first (case-insensitive),
    followed by rows matched only by substring on INN or brand names.
    Duplicates between the two passes are dropped, keeping the higher-ranked
    (prefix) occurrence.
    """
    normalised = q.strip().lower()
    if not normalised:
        return []

    prefix_pattern = f"{normalised}%"
    substring_pattern = f"%{normalised}%"

    prefix_stmt = (
        select(Medication)
        .where(func.lower(Medication.inn).like(prefix_pattern))
        .order_by(Medication.inn, Medication.strength)
    )
    prefix_rows = session.execute(prefix_stmt).scalars().all()

    substring_stmt = (
        select(Medication)
        .where(
            or_(
                func.lower(Medication.inn).like(substring_pattern),
                func.lower(Medication.brand_names).like(substring_pattern),
            )
        )
        .order_by(Medication.inn, Medication.strength)
    )
    substring_rows = session.execute(substring_stmt).scalars().all()

    seen_ids: set[int] = set()
    ordered: list[Medication] = []
    for medication in (*prefix_rows, *substring_rows):
        if medication.id in seen_ids:
            continue
        seen_ids.add(medication.id)
        ordered.append(medication)
        if len(ordered) >= AUTOCOMPLETE_LIMIT:
            break

    return [
        AutocompleteResult(id=m.id, inn=m.inn, form=m.form.value, strength=m.strength)
        for m in ordered
    ]
