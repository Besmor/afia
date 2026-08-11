# Daily Log

## 2026-08-08 (Fri overnight session, 23:00-06:00)

**Shipped:** SQLite seeding, /search endpoint, proximity ranking service,
SMS mock service, shared db/session module refactor.

**Commits:** 33c50c4 (seed), fe0b231 (search), 4d495b2 (ranking),
be62cc8 (SMS mock + refactor).

**Tests:** 18 passing across 5 files.

**Outstanding:** TD-002 (datetime.utcnow deprecation), TD-003 (httpx2
migration) — both deferred to Aug 17-18 polish.

**Tomorrow:** Figma inspection, frontend scaffold (React + Vite + TS),
design system tokens extraction, implement critical-path screens
(search / results / pharmacy detail).

**Ethics checkpoint (raised end-of-day):** The 4 July DSREC message was an
exemption ("no human participants = no approval needed"), not a formal
conditional approval. Adding DITL doctors for expert review potentially
changes scope. Saturday morning first task is to email DSREC (CC Dr. Iqbal)
asking whether expert technical review of the artefact falls within the
existing exemption. Track B evaluation (heuristic + literature-anchored,
no human subjects) is prepared in parallel and will run regardless of the
DSREC response. See `../Rest_of_Plan_8Aug_to_19Aug.md` for the full
two-track schedule.

## 2026-08-09 (Saturday, Glasgow + train)

**Shipped:** DSREC email sent, evaluation protocol drafted (both tracks),
Vite + React + TS + Leaflet scaffold, design tokens extracted and verified
via palette preview, Landing/Search page implemented from Figma with real
Afia lockup logo, geolocation + district-picker fallback, react-router
wired to /results placeholder.

**Commits:** 4c5ecc2 (scaffold + tokens), (Landing page commit hash TBC).

**Demo-time gotcha to remember:** Browser geolocation gives real coords, so
when demoing from Glasgow (or anywhere outside Conakry) the ranking looks
meaningless because every synthetic pharmacy is ~5000 km away. Two
workarounds for demos and the video recording: (a) deny geolocation to
trigger the district picker and select Kaloum/Ratoma etc., or (b) paste
`?q=paracetamol&user_lat=9.515&user_lon=-13.705` directly into the URL.
Consider adding an env-based dev override before the video recording on
Aug 16 that force-overrides to a Conakry centroid in development mode.

**Sunday 10 Aug: Ben Nevis, zero coding.** Monday absorbs Sunday's
originally-planned FT-7 (Results page) + wiring + Plan B eval prep.

## 2026-08-10 (Monday) — SKIPPED

Full recovery day after Ben Nevis. No work. All Monday tasks rolled into
Tue 11 as a double-day.

## 2026-08-11 (Tuesday, ~5 hrs)

**Ethics green light:** DSREC replied — "This sounds like service evaluation
to me which does not require approvals, go ahead." Track A DITL is on;
recruitment WhatsApps sent to two doctors proposing Wed 13 / Thu 14.

**Shipped:**
- Block A — E2E wired, Landing → /search → /results returns real backend
  data (commit aa4fc49).
- Block B — FT-7 Results page built from screenshot workaround since Figma
  MCP quota exhausted. Styled pharmacy cards with tier badge, distance,
  stock, price, French copy (commit 5a2e4d3).
- Block D — FT-8 Pharmacy Detail page: green header, meta pills, tabs
  (Médicaments + Infos Générales functional; Moyen de paiement + Avis
  disabled). New backend endpoint GET /pharmacies/{id} (commit 3fd6fbe).
- Polish — OUVERTE/FERMÉE/De garde pills on both card and detail screens.
  Backend SearchResult schema extended with opens_at, closes_at,
  open_on_sunday; frontend computeStatus module handles Sunday +
  on-call logic (commit 99b6469).

**Tests:** 22 passing across backend. Frontend tsc + oxlint + vite build
clean.

**Commits pushed:** aa4fc49, 5a2e4d3, 3fd6fbe, 99b6469 (12 total on origin).

**Time budget:** Blocks A/B/D + polish took ~75% of planned time. Reinvested
the ~2.5 hr surplus into Block F (below).

**Block F (in progress, added Tue afternoon):** Autocomplete + dose picker.
The four Figma dosage screens (Recherche → Sélection → Dose_selection →
Dose_selected) show a search-bar flow that the original Figma inspection
missed (MCP quota died before capturing interactive states of the search
input). Adding this now to bring PWA + SMS in line with the
catalogue-matching architectural principle. Backend: /medications/autocomplete
endpoint + dose-filtered /search + SMS dose regex with three-branch reply
policy. Frontend: autocomplete dropdown + split search bar with dose picker.

**Deferred to Wed 12 morning:** Block C (Track B evaluation script outline,
~1 hr) — moved off Tue to keep Block F contiguous while the dosage flow
context is fresh.

**Outstanding:** pill edge-case testing (Sunday, after 20:00) — micro-task
for tonight or during a natural break.

**Doctor DITL slots:** awaiting reply. If both confirm for Wed, run one
session AM one PM; if only one, run Wed and hold Thu for the second.

**Manual-smoke followup surfaced (candidate for Wed 12):** typing "lu" on
the autocomplete returned Artemether + Lumefantrine (INN match), Insulin
(INN "soluble" contains "lu") and Metformin (brand "Glucophage" contains
"lu"). All correct per the brand-matching spec, but the UI shows only INN
+ form + strength so the match reason for Metformin and Insulin is
invisible. Followups in priority order: (1) show matched brand in the
secondary line when the match came from brand_names; (2) highlight the
matched substring; (3) rank INN prefix strictly above INN substring
strictly above brand substring. Not blocking commit.
