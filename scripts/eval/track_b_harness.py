"""Track B evaluation harness.

Runs the six scenarios from `docs/evaluation_protocol.md` headlessly against
the seeded synthetic ecosystem and dumps a structured JSON record per
scenario/channel. This is the raw evidence base for the Results chapter's
quantitative section; interpretation of the captured output happens in the
dissertation, not here (see the module's Scope note in the task brief).

Reuses the same access patterns as the existing suite: FastAPI's
`TestClient` against the on-disk `backend/afia.db` (same database `GET
/search` uses when the app runs for real) for the PWA channel, and
`app.services.sms_mock.respond` against a plain `Session` for the SMS
channel, the same pattern `scripts/sms_mock.py` uses.

Run:
    cd afia
    source backend/.venv/bin/activate
    python scripts/eval/track_b_harness.py
"""
from __future__ import annotations

import json
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

# scripts/eval/track_b_harness.py -> parents[2] == repo root
REPO_ROOT = Path(__file__).resolve().parents[2]
BACKEND_DIR = REPO_ROOT / "backend"
OUT_DIR = REPO_ROOT / "data" / "eval"

sys.path.insert(0, str(BACKEND_DIR))

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.db.session import get_engine
from app.main import app
from app.services.sms_mock import respond

SEED = 20260806
PWA_RESULT_LIMIT = 10

# The six scenarios, per docs/evaluation_protocol.md. `expected_summary` is
# the protocol's stated expected behaviour, carried through for the writer's
# reference when interpreting the captured output; the harness does not
# assert against it.
SCENARIOS: list[dict[str, Any]] = [
    {
        "id": "baseline-paracetamol",
        "name": "Baseline urban search (Kaloum resident)",
        "user_lat": 9.515,
        "user_lon": -13.705,
        "query": "paracetamol",
        "channel": "both",
        "expected_summary": (
            "Top 3 results are Kaloum-district pharmacies stocking "
            "paracetamol; at least one is BASIC_WEBSITE tier or better."
        ),
    },
    {
        "id": "brand-name-doliprane",
        "name": "Brand-name match",
        "user_lat": 9.515,
        "user_lon": -13.705,
        "query": "doliprane",
        "channel": "both",
        "expected_summary": (
            "Same results as Scenario 1; the matcher resolves the brand "
            "name Doliprane to the generic INN Paracetamol."
        ),
    },
    {
        "id": "ratoma-amoxicillin",
        "name": "Ratoma resident (informal-majority context)",
        "user_lat": 9.60,
        "user_lon": -13.60,
        "query": "amoxicillin",
        "channel": "both",
        "expected_summary": (
            "Top results are Ratoma-district pharmacies stocking "
            "amoxicillin; the top result is not a Kaloum pharmacy even if "
            "one has higher stock or a better digital-maturity tier."
        ),
    },
    {
        "id": "cross-district-trust-weighting",
        "name": "Cross-district trust weighting",
        "user_lat": 9.55,
        "user_lon": -13.65,
        "query": "paracetamol",
        "channel": "pwa",
        "expected_summary": (
            "A moderately-close, high-tier, high-stock pharmacy may rank "
            "above a slightly-closer NONE-tier, low-stock pharmacy, per the "
            "0.6/0.2/0.2 distance/stock/tier weighting."
        ),
    },
    {
        "id": "sparse-stock-insulin",
        "name": "Sparse-stock medication (Insulin)",
        "user_lat": 9.515,
        "user_lon": -13.705,
        "query": "insulin",
        "channel": "both",
        "expected_summary": (
            "May return fewer than the default 10 results (roughly 1-5); "
            "the response is still sensible and does not crash on a small "
            "result set."
        ),
    },
    {
        "id": "ambiguous-no-medication-query",
        "name": "Ambiguous / no-medication query",
        "user_lat": 9.54,
        "user_lon": -13.68,
        "query": "J'ai mal à la tête",
        "channel": "sms",
        "expected_summary": (
            "The catalogue matcher does not identify a medication; a "
            "French fallback/guidance reply is returned rather than a "
            "pharmacy list."
        ),
    },
]


def reseed_ecosystem() -> None:
    """Regenerate the synthetic ecosystem and reset `afia.db` from the fixed seed.

    Mirrors the "Common preparation" steps in `docs/evaluation_protocol.md`
    (steps 1-2), so every harness run starts from an identical, reproducible
    ecosystem regardless of what a previous run or manual testing left in
    `data/synthetic/` or `backend/afia.db`.
    """
    subprocess.run(
        [sys.executable, "-m", "app.data.generate_ecosystem", "--seed", str(SEED)],
        cwd=BACKEND_DIR,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        [sys.executable, "-m", "app.data.seed_db", "--reset"],
        cwd=BACKEND_DIR,
        check=True,
        capture_output=True,
    )


def run_pwa(client: TestClient, scenario: dict[str, Any]) -> dict[str, Any]:
    """Call GET /search for `scenario` and capture the ranked pharmacy_ids."""
    entry: dict[str, Any] = {
        "scenario_id": scenario["id"],
        "channel": "pwa",
        "query": scenario["query"],
        "user_lat": scenario["user_lat"],
        "user_lon": scenario["user_lon"],
        "elapsed_ms": None,
        "top_pharmacy_ids": None,
        "sms_reply": None,
        "sms_reply_length_chars": None,
        "error": None,
    }
    start = time.perf_counter()
    try:
        response = client.get(
            "/search",
            params={
                "q": scenario["query"],
                "user_lat": scenario["user_lat"],
                "user_lon": scenario["user_lon"],
                "limit": PWA_RESULT_LIMIT,
            },
        )
        response.raise_for_status()
        results = response.json()
        entry["top_pharmacy_ids"] = [result["pharmacy_id"] for result in results]
    except Exception as exc:  # noqa: BLE001 (one scenario's failure must not crash the run)
        entry["error"] = str(exc)
    entry["elapsed_ms"] = round((time.perf_counter() - start) * 1000, 2)
    return entry


def run_sms(session: Session, scenario: dict[str, Any]) -> dict[str, Any]:
    """Call `respond` for `scenario` and capture the reply text."""
    entry: dict[str, Any] = {
        "scenario_id": scenario["id"],
        "channel": "sms",
        "query": scenario["query"],
        "user_lat": scenario["user_lat"],
        "user_lon": scenario["user_lon"],
        "elapsed_ms": None,
        "top_pharmacy_ids": None,
        "sms_reply": None,
        "sms_reply_length_chars": None,
        "error": None,
    }
    start = time.perf_counter()
    try:
        reply = respond(session, scenario["query"])
        entry["sms_reply"] = reply
        entry["sms_reply_length_chars"] = len(reply)
    except Exception as exc:  # noqa: BLE001 (one scenario's failure must not crash the run)
        entry["error"] = str(exc)
    entry["elapsed_ms"] = round((time.perf_counter() - start) * 1000, 2)
    return entry


def _print_summary(index: int, total: int, entry: dict[str, Any]) -> None:
    prefix = f"[{index}/{total}] {entry['scenario_id']} {entry['channel']}"
    if entry["error"] is not None:
        print(f"{prefix}: ERROR {entry['error']} ({entry['elapsed_ms']:.0f} ms)")
    elif entry["channel"] == "pwa":
        count = len(entry["top_pharmacy_ids"])
        print(f"{prefix}: {count} results ({entry['elapsed_ms']:.0f} ms)")
    else:
        print(
            f"{prefix}: reply {entry['sms_reply_length_chars']} chars "
            f"({entry['elapsed_ms']:.0f} ms)"
        )


def main() -> None:
    reseed_ecosystem()

    client = TestClient(app)
    sms_session = Session(get_engine())

    channels_run: list[str] = []
    records: list[dict[str, Any]] = []
    total = len(SCENARIOS)

    try:
        for index, scenario in enumerate(SCENARIOS, start=1):
            channels = ["pwa", "sms"] if scenario["channel"] == "both" else [scenario["channel"]]
            for channel in channels:
                if channel not in channels_run:
                    channels_run.append(channel)
                entry = run_pwa(client, scenario) if channel == "pwa" else run_sms(sms_session, scenario)
                records.append(entry)
                _print_summary(index, total, entry)
    finally:
        sms_session.close()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")  # noqa: DTZ005 (local time is fine for a filename)
    out_path = OUT_DIR / f"track_b_run_{timestamp}.json"

    payload = {
        "meta": {
            "seed": SEED,
            "run_at": datetime.now().astimezone().isoformat(),
            "afia_version": app.version,
            "scenarios_count": total,
            "channels_run": channels_run,
        },
        "scenarios": records,
    }
    out_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False))

    print(f"Wrote {out_path.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
