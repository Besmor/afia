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
