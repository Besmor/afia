# Pre-submission tweaks

Small implementation items that surfaced while writing the dissertation
but were deliberately deferred so that the writing phase would not be
interrupted. All of these ship BEFORE the video-demo recording on
Sunday 16 August so the demo shows the tweaked behaviour, and BEFORE
final submission.

**Not future work.** Everything in this list is in-scope for the MVP;
these are targeted improvements to what has already shipped.

## 1. SMS location handling (drug + dose + location)

**Current behaviour.** `respond(session, text)` in
`backend/app/services/sms_mock.py` takes only text; it scores every SMS
query against a fixed Conakry city centroid (`SMS_DEFAULT_LAT = 9.54`,
`SMS_DEFAULT_LON = -13.68`). The rationale in the code comment is that
feature-phone SMS does not carry device location by default, unlike a
PWA request that ships browser Geolocation.

**What to build.** Parse a district name from the SMS text so that the
same ranking that benefits PWA users benefits SMS users. Two acceptable
approaches:

- **Substring match on district names.** After the medication and dose
  are extracted, scan the remainder of the query for a Conakry district
  name (Kaloum, Dixinn, Ratoma, Matam, Matoto) case-insensitively and
  accent-folded via `fold_accents` (reuses `backend/app/services/text.py`).
  If found, use the district centroid instead of `SMS_DEFAULT_LAT / LON`.
  Simplest to implement; matches what a real user is likely to type
  (`paracetamol 500mg kaloum`).
- **Structured prefix.** Require the user to prefix with a district code
  (`KALOUM: paracetamol 500mg`). More explicit, less user-friendly.

Preferred: substring match. Backwards-compatible (no district word = old
behaviour). Add 4-6 tests to `test_sms_mock.py` covering each district
name, accented and unaccented input, and the no-district fallback.

**Downstream update.** The Track B harness (`scripts/eval/track_b_harness.py`)
currently uses per-scenario `user_lat / user_lon` for the SMS channel
implicitly; verify the harness output stays deterministic after this
change, and re-run the harness so the JSON dump reflects the new
behaviour before video recording.

**Estimate:** 45-60 min including tests.

## 2. PWA autocomplete: "syrup" appears in English

**Current bug.** On the Landing autocomplete dropdown, medication rows
show the form as the raw enum value (`syrup`) instead of the French
label (`Sirop`). Same class of issue as the Détail Médicaments card
that was fixed under task #34 for `tablet` → `Comprimé`.

**What to fix.** Verify that `formLabelFr` from
`frontend/src/lib/medicationForm.ts` is called on the autocomplete row's
secondary line in `frontend/src/components/MedicationSearch.tsx`. If the
mapping is missing entries for any of the eight galenic forms (tablet,
capsule, syrup, injection, ointment, drops, suppository, sachet), add
them. If the mapping is complete but not applied in the autocomplete
row, wire it in.

**Downstream update.** Manual smoke on every galenic form: type a query
that matches each form (e.g. `insulin` → injection, `paracétamol` →
tablet + syrup, `hydrocortisone` → ointment) and verify each shows the
French label.

**Estimate:** 15-25 min including manual smoke.

## 3. Map default zoom (Reviewer 1 D4)

**Current behaviour.** The Results Maps view calls `fitBounds` with the
user location plus all top-10 pharmacy pins. On the Kaloum peninsula
this often zooms out so far that street names disappear and the pin
cluster reads as an abstract shape rather than a walkable neighbourhood.

**What to fix.** Change the initial zoom logic to fit only the user
location plus the **3-4 nearest pharmacies**, at a maximum-zoom cap that
keeps street names legible. Reviewer 1's rationale: the primary user
decision is which of the immediately-walkable pharmacies to go to, so
the map should default to the walking-radius view, not the all-results
view. User can still zoom out manually to see further pins.

Implementation sketch: sort the results by distance ascending, take
the first 3-4, compute bounds from user + those pins only, apply
`fitBounds` with a `maxZoom: 15` or `16` cap.

**Estimate:** 15-30 min including manual smoke.

## 4. Overlapping map pins (Block G followup)

**Current bug.** When a single pharmacy stocks multiple forms of the
same medication (e.g. Paracetamol tablet AND syrup), the backend returns
two SearchResult rows with identical `pharmacy_id` and identical `latitude`,
`longitude`. Their pins stack exactly on top of each other on the Leaflet
map; only the top pin is clickable, and the other becomes invisible.

**What to fix.** In the map view only (list view is fine as-is because
each row is a distinct offer), dedupe the marker list by `pharmacy_id`
before rendering. The popover for a deduped marker should still show
whichever medication row was ranked first.

**Estimate:** 15-30 min.

## Ordering on Sunday

Do these BEFORE the video demo recording so the video shows the final
behaviour. Suggested slot: Sunday morning-early afternoon, ~2 hours
total, followed by a fresh smoke test of the app end-to-end, followed
by the demo recording.

Do them in this order (small warm-up first, riskier last):
1. `syrup` → `Sirop` PWA autocomplete label (15-25 min)
2. Overlapping pins dedupe (15-30 min)
3. Map default zoom (15-30 min)
4. SMS location parsing (45-60 min)
