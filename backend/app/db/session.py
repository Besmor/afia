"""Shared SQLAlchemy engine/session factory for the Afia backend.

Centralises engine construction so `app.api.search`, `app.services.sms_mock`
(and any future consumer) share one lazily-built, path-cached engine rather
than each module binding its own at import time.

Fixes TD-001 (docs/tech_debt.md): importing this module has no side effects
on disk; the engine is only created the first time `get_engine` (or
`get_session`) actually runs.
"""
from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

# backend/app/db/session.py -> parents[2] == backend/
DEFAULT_DB_PATH = Path(__file__).resolve().parents[2] / "afia.db"

_engines: dict[Path, Engine] = {}


def get_engine(db_path: Path = DEFAULT_DB_PATH) -> Engine:
    """Return the cached SQLAlchemy engine for `db_path`, building it on first use.

    Caching by path keeps one engine (and connection pool) per database file
    for the process lifetime, so repeated calls (e.g. once per request) don't
    re-open the database.
    """
    db_path = Path(db_path)
    if db_path not in _engines:
        _engines[db_path] = create_engine(f"sqlite:///{db_path}")
    return _engines[db_path]


def get_session() -> Iterator[Session]:
    """FastAPI dependency yielding a `Session` bound to `DEFAULT_DB_PATH`, closed after the request.

    Takes no parameters (a `db_path` argument here would make FastAPI treat
    it as a stray query parameter on every route that depends on this).
    Overridden in tests (via `app.dependency_overrides`) to point at a
    hermetic in-memory database instead.
    """
    session_local = sessionmaker(bind=get_engine())
    session = session_local()
    try:
        yield session
    finally:
        session.close()
