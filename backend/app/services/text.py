"""Shared text-normalisation helpers for catalogue-name matching.

Hoisted out of `sms_mock.py` (commit 7b56b20) so both the SMS mock and the
`/medications/autocomplete` endpoint compare catalogue names the same way.
"""
from __future__ import annotations

import unicodedata


def fold_accents(text: str) -> str:
    """Lowercase `text` and strip accents, e.g. "Paracétamol" -> "paracetamol".

    Used for catalogue-name comparison only (never for a value shown back to
    the user), so input arriving with or without accents matches the same
    catalogue row.
    """
    decomposed = unicodedata.normalize("NFKD", text.lower())
    return "".join(ch for ch in decomposed if not unicodedata.combining(ch))
