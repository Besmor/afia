"""CLI wrapper for the Afia SMS mock service.

Sends a single mock SMS text through `app.services.sms_mock.respond` against
the on-disk `backend/afia.db` and prints the reply, simulating what a
feature-phone user would receive.

Usage:
    python scripts/sms_mock.py "Where can I find paracetamol?"
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1] / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from sqlalchemy.orm import Session

from app.db.session import get_engine
from app.services.sms_mock import respond


def main() -> None:
    parser = argparse.ArgumentParser(description="Send a mock SMS query to Afia and print the reply.")
    parser.add_argument("text", help="The SMS text, e.g. 'Where can I find paracetamol?'")
    args = parser.parse_args()

    with Session(get_engine()) as session:
        print(respond(session, args.text))


if __name__ == "__main__":
    main()
