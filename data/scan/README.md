# Conakry Pharmacy Digital-Maturity Scan (Anonymised)

Anonymised results of the 15-pharmacy digital-maturity scan conducted in Conakry, June-July 2026, under EECS DSREC ethics approval (4 July 2026).

## Files

- `conakry_scan_anonymised.csv` — machine-readable anonymised scan
- `conakry_scan_anonymised.json` — same data, JSON format for Python consumption

## Ethics

Real pharmacy names, addresses, phone numbers, emails, and website URLs are held only in the author's local Excel spreadsheet outside this repository. Only the following per-pharmacy fields are stored here:

- `id` — sequential anonymous identifier (`Pharmacy_01`..`Pharmacy_15`)
- `district` — Conakry commune inferred from address keywords
- `digital_maturity` — categorical tier (NONE / BASIC_WEBSITE / ECOMMERCE_PARTIAL / ECOMMERCE_FULL / API_LINKED)
- `has_website` — bool
- `has_online_ordering` — bool
- `shows_stock_or_price` — bool
- `has_social_media` — bool
- `notes_present` — bool (whether the scan captured free-text notes; not the notes themselves)

## Observed distributions (source of grounding)

**Digital maturity:**
- NONE: 11 / 15 (73%)
- BASIC_WEBSITE: 3 / 15 (20%)
- ECOMMERCE_PARTIAL: 1 / 15 (7%) — one pharmacy attempted e-commerce with placeholder prices, no functional stock signals
- ECOMMERCE_FULL: 0
- API_LINKED: 0

**District:**
- Kaloum: 4
- Dixinn: 1
- Ratoma: 9
- Unknown (Plus Code address): 1

**Web presence:** 4 / 15 have any web presence; 6 / 15 have social media

## Use

Source of grounding for the synthetic ecosystem in `../synthetic/`. Preserves observed distributions of district and digital maturity so the synthetic 15-pharmacy dataset mirrors the real one at these dimensions.
