"""Seed the Afia SQLite database from the synthetic ecosystem JSON files.

Reads `data/synthetic/{pharmacies,medications,stock_items}.json` and populates
`backend/afia.db` using the SQLAlchemy models in `app.models.pharmacy`.
Idempotent: rows are matched by primary key, so a repeat run skips records
that already exist rather than duplicating them.

Run:
    cd backend && python -m app.data.seed_db [--reset] [--db-path afia.db]

Design in `docs/decisions/ADR-005-synthetic-ecosystem-data-model.md`.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, time
from pathlib import Path
from typing import Any

from sqlalchemy import create_engine, func, select
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from app.models.pharmacy import Base, Medication, Pharmacy, StockItem

REPO_ROOT = Path(__file__).resolve().parents[3]
SYNTHETIC_DIR = REPO_ROOT / "data" / "synthetic"
DEFAULT_DB_PATH = Path(__file__).resolve().parents[2] / "afia.db"


def load_json(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def seed_pharmacies(session: Session, records: list[dict[str, Any]]) -> int:
    """Insert pharmacy records not already present (matched by id). Returns count inserted."""
    inserted = 0
    for rec in records:
        if session.get(Pharmacy, rec["id"]) is not None:
            continue
        session.add(
            Pharmacy(
                id=rec["id"],
                name=rec["name"],
                district=rec["district"],
                latitude=rec["latitude"],
                longitude=rec["longitude"],
                digital_maturity=rec["digital_maturity"],
                phone=rec.get("phone"),
                opens_at=time.fromisoformat(rec["opens_at"]),
                closes_at=time.fromisoformat(rec["closes_at"]),
                open_on_sunday=rec["open_on_sunday"],
            )
        )
        inserted += 1
    return inserted


def seed_medications(session: Session, records: list[dict[str, Any]]) -> int:
    """Insert medication records not already present (matched by id). Returns count inserted."""
    inserted = 0
    for rec in records:
        if session.get(Medication, rec["id"]) is not None:
            continue
        session.add(
            Medication(
                id=rec["id"],
                inn=rec["inn"],
                brand_names=rec.get("brand_names"),
                form=rec["form"],
                strength=rec["strength"],
                therapeutic_class=rec["therapeutic_class"],
                is_who_essential=rec["is_who_essential"],
            )
        )
        inserted += 1
    return inserted


def seed_stock_items(session: Session, records: list[dict[str, Any]]) -> int:
    """Insert stock item records not already present (matched by id). Returns count inserted."""
    inserted = 0
    for rec in records:
        if session.get(StockItem, rec["id"]) is not None:
            continue
        session.add(
            StockItem(
                id=rec["id"],
                pharmacy_id=rec["pharmacy_id"],
                medication_id=rec["medication_id"],
                quantity=rec["quantity"],
                price_gnf=rec["price_gnf"],
                last_verified_at=datetime.fromisoformat(rec["last_verified_at"]),
            )
        )
        inserted += 1
    return inserted


def seed_all(session: Session, data_dir: Path = SYNTHETIC_DIR) -> dict[str, int]:
    """Seed pharmacies, medications and stock items from `data_dir`. Returns rows inserted per table."""
    pharmacies = load_json(data_dir / "pharmacies.json")
    medications = load_json(data_dir / "medications.json")
    stock_items = load_json(data_dir / "stock_items.json")

    # Order matters: stock_items has FK dependencies on pharmacies and medications.
    counts = {
        "pharmacies": seed_pharmacies(session, pharmacies),
        "medications": seed_medications(session, medications),
        "stock_items": seed_stock_items(session, stock_items),
    }
    session.flush()
    return counts


def print_row_counts(session: Session) -> None:
    """Print current row counts for each table."""
    pharmacy_count = session.scalar(select(func.count()).select_from(Pharmacy))
    medication_count = session.scalar(select(func.count()).select_from(Medication))
    stock_item_count = session.scalar(select(func.count()).select_from(StockItem))
    print("Row counts:")
    print(f"  pharmacies:  {pharmacy_count}")
    print(f"  medications: {medication_count}")
    print(f"  stock_items: {stock_item_count}")


def build_engine(db_path: Path, reset: bool = False) -> Engine:
    """Create the SQLite engine, optionally dropping and recreating all tables first."""
    engine = create_engine(f"sqlite:///{db_path}")
    if reset:
        Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    return engine


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed the Afia database from the synthetic ecosystem.")
    parser.add_argument("--db-path", type=Path, default=DEFAULT_DB_PATH, help="Path to the SQLite database file.")
    parser.add_argument("--data-dir", type=Path, default=SYNTHETIC_DIR, help="Directory containing the synthetic JSON files.")
    parser.add_argument("--reset", action="store_true", help="Drop and recreate all tables before seeding.")
    args = parser.parse_args()

    engine = build_engine(args.db_path, reset=args.reset)

    with Session(engine) as session:
        inserted = seed_all(session, args.data_dir)
        session.commit()

    print(f"Seeded {args.db_path} from {args.data_dir}:")
    print(f"  pharmacies:  {inserted['pharmacies']} inserted")
    print(f"  medications: {inserted['medications']} inserted")
    print(f"  stock_items: {inserted['stock_items']} inserted")

    with Session(engine) as session:
        print_row_counts(session)


if __name__ == "__main__":
    main()
