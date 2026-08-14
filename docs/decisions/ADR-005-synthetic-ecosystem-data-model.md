# ADR-005: Synthetic Ecosystem Data Model

Date: 2026-08-06
Status: accepted

## Context

The MVP evaluation runs against a synthetic Conakry pharmacy ecosystem grounded in a real 15-pharmacy digital-maturity scan (June-July 2026, EECS DSREC-approved). The ecosystem must support:

1. Medication search (query string → ranked pharmacy list with stock signal)
2. Proximity ranking (walking-realistic distance, per Friesen et al. 2025)
3. Digital-maturity-aware trust weighting (higher tier = more trustworthy stock signal)
4. Reproducibility (seeded generation)

The scan captured **only** digital-maturity indicators (name, address, website, online ordering, stock/price display, phone, email, digital maturity tier, social media). It does NOT contain:
- Geolocation (addresses only, mostly French descriptive)
- Operating hours
- Stock levels
- Prices
- Medication catalogues

Everything above must be synthesised, grounded in the scan's real distributions and published sources where available. This positions Afia's synthetic generation squarely in the Statistical-based SDG category (Osorio-Marulanda et al. 2024).

## Decision

Three-table schema: `pharmacies`, `medications`, `stock_items` (sparse join).

### `pharmacies` — 15 records, 1:1 mapped to anonymised scan

| Field               | Type   | Source    | Notes                                                                                                                     |
| ------------------- | ------ | --------- | ------------------------------------------------------------------------------------------------------------------------- |
| id                  | str PK | Real      | `Pharmacy_01`..`Pharmacy_15`, matches anonymised scan                                                                     |
| name                | str    | Synthetic | Plausible French-named placeholders (not real names)                                                                      |
| district            | enum   | Real      | Preserves observed distribution: 4 Kaloum, 9 Ratoma, 1 Dixinn, 1 Unknown                                                  |
| latitude, longitude | float  | Grounded  | Sampled within district polygon (public OSM Conakry commune boundaries)                                                   |
| digital_maturity    | enum   | Real      | Preserves observed distribution: 11 NONE, 3 BASIC_WEBSITE, 1 ECOMMERCE_PARTIAL                                            |
| phone               | str?   | Synthetic | Placeholder Guinean-format numbers                                                                                        |
| opens_at, closes_at | time   | Grounded  | Calibrated to typical West African community pharmacy hours (08:00-20:00 default; documented in data/synthetic/README.md) |
| open_on_sunday      | bool   | Synthetic | ~30% Sunday opening (rotating on-call precedent, invented for MVP)                                                        |

### `medications` — WHO EML seeded, ~50-100 records

| Field | Type | Source |
|-------|------|--------|
| id | int PK | Auto |
| inn | str | Real (WHO EML International Non-proprietary Names) |
| brand_names | str? | Synthetic (plausible; not tied to real brands) |
| form | enum | Real (tablet, capsule, syrup, injection, ointment, drops, suppository, sachet) |
| strength | str | Real (WHO EML strengths, e.g. "500 mg") |
| therapeutic_class | str | Real (WHO EML anatomical/therapeutic groupings) |
| is_who_essential | bool | Real |

### `stock_items` — sparse join

Not every pharmacy stocks every medication. Calibration:
- Coverage per pharmacy: draw from truncated distribution centred on ~60% of catalogue (typical LMIC pharmacy assortment)
- Stock quantity: log-normal (median 20 units, tail to 200)
- Price: log-normal in GNF (Guinean Franc), tier-adjusted by digital maturity (higher tier ≈ slightly higher price signal, consistent with private-pharmacy premium literature)
- Digital-maturity-aware trust: higher tier pharmacies get `last_verified_at` closer to `datetime.utcnow`; NONE-tier pharmacies get stale `last_verified_at` (48-168h old), simulating the real-world signal-quality gap the platform is designed to bridge

## Consequences

**Positive:**
- Reproducible (single `SYNTHETIC_SEED` env variable controls all randomness)
- Defensible under Osorio-Marulanda's Statistical-based SDG category
- Directly supports the four search-ranking factors the platform advertises
- Anonymised scan committed to repo; real names/addresses stay in the author's local Excel

**Negative:**
- No real medication stock observations means calibration for stock levels and prices leans on published LMIC literature rather than direct evidence. Documented as a limitation in Discussion.
- Geolocations sampled from district polygons rather than real geocoded addresses. Acceptable for proximity ranking demonstration; noted in limitations.
- Sunday opening percentage is invented (no scan data). Low-stakes for MVP.

## Related

- Osorio-Marulanda et al. (2024) — Statistical-based SDG legitimising category
- Silva et al. (2025) — no-gold-standard framing
- Friesen et al. (2025) — walking-realistic ranking motivation
- Falchetta et al. (2020) — Conakry as informal-majority context
