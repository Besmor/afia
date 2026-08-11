"""Standalone pharmacy lookup endpoint.

GET /pharmacies/{pharmacy_id} returns the full pharmacy record for the
Pharmacy Detail screen (FT-8). `GET /search` only ever returns pharmacy
fields alongside a matched stock item, so a page navigated to directly (or
refreshed) needs its own fetch that does not depend on a medication match.
No stock or medication data is included here; that stays on `GET /search`.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.session import get_session
from app.models.pharmacy import Pharmacy

router = APIRouter(tags=["pharmacies"])


class PharmacyDetail(BaseModel):
    """Full pharmacy record, no stock/medication data."""
    id: str
    name: str
    district: str
    latitude: float
    longitude: float
    digital_maturity: str
    phone: str | None
    opens_at: str
    closes_at: str
    open_on_sunday: bool


@router.get("/pharmacies/{pharmacy_id}", response_model=PharmacyDetail)
def get_pharmacy(
    pharmacy_id: str,
    session: Session = Depends(get_session),  # noqa: B008 (FastAPI's DI pattern requires this)
) -> PharmacyDetail:
    """Fetch one pharmacy by id, or 404 if it does not exist."""
    pharmacy = session.get(Pharmacy, pharmacy_id)
    if pharmacy is None:
        raise HTTPException(status_code=404, detail="Pharmacy not found")

    return PharmacyDetail(
        id=pharmacy.id,
        name=pharmacy.name,
        district=pharmacy.district.value,
        latitude=pharmacy.latitude,
        longitude=pharmacy.longitude,
        digital_maturity=pharmacy.digital_maturity.value,
        phone=pharmacy.phone,
        opens_at=pharmacy.opens_at.isoformat(),
        closes_at=pharmacy.closes_at.isoformat(),
        open_on_sunday=pharmacy.open_on_sunday,
    )
