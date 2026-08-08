"""Pharmacy result ranking service.

Combines three normalised [0, 1] signals into a single score used to order
`GET /search` results: walking-realistic distance, stock quantity and
digital-maturity tier trust. Weighting rationale in
`docs/decisions/ADR-006-ranking-weights.md`.
"""
from __future__ import annotations

import math
from typing import Protocol, TypeVar

from app.models.pharmacy import DigitalMaturity

# Earth radius in metres, used for the haversine great-circle distance.
EARTH_RADIUS_M = 6_371_000

# Walking-realistic correction applied to straight-line distance. Walking
# routes are less direct than straight lines, and walking measurements report
# substantially lower access than driving-time estimates (Friesen et al. 2025).
WALKING_DISTANCE_FACTOR = 1.4

# Distance beyond which a result's distance score soft-caps to ~0.
DISTANCE_SOFT_CAP_M = 5_000

# Weights for the combined score. Must sum to 1.0.
DISTANCE_WEIGHT = 0.6
STOCK_WEIGHT = 0.2
TIER_WEIGHT = 0.2

# Digital-maturity tier trust weighting: higher tiers imply fresher, more
# reliable stock signals.
TIER_TRUST_SCORES: dict[DigitalMaturity, float] = {
    DigitalMaturity.API_LINKED: 1.0,
    DigitalMaturity.ECOMMERCE_FULL: 0.9,
    DigitalMaturity.ECOMMERCE_PARTIAL: 0.6,
    DigitalMaturity.BASIC_WEBSITE: 0.4,
    DigitalMaturity.NONE: 0.2,
}


def haversine_distance_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great-circle distance in metres between two lat/lon points."""
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return 2 * EARTH_RADIUS_M * math.asin(math.sqrt(a))


def walking_distance_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Walking-realistic distance: haversine distance corrected by `WALKING_DISTANCE_FACTOR`."""
    return haversine_distance_m(lat1, lon1, lat2, lon2) * WALKING_DISTANCE_FACTOR


def distance_score(distance_m: float) -> float:
    """Normalise a walking distance to [0, 1], nearer = higher score.

    Linear soft cap: 0 m -> 1.0, `DISTANCE_SOFT_CAP_M` and beyond -> 0.0.
    """
    if distance_m <= 0:
        return 1.0
    if distance_m >= DISTANCE_SOFT_CAP_M:
        return 0.0
    return 1.0 - (distance_m / DISTANCE_SOFT_CAP_M)


def stock_scores(quantities: list[int]) -> list[float]:
    """Normalise a list of stock quantities to [0, 1], per-search.

    Highest quantity in the set scores 1.0, lowest scores 0.0. If every
    quantity is equal (including a single-item set), all score 1.0.
    """
    if not quantities:
        return []

    lowest, highest = min(quantities), max(quantities)
    if highest == lowest:
        return [1.0 for _ in quantities]

    return [(q - lowest) / (highest - lowest) for q in quantities]


def tier_score(tier: DigitalMaturity) -> float:
    """Digital-maturity tier trust score, per `TIER_TRUST_SCORES`."""
    return TIER_TRUST_SCORES[tier]


def combined_score(dist_score: float, stock_score: float, trust_score: float) -> float:
    """Weighted combination of the three normalised signals (0.6 / 0.2 / 0.2)."""
    return (
        DISTANCE_WEIGHT * dist_score
        + STOCK_WEIGHT * stock_score
        + TIER_WEIGHT * trust_score
    )


class Rankable(Protocol):
    """Shape a result must have to be ranked (e.g. `SearchResult` from `app.api.search`)."""
    latitude: float
    longitude: float
    quantity: int
    digital_maturity: str


T = TypeVar("T", bound=Rankable)


def rank_results(results: list[T], user_lat: float, user_lon: float) -> list[T]:
    """Sort `results` by combined ranking score, descending (best first).

    Stock quantity is normalised across the full result set passed in, so
    callers should rank the complete match set before applying any `limit`.
    """
    if not results:
        return []

    quantities = [r.quantity for r in results]
    quant_scores = stock_scores(quantities)

    scored = []
    for result, quant_score in zip(results, quant_scores):
        dist_m = walking_distance_m(user_lat, user_lon, result.latitude, result.longitude)
        dscore = distance_score(dist_m)
        tscore = tier_score(DigitalMaturity(result.digital_maturity))
        score = combined_score(dscore, quant_score, tscore)
        scored.append((score, result))

    scored.sort(key=lambda pair: pair[0], reverse=True)
    return [result for _, result in scored]
