"""Synthetic ecosystem generator.

Reads the anonymised Conakry scan and the WHO EML seed, produces a deterministic
synthetic pharmacy ecosystem (pharmacies + medications + stock items) as three
JSON files under `data/synthetic/`.

Run:
    cd backend && python -m app.data.generate_ecosystem [--seed 20260806]

Design in `docs/decisions/ADR-005-synthetic-ecosystem-data-model.md`.
"""
from __future__ import annotations

import argparse
import json
import random
from datetime import datetime, time, timedelta
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]
SCAN_PATH = REPO_ROOT / "data" / "scan" / "conakry_scan_anonymised.json"
EML_PATH = Path(__file__).parent / "who_eml_seed.json"
DISTRICTS_PATH = Path(__file__).parent / "conakry_district_bounds.json"
OUT_DIR = REPO_ROOT / "data" / "synthetic"

DEFAULT_SEED = 20260806

# Tier-adjusted stock-freshness windows (hours old)
FRESHNESS_HOURS_BY_TIER = {
    "API_LINKED": (0, 1),
    "ECOMMERCE_FULL": (0, 1),
    "ECOMMERCE_PARTIAL": (6, 24),
    "BASIC_WEBSITE": (24, 72),
    "NONE": (48, 168),
}

# Tier-adjusted price multipliers (higher tier ~ slightly higher price signal)
PRICE_MULTIPLIER_BY_TIER = {
    "API_LINKED": 1.10,
    "ECOMMERCE_FULL": 1.08,
    "ECOMMERCE_PARTIAL": 1.05,
    "BASIC_WEBSITE": 1.02,
    "NONE": 1.00,
}

# Base price (GNF) medians per medication form, log-normal draws
BASE_PRICE_GNF_MEDIAN = {
    "tablet": 5000,
    "capsule": 8000,
    "syrup": 15000,
    "injection": 25000,
    "ointment": 12000,
    "drops": 18000,
    "suppository": 10000,
    "sachet": 3000,
}


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def generate_pharmacies(scan: list[dict], districts: dict, rng: random.Random) -> list[dict]:
    """Turn anonymised scan records into synthetic pharmacy records."""
    pharmacies: list[dict] = []
    for record in scan:
        bounds = districts[record["district"]]
        lat = rng.uniform(bounds["lat_min"], bounds["lat_max"])
        lon = rng.uniform(bounds["lon_min"], bounds["lon_max"])

        # Operating hours: default 08:00-20:00, slight variation
        open_hour = 8 + rng.choice([0, 0, 0, 1])  # mostly 08:00, sometimes 09:00
        close_hour = 20 + rng.choice([-1, 0, 0, 0])  # mostly 20:00, sometimes 19:00

        pharmacies.append({
            "id": record["id"],
            "name": f"Pharmacie {record['id'].replace('_', ' ')}",  # placeholder, not the real name
            "district": record["district"],
            "latitude": round(lat, 6),
            "longitude": round(lon, 6),
            "digital_maturity": record["digital_maturity"],
            "phone": f"+224 6{rng.randint(10, 99)} {rng.randint(10, 99)} {rng.randint(10, 99)} {rng.randint(10, 99)}",
            "opens_at": time(open_hour, 0).isoformat(),
            "closes_at": time(close_hour, 0).isoformat(),
            "open_on_sunday": rng.random() < 0.30,
        })
    return pharmacies


def generate_medications(eml_seed: dict) -> list[dict]:
    """Assign integer IDs to WHO EML medications."""
    medications = []
    for i, med in enumerate(eml_seed["medications"], start=1):
        medications.append({
            "id": i,
            "inn": med["inn"],
            "brand_names": med.get("brand_names"),
            "form": med["form"],
            "strength": med["strength"],
            "therapeutic_class": med["therapeutic_class"],
            "is_who_essential": True,
        })
    return medications


def generate_stock(
    pharmacies: list[dict],
    medications: list[dict],
    rng: random.Random,
    now: datetime,
) -> list[dict]:
    """Sparse per-pharmacy per-medication stock and prices."""
    stock: list[dict] = []
    stock_id = 0
    for pharmacy in pharmacies:
        tier = pharmacy["digital_maturity"]
        price_mult = PRICE_MULTIPLIER_BY_TIER.get(tier, 1.0)
        freshness_lo, freshness_hi = FRESHNESS_HOURS_BY_TIER.get(tier, (48, 168))

        # Coverage: ~60% of catalogue with variation
        coverage = max(0.30, min(0.90, rng.gauss(0.60, 0.15)))
        catalogue_sample = rng.sample(medications, k=int(len(medications) * coverage))

        for med in catalogue_sample:
            # Stock quantity: log-normal, median 20
            quantity = max(1, int(rng.lognormvariate(mu=3.0, sigma=0.8)))

            # Price: log-normal around form-specific median, tier-adjusted
            base = BASE_PRICE_GNF_MEDIAN.get(med["form"], 8000)
            price = int(rng.lognormvariate(mu=0, sigma=0.25) * base * price_mult)

            # Stock freshness: tier-adjusted staleness
            hours_old = rng.uniform(freshness_lo, freshness_hi)
            last_verified = now - timedelta(hours=hours_old)

            stock_id += 1
            stock.append({
                "id": stock_id,
                "pharmacy_id": pharmacy["id"],
                "medication_id": med["id"],
                "quantity": quantity,
                "price_gnf": price,
                "last_verified_at": last_verified.isoformat(),
            })
    return stock


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate the Afia synthetic ecosystem.")
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED, help="Random seed for reproducibility.")
    parser.add_argument("--out-dir", type=Path, default=OUT_DIR, help="Output directory for JSON files.")
    args = parser.parse_args()

    rng = random.Random(args.seed)
    now = datetime(2026, 8, 6, 18, 0, 0)  # noqa: DTZ001 (naive matches DB columns; see TD-002 for tz-migration)

    scan = load_json(SCAN_PATH)
    eml = load_json(EML_PATH)
    districts = load_json(DISTRICTS_PATH)["districts"]

    pharmacies = generate_pharmacies(scan, districts, rng)
    medications = generate_medications(eml)
    stock = generate_stock(pharmacies, medications, rng, now)

    args.out_dir.mkdir(parents=True, exist_ok=True)
    (args.out_dir / "pharmacies.json").write_text(json.dumps(pharmacies, indent=2, ensure_ascii=False))
    (args.out_dir / "medications.json").write_text(json.dumps(medications, indent=2, ensure_ascii=False))
    (args.out_dir / "stock_items.json").write_text(json.dumps(stock, indent=2, ensure_ascii=False))

    print(f"Generated with seed {args.seed}:")
    print(f"  {len(pharmacies)} pharmacies -> {args.out_dir / 'pharmacies.json'}")
    print(f"  {len(medications)} medications -> {args.out_dir / 'medications.json'}")
    print(f"  {len(stock)} stock items -> {args.out_dir / 'stock_items.json'}")


if __name__ == "__main__":
    main()
