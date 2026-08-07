"""Medication search endpoint.

GET /search returns unranked pharmacy/stock matches for a free-text medication
query. Walking-distance ranking is Block 3 (see CLAUDE.md build order) and is
deliberately not implemented here.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, sessionmaker

from app.data.seed_db import DEFAULT_DB_PATH, build_engine
from app.models.pharmacy import Medication, Pharmacy, StockItem

router = APIRouter(tags=["search"])

# Kaloum commune centroid: default origin when the caller supplies no location.
DEFAULT_USER_LAT = 9.515
DEFAULT_USER_LON = -13.705

_engine = build_engine(DEFAULT_DB_PATH)
_SessionLocal = sessionmaker(bind=_engine)


def get_session():
    """Yield a database session for the request, closed once the request ends.

    Overridden in tests to point at a hermetic in-memory database.
    """
    session = _SessionLocal()
    try:
        yield session
    finally:
        session.close()


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


@router.get("/search", response_model=list[SearchResult])
def search(
    q: str = Query(..., min_length=1, description="Medication name query (INN or brand name)."),
    user_lat: float = Query(DEFAULT_USER_LAT, description="Caller latitude; defaults to the Kaloum centroid."),
    user_lon: float = Query(DEFAULT_USER_LON, description="Caller longitude; defaults to the Kaloum centroid."),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of results returned."),
    session: Session = Depends(get_session),  # noqa: B008 (FastAPI's DI pattern requires this)
) -> list[SearchResult]:
    """Unranked medication search.

    Matches `q` case-insensitively as a substring of either the medication's
    INN or its brand names, then joins to stock held in quantity > 0.
    `user_lat`/`user_lon` are accepted for the ranking step introduced in
    Block 3 and are not yet used to order results.
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
        .limit(limit)
    )

    rows = session.execute(stmt).all()

    return [
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
        )
        for pharmacy, medication, stock_item in rows
    ]
