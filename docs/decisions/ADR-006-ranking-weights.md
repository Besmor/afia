# ADR-006: Search Result Ranking Weights

Date: 2026-08-08
Status: accepted

## Context

`GET /search` (ADR-005) returns every pharmacy that stocks a matching medication, but users need the results ordered so the most useful pharmacy appears first. "Most useful" combines three things a user in Conakry actually cares about: how far they would have to walk, whether the pharmacy has enough stock to be worth the trip, and how much we can trust that the stock figure is current.

We need a single combined score to sort by, and each of its inputs needs its own normalisation and calibration decision.

## Decision

### The three factors and their weights

| Factor | Weight | Signal |
|--------|--------|--------|
| Walking-realistic distance | 0.6 | Nearer pharmacy = higher score |
| Stock quantity | 0.2 | More units in stock = higher score |
| Digital-maturity tier trust | 0.2 | Higher tier = higher score |

`combined_score = 0.6 * distance_score + 0.2 * stock_score + 0.2 * tier_score`

Distance dominates because the core user need is "which nearby pharmacy has drug X", per CLAUDE.md's search-first principle. Stock and trust are weighted equally and lower: they matter, but should not override a pharmacy being genuinely far away, nor should either one alone override the other.

Each factor is normalised to [0, 1] independently before weighting:

- **Distance score**: haversine straight-line distance, corrected for walking (see below), linearly mapped so 0 m scores 1.0 and the 5 km soft cap (see below) scores 0.0.
- **Stock score**: normalised per-search across the result set. Highest quantity returned = 1.0, lowest = 0.0. If every result has identical quantity (including a result set of one), all score 1.0, since there is no relative signal to draw from.
- **Tier score**: fixed lookup table (see below), independent of the other results in the set.

### Walking-realistic multiplier (1.4)

Straight-line (haversine) distance underestimates real pedestrian travel because streets are not straight lines. Friesen et al. (2025) report that walking-based access measurements are substantially lower than driving-time-based estimates commonly used in access studies, meaning driving-oriented distance proxies overstate how reachable a pharmacy actually is for someone on foot. We correct for this with a fixed 1.4x multiplier applied to the haversine distance before scoring.

This is a straight-line-to-network-distance approximation, not a routed path. A precise pedestrian routing engine is out of scope for the MVP; the multiplier is a documented, defensible stand-in that keeps the "nearer is better" ordering realistic without adding a routing dependency ahead of the 19 August deadline.

### Digital-maturity tier trust mapping

| Tier | Trust score | Rationale |
|------|-------------|-----------|
| API_LINKED | 1.0 | Live system integration; stock figure is as fresh as it can be |
| ECOMMERCE_FULL | 0.9 | Pharmacy actively maintains online stock/price data |
| ECOMMERCE_PARTIAL | 0.6 | Some online presence, but stock data is only partially maintained |
| BASIC_WEBSITE | 0.4 | Web presence exists but is not evidence of stock-data discipline |
| NONE | 0.2 | No digital footprint; stock figure is the least likely to be current |

This mirrors the `last_verified_at` staleness calibration already documented in ADR-005 (higher tiers get fresher timestamps): the tier is a proxy for how likely the recorded quantity still reflects reality. The floor is 0.2, not 0.0, because a NONE-tier pharmacy's stock signal is still synthetic ground truth in this evaluation context, not worthless; it should be discounted, not excluded.

### 5 km soft-cap decision

Beyond 5 km, walking stops being a realistic mode of access for a pharmacy errand in Conakry; a result that far away should sink to the bottom of the ranking regardless of stock or tier, rather than being excluded outright (a pharmacy might still be the only one stocking a given medication). A linear soft cap (score decays smoothly to 0 at 5 km, rather than a hard cutoff) avoids a discontinuity where two pharmacies a few metres apart, one just inside and one just outside the cap, would otherwise receive drastically different scores.

## Consequences

**Positive:**
- Single deterministic score keeps ranking behaviour testable in isolation (`backend/tests/test_ranking.py`) without needing HTTP or the database.
- Distance dominance matches the platform's stated search-first priority.
- Tier trust weighting gives the digital-maturity scan (the project's grounding dataset) a direct, visible role in the product behaviour, not just in data generation.

**Negative:**
- The 1.4 walking multiplier and the 5 km soft cap are both calibration judgement calls, not measured from Conakry pedestrian data; documented here as a limitation for Discussion.
- Stock quantity normalisation is relative to the current result set, so the same pharmacy's stock score can shift between searches with different result sets. This is intentional (it answers "who has the most, among these options") but is a behaviour worth surfacing to evaluators.

## Related

- ADR-005: Synthetic Ecosystem Data Model (digital-maturity tiers, `last_verified_at` staleness calibration)
- Friesen et al. (2025): walking-realistic ranking motivation
