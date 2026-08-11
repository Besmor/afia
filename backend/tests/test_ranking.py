"""Tests for the pharmacy result ranking service.

Isolated from HTTP and the database: results are constructed directly as
`SearchResult` objects. Design in `docs/decisions/ADR-006-ranking-weights.md`.
"""
from __future__ import annotations

from app.api.search import SearchResult
from app.services.ranking import rank_results

# Kaloum commune centroid, used as the fixed origin in these tests.
USER_LAT = 9.515
USER_LON = -13.705


def make_result(
    pharmacy_id: str,
    latitude: float,
    longitude: float,
    quantity: int = 20,
    digital_maturity: str = "NONE",
) -> SearchResult:
    """Build a synthetic `SearchResult` with sensible defaults for the fields ranking ignores."""
    return SearchResult(
        pharmacy_id=pharmacy_id,
        pharmacy_name=f"Pharmacie {pharmacy_id}",
        district="Kaloum",
        latitude=latitude,
        longitude=longitude,
        digital_maturity=digital_maturity,
        medication_id=1,
        medication_inn="Paracetamol",
        medication_form="tablet",
        medication_strength="500 mg",
        quantity=quantity,
        price_gnf=5000,
        last_verified_at="2026-08-08T00:00:00",
        opens_at="08:00:00",
        closes_at="20:00:00",
        open_on_sunday=False,
    )


def test_closer_pharmacy_ranks_higher():
    """Same stock and tier: the nearer pharmacy should rank first."""
    near = make_result("near", USER_LAT + 0.001, USER_LON)  # ~111 m away
    far = make_result("far", USER_LAT + 0.02, USER_LON)  # ~2.2 km away

    ranked = rank_results([far, near], USER_LAT, USER_LON)

    assert [r.pharmacy_id for r in ranked] == ["near", "far"]


def test_higher_stock_ranks_higher():
    """Same distance and tier: the pharmacy with more stock should rank first."""
    low_stock = make_result("low", USER_LAT, USER_LON, quantity=5)
    high_stock = make_result("high", USER_LAT, USER_LON, quantity=100)

    ranked = rank_results([low_stock, high_stock], USER_LAT, USER_LON)

    assert [r.pharmacy_id for r in ranked] == ["high", "low"]


def test_higher_tier_ranks_higher():
    """Same distance and stock: the higher digital-maturity tier should rank first."""
    low_tier = make_result("low_tier", USER_LAT, USER_LON, digital_maturity="NONE")
    high_tier = make_result("high_tier", USER_LAT, USER_LON, digital_maturity="API_LINKED")

    ranked = rank_results([low_tier, high_tier], USER_LAT, USER_LON)

    assert [r.pharmacy_id for r in ranked] == ["high_tier", "low_tier"]


def test_combined_weighting_lets_tier_and_stock_outweigh_small_distance_edge():
    """A moderately-close, high-tier, well-stocked pharmacy can outrank a
    very-close, low-tier, poorly-stocked one, proving the 0.6/0.2/0.2
    weighting is applied rather than distance alone deciding the order.
    """
    very_close_low_tier = make_result(
        "very_close_low_tier",
        USER_LAT + 0.0005,  # ~55 m away
        USER_LON,
        quantity=1,
        digital_maturity="NONE",
    )
    moderately_close_high_tier = make_result(
        "moderately_close_high_tier",
        USER_LAT + 0.01,  # ~1.1 km away
        USER_LON,
        quantity=100,
        digital_maturity="API_LINKED",
    )

    ranked = rank_results(
        [very_close_low_tier, moderately_close_high_tier], USER_LAT, USER_LON
    )

    assert ranked[0].pharmacy_id == "moderately_close_high_tier"


def test_all_equal_stock_scores_all_one():
    """When every result has the same stock quantity, stock scoring should not affect order."""
    same_stock_near = make_result("near", USER_LAT + 0.001, USER_LON, quantity=42)
    same_stock_far = make_result("far", USER_LAT + 0.02, USER_LON, quantity=42)

    ranked = rank_results([same_stock_far, same_stock_near], USER_LAT, USER_LON)

    assert [r.pharmacy_id for r in ranked] == ["near", "far"]


def test_empty_results_returns_empty_list():
    assert rank_results([], USER_LAT, USER_LON) == []
