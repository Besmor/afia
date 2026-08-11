"""Medication search endpoint.

GET /search returns ranked pharmacy/stock matches for a free-text medication
query, ordered by the combined ranking score from `app.services.ranking`
(walking-realistic distance, stock quantity, digital-maturity tier trust).
Weighting rationale in `docs/decisions/ADR-006-ranking-weights.md`.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.db.session import get_session
from app.models.pharmacy import Medication, Pharmacy, StockItem
from app.services.ranking import rank_results

router = APIRouter(tags=["search"])

# Kaloum commune centroid: default origin when the caller supplies no location.
DEFAULT_USER_LAT = 9.515
DEFAULT_USER_LON = -13.705


class SearchResult(BaseModel):
    """One pharmacy-medication stock match."""
    pharmacy_id: str
    pharmacy_name: str
    district: str
    latitude: float
    longitude: float
    digital_maturity: str
    medication_id: int
    medication_inn: str
    medication_form: str
    medication_strength: str
    quantity: int
    price_gnf: int
    last_verified_at: str
    opens_at: str
    closes_at: str
    open_on_sunday: bool


def search_medications(
    session: Session,
    q: str,
    user_lat: float = DEFAULT_USER_LAT,
    user_lon: float = DEFAULT_USER_LON,
    limit: int = 10,
) -> list[SearchResult]:
    """DB-level ranked medication search.

    Matches `q` case-insensitively as a substring of either the medication's
    INN or its brand names, then joins to stock held in quantity > 0. The
    full match set is scored by `rank_results` (distance from
    `user_lat`/`user_lon`, stock quantity, digital-maturity tier trust)
    before `limit` is applied, so limiting never discards a better-ranked
    result in favour of a worse one.

    This is the shared search implementation: the `GET /search` endpoint
    below and `app.services.sms_mock` both call it directly, rather than the
    SMS mock going through the HTTP endpoint.
    """
    normalised = q.strip().lower()
    pattern = f"%{normalised}%"

    stmt = (
        select(Pharmacy, Medication, StockItem)
        .join(StockItem, StockItem.pharmacy_id == Pharmacy.id)
        .join(Medication, Medication.id == StockItem.medication_id)
        .where(
            or_(
                func.lower(Medication.inn).like(pattern),
                func.lower(Medication.brand_names).like(pattern),
            )
        )
        .where(StockItem.quantity > 0)
        .order_by(Pharmacy.id, Medication.id)
    )

    rows = session.execute(stmt).all()

    results = [
        SearchResult(
            pharmacy_id=pharmacy.id,
            pharmacy_name=pharmacy.name,
            district=pharmacy.district.value,
            latitude=pharmacy.latitude,
            longitude=pharmacy.longitude,
            digital_maturity=pharmacy.digital_maturity.value,
            medication_id=medication.id,
            medication_inn=medication.inn,
            medication_form=medication.form.value,
            medication_strength=medication.strength,
            quantity=stock_item.quantity,
            price_gnf=stock_item.price_gnf,
            last_verified_at=stock_item.last_verified_at.isoformat(),
            opens_at=pharmacy.opens_at.isoformat(),
            closes_at=pharmacy.closes_at.isoformat(),
            open_on_sunday=pharmacy.open_on_sunday,
        )
        for pharmacy, medication, stock_item in rows
    ]

    ranked = rank_results(results, user_lat, user_lon)
    return ranked[:limit]


@router.get("/search", response_model=list[SearchResult])
def search(
    q: str = Query(..., min_length=1, description="Medication name query (INN or brand name)."),
    user_lat: float = Query(DEFAULT_USER_LAT, description="Caller latitude; defaults to the Kaloum centroid."),
    user_lon: float = Query(DEFAULT_USER_LON, description="Caller longitude; defaults to the Kaloum centroid."),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of results returned."),
    session: Session = Depends(get_session),  # noqa: B008 (FastAPI's DI pattern requires this)
) -> list[SearchResult]:
    """Ranked medication search. See `search_medications` for the implementation."""
    return search_medications(session, q, user_lat, user_lon, limit)
