# Evaluation Protocol

**Status:** First-pass draft (2026-08-08). To be refined before Wed 12 Aug evaluation day.

**Two-track strategy:** the same six scenarios are used regardless of which
evaluation methodology the DSREC clarifies is in scope.

- **Track A: Doctor-in-the-Loop (DITL) qualitative review** — contingent on
  DSREC confirming expert technical review falls within the 4 July exemption.
  Two qualified medical professionals each spend ~45 min walking through the
  scenarios and providing professional feedback on ranking sensibility,
  interface clarity, and medication-catalogue coverage. Aggregated,
  anonymised notes only; no audio/video, no personal data.
- **Track B: Self-conducted heuristic + literature-anchored evaluation** —
  runs regardless of DSREC response. The author walks through the same six
  scenarios, applies Hevner et al. (2004) 7 DSR guidelines and Nielsen's
  usability heuristics, and compares outputs against published benchmarks
  (Friesen et al. 2025 walking-access findings, Agarwal et al. 2020
  implementation factors, Tharumia Jagadeesan & Wirtz 2021 pharmacy-mapping
  methods).

## Common preparation

Before any evaluation session:

1. Seed the synthetic ecosystem with the fixed seed:
   `python -m app.data.generate_ecosystem --seed 20260806`
2. Seed the SQLite DB: `python -m app.data.seed_db --reset`
3. Start the backend: `uvicorn app.main:app --host 127.0.0.1 --port 8000`
4. Start the PWA: `cd frontend && npm run dev`
5. Confirm health endpoint: `curl 127.0.0.1:8000/health` returns 200

## The six scenarios

Each scenario specifies user location, query, expected behaviour, and what
the scenario is designed to test. The expected outputs are computed
against the seeded ecosystem (seed `20260806`, 15 pharmacies, 25 medications,
225 stock items).

### Scenario 1 — Baseline urban search (Kaloum resident)

- **User location:** Kaloum centroid (lat 9.515, lon -13.705)
- **Query:** `paracetamol`
- **Channel:** PWA and SMS (run both)
- **Expected behaviour:** top 3 results are Kaloum-district pharmacies stocking
  paracetamol (tablet or syrup). At least one has BASIC_WEBSITE tier or better.
- **What this tests:** baseline proximity ranking; catalogue matching on
  International Non-proprietary Name (INN); no false positives from other
  medications.
- **DSR guideline it exercises:** Design Evaluation (Hevner 2004 #3),
  Problem Relevance (#2).

### Scenario 2 — Brand-name match

- **User location:** Kaloum centroid (9.515, -13.705)
- **Query:** `doliprane`
- **Channel:** PWA and SMS
- **Expected behaviour:** same results as Scenario 1 (Doliprane is the
  paracetamol brand in the catalogue). Confirms the matcher resolves brand
  names to their generic INN.
- **What this tests:** catalogue matcher brand-name recognition; the
  language-invariance property (patients often ask for brand names rather
  than INNs).
- **DSR guideline:** Research Rigor (#5) — the matcher's brand resolution
  is a documented behaviour that we can verify deterministically.

### Scenario 3 — Ratoma resident (informal-majority context)

- **User location:** Ratoma centroid (9.60, -13.60)
- **Query:** `amoxicillin`
- **Channel:** PWA and SMS
- **Expected behaviour:** top results are Ratoma-district pharmacies stocking
  amoxicillin (capsule or syrup). Top result should NOT be a Kaloum pharmacy
  even if that pharmacy has higher stock or better digital-maturity tier.
- **What this tests:** ranking correctly weights walking-realistic distance
  as the dominant factor (0.6 weight per ADR-006), consistent with Friesen
  et al. (2025) finding that informal-area residents face substantially
  worse walking access.
- **Literature anchor (Track B):** Friesen 71.9% informal-majority + walking
  underestimation vs driving-time.

### Scenario 4 — Cross-district trust weighting

- **User location:** Between districts (approx. Dixinn edge, 9.55, -13.65)
- **Query:** `paracetamol`
- **Channel:** PWA
- **Expected behaviour:** a moderately-close pharmacy with high tier and high
  stock may rank above a slightly-closer NONE-tier pharmacy with low stock.
  Verify the combined 0.6/0.2/0.2 weighting is visible in the ordering.
- **What this tests:** the ranking service correctly combines the three
  signals (distance, stock, tier trust) rather than sorting on distance
  alone.
- **DSR guideline:** Design as Search Process (#6) — the ranking function
  was iteratively designed; this scenario verifies the search space chose
  a defensible point.

### Scenario 5 — Sparse-stock medication (Insulin)

- **User location:** Kaloum centroid (9.515, -13.705)
- **Query:** `insulin`
- **Channel:** PWA and SMS
- **Expected behaviour:** may return fewer than the default 10 results because
  Insulin (an injection) has lower per-pharmacy coverage than tablets. Response
  should still be sensible (correct pharmacies, no crashes, ~1-5 results).
- **What this tests:** graceful handling of sparse stock; ranking does not
  break on small result sets.
- **DSR guideline:** Design as Artifact (#1) — the artefact must function
  across the range of realistic query distributions.

### Scenario 6 — Ambiguous / no-medication query

- **User location:** any (use Conakry centroid 9.54, -13.68)
- **Query:** `"J'ai mal à la tête"` ("I have a headache", colloquial French)
- **Channel:** SMS (this is the most realistic SMS scenario)
- **Expected behaviour:** the catalogue matcher does NOT identify a
  medication (headache is a symptom, not a catalogue INN). The SMS fallback
  is returned: "Afia n'a pas reconnu ce médicament. Vérifiez l'orthographe
  ou envoyez le nom exact (ex: paracétamol). Afia ne remplace pas votre
  pharmacien."
- **What this tests:** the parser's boundary handling and the user-friendliness
  of the fallback message; verifies the "intentionally light NLP" scope
  decision is defensible.
- **Literature anchor (Track B):** Agarwal et al. (2020) user-friendly design
  is one of 12 identified implementation factors.

## Track A protocol (DITL) — contingent on DSREC approval

**Session structure (~45 min per doctor):**

1. **Introduction (5 min):** thank them, explain the project in one paragraph,
   confirm voluntary participation and right to stop at any time. Confirm they
   understand no personal or medical practice data will be recorded, only their
   professional opinion on the artefact.
2. **Demo the PWA (10 min):** run through the three critical-path screens
   (Landing/Search, Results, Pharmacy Detail) using Scenario 1 as the example.
3. **Scenarios 2-6 with the doctor (25 min):** for each, the doctor uses the
   PWA or reads the SMS response and provides feedback verbally. Author types
   anonymised notes.
4. **Debrief (5 min):** open-ended: "what would you change?", "is anything
   confusing?", "would this be usable by a patient in Conakry?"

**Notes discipline:**

- Anonymised: refer to the two doctors as "Reviewer 1" and "Reviewer 2".
- Aggregated for the Results chapter: themes across both reviewers, not
  quotes tied to individuals.
- No recording of audio, video, name, professional affiliation, or any
  personal identifier.

**Consent (informal, in advance):**

Email exchange confirming voluntary participation. Sample text:

> "Thank you for agreeing to a 45-min feedback session on my MSc project
> prototype. To confirm: (a) participation is voluntary and you may stop
> at any time, (b) no audio or video will be recorded, (c) only anonymised
> aggregated notes on your professional opinion of the technical artefact
> will appear in the dissertation, (d) no personal data or medical practice
> information will be collected. Please reply confirming you are happy to
> proceed on those terms."

## Track B protocol (self-conducted) — runs regardless

**Structure (~4 hours across Wed-Thu):**

1. **Scenario walkthrough (2 hrs):** author runs all six scenarios personally
   through both PWA and SMS. For each, records:
   - Actual top-3 results (screenshot or JSON dump)
   - Actual SMS response text
   - Response time
   - Any friction encountered
2. **Heuristic evaluation (1 hr):** apply Hevner et al. (2004) 7 DSR
   guidelines to the artefact as a whole. For each guideline, record: does
   Afia satisfy it, what evidence supports the claim, any gaps.
3. **Literature-anchored comparison (1 hr):** for each of the three primary
   anchors, document how Afia's actual behaviour compares to the published
   benchmark:
   - **Friesen et al. (2025)** — does the walking-realistic multiplier
     (1.4×) yield rankings consistent with the walking-underestimation
     finding for informal-area residents?
   - **Agarwal et al. (2020)** — how many of the 12 implementation factors
     does Afia address? Which are out of scope?
   - **Tharumia Jagadeesan & Wirtz (2021)** — how does Afia's synthetic
     pharmacy-mapping approach compare to the reviewed LMIC methodologies?

**Deliverable:** a section in the Results chapter titled "Heuristic and
literature-anchored evaluation" documenting the scenario outputs, the
7-guideline assessment, and the three-anchor comparison. Explicitly note
this is a self-conducted evaluation and cite Hevner et al. (2004) on the
appropriateness of researcher-conducted heuristic evaluation for
early-stage DSR artefacts.

## Data captured (both tracks)

- Per-scenario: query, expected behaviour, actual behaviour, notes
- Aggregated (Track A only): themes across the two reviewers
- Timing: how long each scenario takes to run
- Failure modes: any scenario that surfaces a bug or friction point

## Data NOT captured

- Personal information about doctors (Track A)
- Patient data (any track — not applicable)
- Real pharmacy operational data (any track — ethics constraint)
- Audio or video recordings (Track A)

## Deliverables into the Results chapter

- Scenario outcome table (one row per scenario)
- Ranking behaviour analysis (Kaloum-vs-Ratoma comparison)
- Aggregated qualitative feedback (Track A) OR heuristic assessment (Track B)
- Literature-anchored comparison table (Track B, complements Track A if both ran)
- Discussion of what the evaluation reveals about Afia's readiness for
  real-world deployment
