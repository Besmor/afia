# Tech Debt Log

Small issues that are worth fixing but not blocking. Sweep during polish phase (Aug 17-18) or when a related block introduces the fix naturally.

## TD-001: Module-level engine binding in `app.api.search` — RESOLVED

**Date logged:** 2026-08-07 (Block 2)
**Date resolved:** 2026-08-08 (Block 4)
**Severity:** Low (harmless, gitignored)
**Location:** `backend/app/api/search.py` `build_engine()` runs at import time
**Symptom:** Importing `app.main` (and thus `app.api.search`) eagerly creates/touches `backend/afia.db` on disk. Idempotent, `.db` is gitignored, tests override the dependency anyway — so nothing breaks.
**Fix applied:** Engine construction moved into `app.db.session.get_engine()`, a lazy factory cached by db path (module-level dict). `app.db.session.get_session()` is the shared FastAPI dependency, used by `app.api.search`; `scripts/sms_mock.py` uses `get_engine()` directly for its CLI session. Imports now have zero side effects.

## TD-002: `datetime.utcnow()` deprecation in SQLAlchemy defaults

**Date logged:** 2026-08-08 (Block 3)
**Severity:** Low (deprecation warning only; still functional)
**Location:** `backend/app/models/pharmacy.py` — `default=datetime.utcnow` on `created_at` and `last_verified_at` columns
**Symptom:** Python 3.13 deprecates `datetime.utcnow()`; SQLAlchemy passes through, generating hundreds of `DeprecationWarning` entries during test runs.
**Proper fix:** Replace `default=datetime.utcnow` with `default=lambda: datetime.now(timezone.utc)` and store timezone-aware datetimes.
**When to fix:** Aug 17-18 polish sweep, or earlier if warnings become distracting.

## TD-003: `httpx → httpx2` deprecation in Starlette TestClient

**Date logged:** 2026-08-08 (Block 3)
**Severity:** Low (deprecation warning; tests still pass)
**Location:** transitively via FastAPI's `TestClient` in `backend/tests/test_search.py`
**Symptom:** `StarletteDeprecationWarning: Using httpx with starlette.testclient is deprecated; install httpx2 instead.`
**Proper fix:** Install `httpx2` and update TestClient import when FastAPI ships an update supporting it. Currently pinned by upstream.
**When to fix:** Wait for upstream FastAPI to bless the migration path. Do not manually swap now.

