# Tech Debt Log

Small issues that are worth fixing but not blocking. Sweep during polish phase (Aug 17-18) or when a related block introduces the fix naturally.

## TD-001: Module-level engine binding in `app.api.search`

**Date logged:** 2026-08-07 (Block 2)
**Severity:** Low (harmless, gitignored)
**Location:** `backend/app/api/search.py` `build_engine()` runs at import time
**Symptom:** Importing `app.main` (and thus `app.api.search`) eagerly creates/touches `backend/afia.db` on disk. Idempotent, `.db` is gitignored, tests override the dependency anyway — so nothing breaks.
**Proper fix:** Move engine construction into a lazy factory inside `get_session()` so imports have zero side effects. Cache the engine in a module-level dict keyed by db path.
**When to fix:** Naturally during Block 4 (SMS mock will need the same session dependency — refactor to shared `app.db.session` module then).
