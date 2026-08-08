# Afia Runbook

Afia is a middle-layer pharmaceutical access platform for Conakry, Guinea. A FastAPI backend is the single source of truth for medication search over a synthetic pharmacy ecosystem, served to two channels: a React PWA (not yet built, see `docs/`) and a local SMS mock. This runbook gets the backend running and exercised end to end. Full project context lives in `README.md` and `CLAUDE.md`.

## Prerequisites

- Python 3.11+ (developed/tested on 3.13)
- Node 18+ (for the frontend, once it exists)
- git

## Setup

```bash
git clone <repo-url> afia
cd afia/backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Seed the synthetic ecosystem

Generate the synthetic pharmacy/medication/stock JSON files, then load them into SQLite. Run both from `backend/` with the venv active.

```bash
python -m app.data.generate_ecosystem   # writes data/synthetic/*.json
python -m app.data.seed_db              # writes backend/afia.db
```

`seed_db` is idempotent (rows matched by primary key), so re-running it is safe. Pass `--reset` to drop and recreate all tables first.

## Run the backend

```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload
```

Health check:

```bash
curl http://127.0.0.1:8000/health
# {"status":"ok","service":"afia"}
```

## Query the search endpoint

```bash
curl "http://127.0.0.1:8000/search?q=paracetamol&limit=2"
```

```json
[
  {
    "pharmacy_id": "Pharmacy_02",
    "pharmacy_name": "Pharmacie Pharmacy 02",
    "district": "Kaloum",
    "latitude": 9.521483,
    "longitude": -13.694496,
    "digital_maturity": "BASIC_WEBSITE",
    "medication_id": 1,
    "medication_inn": "Paracetamol",
    "medication_form": "tablet",
    "medication_strength": "500 mg",
    "quantity": 55,
    "price_gnf": 10830,
    "last_verified_at": "2026-08-04T01:10:15.179445"
  }
]
```

Results are ranked by walking-realistic distance, stock quantity, and digital-maturity tier trust (`app/services/ranking.py`, rationale in `docs/decisions/ADR-006-ranking-weights.md`).

```bash
# Brand-name query (matches the same INN via brand_names)
curl "http://127.0.0.1:8000/search?q=doliprane"

# Explicit caller location (defaults to the Kaloum centroid if omitted)
curl "http://127.0.0.1:8000/search?q=amoxicillin&user_lat=9.54&user_lon=-13.68&limit=5"
```

Expected shape: a JSON array of pharmacy/medication/stock matches, ranked best-first, empty array if nothing matches.

## Try the SMS mock

No real SMS provider is involved (ethics/scope constraint) — this is a local Python mock that parses a text string and returns the reply a feature-phone user would see. Run from the repo root with the backend venv active.

```bash
# INN query
python scripts/sms_mock.py "Where can I find paracetamol?"

# Brand-name query
python scripts/sms_mock.py "Do you have Doliprane?"

# Fallback (no medication matched)
python scripts/sms_mock.py "hello there"
# Afia: type a medication name (e.g. 'paracetamol') to find nearby pharmacies with stock.
```

Each exchange is logged to `logs/sms_mock.log`.

## Run the tests

```bash
cd backend
source .venv/bin/activate
pytest
```

Expected: 18 passed, across 5 files (`test_ranking.py`, `test_search.py`, `test_seed_db.py`, `test_sms_mock.py`, plus the package `__init__.py`). SQLAlchemy `datetime.utcnow()` deprecation warnings are expected noise (TD-002, deferred).

## Regenerate synthetic data

```bash
cd backend
python -m app.data.generate_ecosystem --seed 20260806
```

The default seed (`20260806`) is what the committed calibration log in `data/synthetic/README.md` assumes. Same seed produces the same ecosystem; change it to explore alternative synthetic realisations, but log the seed used in any evaluation results. Generated JSON files are gitignored — always regenerate rather than expecting them to be present after a fresh clone.

## Project structure

```
afia/
├── backend/
│   ├── app/
│   │   ├── api/           HTTP route handlers (search.py)
│   │   ├── db/            Shared SQLAlchemy engine/session factory
│   │   ├── models/        SQLAlchemy models (Pharmacy, Medication, StockItem)
│   │   ├── services/      Ranking logic, SMS mock service
│   │   └── data/          Synthetic ecosystem generator + DB seeder
│   └── tests/              Pytest suite
├── frontend/                React + Vite PWA (scaffold pending)
├── data/
│   ├── scan/                Anonymised 15-pharmacy digital-maturity scan
│   └── synthetic/            Generated ecosystem JSON (gitignored) + README
├── docs/
│   ├── decisions/            ADRs
│   ├── tech_debt.md
│   └── daily_log.md
└── scripts/
    └── sms_mock.py           SMS mock CLI entry point
```
