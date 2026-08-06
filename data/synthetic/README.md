# Synthetic Ecosystem

Programmatically generated pharmacy dataset for Conakry, grounded in the 15-pharmacy digital-maturity scan (`../scan/`). Regeneration scripts live in `backend/app/data/`; the generated data files themselves are gitignored (regenerate from seed).

## Grounding

**Real, preserved as-is from the scan:**
- Pharmacy count: 15
- Digital-maturity distribution: 11 NONE / 3 BASIC_WEBSITE / 1 ECOMMERCE_PARTIAL
- District distribution: 4 Kaloum / 1 Dixinn / 9 Ratoma / 1 Unknown

**Grounded synthetic (real basis, invented realisation):**
- Geolocation: sampled uniformly within OSM commune polygon for the pharmacy's district (Unknown → sampled from Conakry-wide bounding box)
- Operating hours: default 08:00-20:00, calibrated against typical West African community pharmacy norms
- Sunday opening: 30% probability (rotating on-call precedent)
- Medication catalogue: WHO Essential Medicines List (EML) 22nd edition subset, ~80 medications spanning eight therapeutic classes
- Per-pharmacy medication coverage: ~60% of catalogue, truncated normal distribution
- Stock quantities: log-normal (median 20 units, tail to 200)
- Prices (GNF): log-normal, tier-adjusted by digital maturity (higher tier = slightly higher price signal)
- Stock freshness (`last_verified_at`): tier-adjusted. API_LINKED = now; ECOMMERCE_FULL = <1h; ECOMMERCE_PARTIAL = 6-24h; BASIC_WEBSITE = 24-72h; NONE = 48-168h stale

## Reproducibility

All generation is seeded via `SYNTHETIC_SEED` (default `20260806`). Same seed produces the same ecosystem. Change the seed to explore alternative synthetic realisations, but log the seed in evaluation results.

## Calibration log

Update as calibration decisions are made or revised.

| Date | Attribute | Source | Decision |
|------|-----------|--------|----------|
| 2026-08-06 | Pharmacy count | Real scan | 15, preserved as-is |
| 2026-08-06 | Digital-maturity distribution | Real scan | Preserved 11/3/1 (NONE/BASIC/ECOMMERCE_PARTIAL) |
| 2026-08-06 | District distribution | Real scan | Preserved 4/9/1/1 (Kaloum/Ratoma/Dixinn/Unknown) |
| 2026-08-06 | Opening hours | West African norms | 08:00-20:00 default, 30% Sunday |
| 2026-08-06 | Medication catalogue | WHO EML 22nd ed. | ~80 essential medicines, 8 therapeutic classes |
| 2026-08-06 | Stock freshness by tier | Design decision | Tier-adjusted staleness (see main table) |

## Regeneration

```bash
cd backend
source .venv/bin/activate
python -m app.data.generate_ecosystem  # writes to data/synthetic/*.json
```

## Limitations (to be surfaced in Discussion chapter)

- Stock quantities and prices are calibrated against LMIC literature rather than direct pharmacy observation (the scan did not capture operational data by design).
- Geolocations are district-uniform, not address-precise. Sufficient for proximity-ranking demonstration; not sufficient for last-mile navigation.
- Sunday opening percentage is invented.
- Medication catalogue is WHO EML seeded, not calibrated to Guinean-specific dispensing patterns.
