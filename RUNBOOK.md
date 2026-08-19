# Afia Runbook

Afia is a middle-layer pharmaceutical access platform for Conakry, Guinea. A FastAPI backend is the single source of truth for medication search over a synthetic pharmacy ecosystem, served to two channels: a React PWA (not yet built, see `docs/`) and a local SMS mock. This runbook gets the backend running and exercised end to end. Full project context lives in `README.md`.

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

# Syrup form, via brand name (Ventolin -> Salbutamol, syrup, 2 mg/5 ml)
curl "http://127.0.0.1:8000/search?q=ventolin&limit=3"

# Injection form, via brand name (Mixtard -> Insulin (soluble, human), 100 IU/ml)
curl "http://127.0.0.1:8000/search?q=mixtard&limit=3"
```

Expected shape: a JSON array of pharmacy/medication/stock matches, ranked best-first, empty array if nothing matches.

## Try the SMS mock

No real SMS provider is involved (ethics/scope constraint) — this is a local Python mock that parses a text string and returns the reply a feature-phone user would see. All replies are French, matching the target SMS user base (feature-phone users in Conakry, Guinea). Run from the repo root with the backend venv active.

```bash
# INN query (Paracetamol has two dose forms in the seed, so this asks back)
python scripts/sms_mock.py "Où puis-je trouver du paracetamol ?"

# Brand-name query (Doliprane -> Paracetamol)
python scripts/sms_mock.py "Avez-vous du Doliprane ?"

# Fallback (no medication matched)
python scripts/sms_mock.py "bonjour"
# Afia n'a pas reconnu ce médicament. Vérifiez l'orthographe ou envoyez le nom exact (ex: paracétamol). Afia ne remplace pas votre pharmacien.
```

A different medication, with dose supplied up front — since Ibuprofen has only one
catalogue entry (tablet, 400mg), this resolves directly to the ranked pharmacy list
(`format_response`) rather than an ask-back. Output depends on your local synthetic
seed, so it isn't reproduced here — run it and compare against
`GET /search?q=ibuprofen` below.

```bash
python scripts/sms_mock.py "ibuprofene 400mg"
```

Same query with a district named in the text — narrows the ranking origin from the
Conakry-wide default (`SMS_DEFAULT_LAT`/`LON`) to that commune's centroid
(`DISTRICT_CENTROIDS`), so the distances shown differ from the query above:

```bash
python scripts/sms_mock.py "ibuprofene 400mg ratoma"
```

Brand name only, no dose yet — an injection-form medication this time (not Paracetamol/Doliprane), triggering the French ask-back rather than a pharmacy list:

```bash
python scripts/sms_mock.py "mixtard"
# Insulin (soluble, human): injection 100IU/ml. Répondez avec la dose pour voir les pharmacies.
```

Symptom description rather than a medication name — this is the safety-critical
branch (`SYMPTOM_MESSAGE`, DITL Reviewer 1 P0): Afia deliberately refuses to guess a
drug for a symptom and defers to a clinician instead, regardless of any dose-like
tokens in the text:

```bash
python scripts/sms_mock.py "jai mal a la tete"
# Afia ne propose pas de médicament pour un symptôme. Consultez votre médecin ou pharmacien. Envoyez ensuite le nom du médicament prescrit pour vérifier les stocks.
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
