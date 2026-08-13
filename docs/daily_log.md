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

**Tuesday evening (Block G + polish):** Built the Results map view per
Figma "Vue Maps" screens using Leaflet + OSM tiles. Segmented Liste/Maps
toggle at top of Results, custom DivIcon price pins, popover card on pin
click with pharmacy meta and "voir la pharmacie" CTA. Three atomic
commits (1c4646e, 9fce09c, 6b0d896). Followup polish batch in flight to
add phone line to card (SearchResult was missing phone though DB rows
are populated), preserve list/map toggle across nav via URL param
?view=map, and make the visually-disabled bookmark button read as
disabled at a glance.

**Manual-smoke findings on Block G:** (a) pharmacies rendering in the
Atlantic / mangrove / uninhabited zones because generate_ecosystem.py
uses district-centroid bounding boxes with no land mask; deferred to
Wed morning as task #24, must fix before Doctor 1 sees the map;
(b) overlapping pins where a pharmacy has multiple SearchResult rows
at the identical coord; deferred as task #22; (c) Pharmacy Detail's
own mini-map still shows the "Carte (à venir)" placeholder — this is
pre-existing and would be a separate Block H.

**DITL scheduling:** Doctor 1 confirmed for Wed 12 Aug (exact time TBC,
awaiting slot confirmation). Doctor 2 still awaiting reply — could be
Wed 13 or Thu 14.

## 2026-08-12 (Wednesday)

**Shipped:** Sea-pharmacies fix (commit e4014eb). Iterated once on
Pharmacy_01 coord after smoke-testing revealed the initial coord and the
first fix-attempt both landed in water east of Coléah; final coord
(9.535, -13.685) confirmed dry across paracetamol / amoxicillin /
metformin searches.

**DITL Session #1 — Reviewer 1 (~2 hours, planned 45 min).** Ran long
because the doctor engaged deeply and volunteered substantive feedback
on almost every screen. Notes saved anonymised in
`afia/docs/evaluation/DITL Reviewer 1.docx` per DSREC exemption.
Consent confirmed verbally at start; no audio/video recorded.

**Seven themes surfaced:**

1. Brand names are how Guinean patients actually shop, not INN.
   "Population n'est pas très instruite, ils achètent ce qui est écrit
   sur l'ordonnance." Validates our brand-in-catalogue design and the
   pending autocomplete-brand-hint polish (task #21).
2. "No result" is a walkaway moment. Doctor explicitly said the
   unmatched-dose SMS reply would send him to the pharmacy in person
   rather than retry. Empty-states must soft-land users.
3. Symptom queries are ethically dangerous. The "j'ai mal à la tête"
   scenario surfaced concrete risk examples (pregnant woman receives
   drug suggestion contraindicated for pregnancy; hypertensive patient
   whose headache is a symptom of the hypertension itself, not a
   paracetamol case). Platform must never recommend medication for a
   symptom description. Our current fallback refuses but in English,
   which is both a bug and a missed safety-framing opportunity.
4. Visual hierarchy on Results fails. Green "Résultats pour X" heading
   blends into the green background; doctor's eyes went directly to the
   pharmacy list.
5. Map pins carry the wrong signal. Prices are approximately equal
   across Conakry so price on the pin is noise; distance and pharmacy
   name are signal.
6. Filter chips being non-functional is a broken promise. Doctor tried
   them.
7. Dose UX has three issues: not always relevant (syrups), most variants
   missing from the seed (paracetamol comes in 50 / 100 / 150 / 200 /
   300 / 500 / 1000 mg in Guinea, we have far fewer), and should
   preselect a sensible default after picking a medication.

**Bugs to fix Wed evening before Doctor 2 (P0 / P1):**
- #25 SMS fallback in English (three occurrences: "amoxicilin 500mg",
  "mixtard", "jai mal tete")
- #28 Symptom-query reply French + safety-aware wording
- #26 Detail default tab → Médicaments not Infos Générales
- #27 Results heading contrast

**Bigger findings deferred to dissertation write-up:**
- Symptom-query safety gap → Ethics + Discussion chapters. This is a
  real research contribution: DITL surfaced a safety gap that a purely
  technical evaluation could not have. Cite Hevner et al. (2004)
  Design Evaluation guideline.
- Brand-first shopping behaviour → validates middle-layer architecture
  thesis in Discussion. Bridging brand-generic is precisely what a
  middle layer is for.
- Approximately-equal prices → validates ADR-006's 0.6 / 0.2 / 0.2
  weighting (distance / stock / tier), with price correctly absent
  from the formula. Doctor's exact wording: "les prix sont
  approximatifs, similaires, c'est surtout la proximité qui prime."
- Scan-a-prescription feature suggestion → documented as future work.
- 24h pharmacies and inconsistent on-call adherence → documented as
  future work; the FERMÉE / OUVERTE pill is useful, the "De garde"
  pill is contested because on-call schedules aren't always respected
  in practice.

**Doctor 2 scheduling:** still not confirmed. User will remind Thursday
morning.
