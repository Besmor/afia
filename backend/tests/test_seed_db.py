"""Tests for the synthetic ecosystem seed script.

Seeds a temporary in-memory SQLite database from the committed
`data/synthetic/` fixtures and checks the resulting row counts and
digital-maturity distribution against ADR-005.

Design in `docs/decisions/ADR-005-synthetic-ecosystem-data-model.md`.
"""
from __future__ import annotations

import pytest
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session

from app.data.seed_db import SYNTHETIC_DIR, seed_all
from app.models.pharmacy import Base, DigitalMaturity, Medication, Pharmacy, StockItem


@pytest.fixture()
def session():
    """A fresh in-memory SQLite session, tables created but not yet seeded."""
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


def _count(session: Session, model) -> int:
    return session.scalar(select(func.count()).select_from(model))


def test_seed_all_inserts_expected_row_counts(session: Session):
    seed_all(session, SYNTHETIC_DIR)
    session.commit()

    assert _count(session, Pharmacy) == 15
    assert _count(session, Medication) == 25
    assert _count(session, StockItem) == 225


def test_seed_all_is_idempotent(session: Session):
    seed_all(session, SYNTHETIC_DIR)
    session.commit()
    seed_all(session, SYNTHETIC_DIR)
    session.commit()

    assert _count(session, Pharmacy) == 15
    assert _count(session, Medication) == 25
    assert _count(session, StockItem) == 225


def test_digital_maturity_distribution_includes_extremes(session: Session):
    seed_all(session, SYNTHETIC_DIR)
    session.commit()

    tiers = {p.digital_maturity for p in session.scalars(select(Pharmacy))}
    assert DigitalMaturity.NONE in tiers
    assert DigitalMaturity.ECOMMERCE_PARTIAL in tiers
