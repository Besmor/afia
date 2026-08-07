"""Afia FastAPI application entrypoint."""
from fastapi import FastAPI

from app.api import search

app = FastAPI(
    title="Afia",
    description="Middle-layer pharmaceutical access platform for Guinea",
    version="0.1.0",
)

app.include_router(search.router)


@app.get("/health")
def health() -> dict[str, str]:
    """Liveness check."""
    return {"status": "ok", "service": "afia"}


# Further route registrations to be added by Claude Code as they are built:
# from app.api import sms
# app.include_router(sms.router)
