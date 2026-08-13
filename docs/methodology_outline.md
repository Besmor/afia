# Methodology chapter — outline scaffold

Fill in with bullets first. Convert bullets to prose in a separate pass.
Each section header is followed by:
- one-line **Purpose** (why this section exists in the chapter)
- **Sources** (where the facts already live in the repo)
- **Bullets to write** (what to actually put down)

Budget: ~4 columns of the dissertation (roughly 2500-3000 words). Do
not over-write; the reader wants clear, defensible design choices, not
a redocumentation of the entire codebase.

---

## 1. Research design (Design Science Research)

**Purpose.** Anchor the methodology in a recognised research paradigm
so evaluators know how to judge the artefact.

**Sources.** Hevner et al. (2004) 7 DSR guidelines, cited in
`docs/evaluation_protocol.md` and `Rest_of_Plan_8Aug_to_19Aug.md`.

**Bullets to write:**
- Why DSR fits this problem (artefact is the contribution, not the
  study)
- The 7 guidelines mapped one-line each to Afia (design as artefact,
  problem relevance, design evaluation, research contributions,
  research rigor, design as search process, communication of research)
- Explicit note that "design as search process" (guideline 6) was
  visible during DITL: Reviewer 1 surfaced the symptom-safety gap, the
  artefact evolved (commit 7b56b20), the protocol document lagged.
  Cite this drift honestly in Methodology, not as failure.

---

## 2. System architecture

**Purpose.** Explain the middle-layer + dual-channel design at a level
where a reader who doesn't touch the code can still follow the flow.

**Sources.** `README.md` mermaid diagram (copy it into the chapter),
`CLAUDE.md` "Architecture principles" section, `docs/decisions/`
ADRs 001-006.

**Bullets to write:**
- Middle-layer thesis: backend is single source of truth; PWA and SMS
  both call the same HTTP API. ADR-001.
- Why not pharmacy-side integration for MVP: digital-maturity scan
  showed near-zero API availability. ADR-001.
- Dual channel: PWA for smartphone users, SMS for feature-phone users.
  Both required for realistic Conakry deployment.
- SMS mock over Twilio: ADR-002. Cost + scope + regulatory reasons.
- Include the mermaid diagram from README (copy verbatim or redraw for
  the dissertation figure style).

---

## 3. Synthetic ecosystem construction

**Purpose.** Show that our test bed is grounded in real observation
rather than invented, and that its statistical properties preserve the
scan's key distributions.

**Sources.** `docs/decisions/ADR-003-synthetic-pharmacy-ecosystem-for-evaluation.md`
(if drafted; if not, in-progress content is in Rest_of_Plan and daily_log),
`docs/decisions/ADR-005-synthetic-ecosystem-data-model.md`,
`backend/app/data/generate_ecosystem.py`,
`data/scan/` (the 15-pharmacy scan is the grounding),
`data/synthetic/` (the generated output),
commit e4014eb (KNOWN_PHARMACY_COORDS + curated Conakry lat/lon).

**Bullets to write:**
- Why synthetic: DSREC exemption + no operational-data access
- What is grounded from the scan: 15 pharmacy identities, district
  distribution, digital-maturity distribution
- What is synthetic: coordinates (curated post-Reviewer 1 to land-safe
  Conakry neighbourhoods), opening hours, stock quantities, prices
- Determinism: fixed seed (20260806), reproducible on any machine
- Ethics constraint (no real patient/user/pharmacy operational data)
- Honest limitation: 15 pharmacies + 25 medications is small; documented
  as scope-controlled synthetic ecosystem, not a national database.

---

## 4. Search ranking algorithm

**Purpose.** Show the ranking is defensible, evidence-based, and
Reviewer-1-validated.

**Sources.** `docs/decisions/ADR-006-search-result-ranking-weights.md`,
`backend/app/services/ranking.py`, Friesen et al. (2025) reference,
Reviewer 1 quote in `docs/evaluation/doctor_1_suggestions_status.md`
("les prix sont approximatifs, similaires, c'est surtout la proximité
qui prime").

**Bullets to write:**
- Three signals: walking distance, in-stock quantity, digital-maturity
  tier
- Weights: 0.6 / 0.2 / 0.2 (ADR-006 rationale)
- Walking-realism multiplier: 1.4x haversine per Friesen et al. (2025)
- Deliberately NOT in the formula: price. Rationale documented in
  ADR-006 and independently validated by Reviewer 1's observation
  that Conakry prices vary little across pharmacies for equivalent
  products.
- Formula and one worked example (pick from a Track B harness
  scenario)

---

## 5. Catalogue-matching parser + SMS mock

**Purpose.** Justify the deliberate scope of the NLP: catalogue-match,
not free-form NLU.

**Sources.** `CLAUDE.md` "Architecture principles" (parser is
intentionally light), `backend/app/services/sms_mock.py`,
Reviewer 1 quote about brand-first shopping.

**Bullets to write:**
- Intent: normalise free-form user input into a fixed catalogue entry
  (INN + form + strength). Not general NLU.
- Brand-generic bridge: catalogue rows carry brand_names; parser
  matches either INN or brand substrings; accent-folded for French
  input (commit 7b56b20's `fold_accents` hoisted for reuse, 29a6335).
- Dose token extraction: regex on `(\d+(?:[.,]\d+)?)\s*(mg|g|mcg|ml|ui|iu)`,
  normalises units, three-branch reply policy for dose-matched,
  dose-mismatched, no-dose (Reviewer 1 explicitly appreciated the
  ask-back).
- Safety-aware branch: symptom keywords route to a non-prescribing
  reply. This was Reviewer 1's ethics-critical concern; the fix
  (commit 7b56b20) is a real research contribution the DITL surfaced.
- SMS mock architecture: local Python module, `respond(session, text)`,
  no Twilio, no external SMS provider. ADR-002.

---

## 6. Evaluation methodology (Track A DITL + Track B harness)

**Purpose.** Show the evaluation combines qualitative expert review
with quantitative deterministic runs, and that this pairing was
principled from the start.

**Sources.** `docs/evaluation_protocol.md`,
`docs/evaluation/DITL Reviewer 1.docx`,
`docs/evaluation/DITL Reviewer 2.docx` (after tonight),
`docs/evaluation/doctor_1_suggestions_status.md`,
`scripts/eval/track_b_harness.py` (commit 20783de),
`data/eval/track_b_run_*.json` (harness output).

**Bullets to write:**
- Two-track rationale: Track A (qualitative, DITL, DSREC-exempt
  service evaluation) + Track B (heuristic + literature-anchored +
  scripted harness, no human subjects, runs regardless)
- The six scenarios and what each is designed to test
- DITL session structure (intro / demo / scenarios / debrief, 45-90
  min per reviewer, anonymised, no recording)
- Reviewers: 2 qualified medical professionals, referred to as
  "Reviewer 1" and "Reviewer 2", themes cross-referenced across both.
- Track B harness: TestClient + SMS mock, deterministic run against
  seeded ecosystem, dumps JSON per scenario per channel
- Protocol-vs-artefact drift: honest note that Scenario 6's expected
  reply evolved after DITL 1 (Hevner "Design as Search Process")

---

## 7. Ethics constraints

**Purpose.** Head off any reviewer concern about human-subjects work
or real-data leakage.

**Sources.** `README.md` "Ethics constraint" section, DSREC
correspondence (Fri 4 July 2026 exemption + Tue 11 Aug 2026 DITL
service-evaluation confirmation).

**Bullets to write:**
- DSREC granted exemption 4 July 2026: no human participants, no
  formal ethics approval required
- DITL adds expert technical review, confirmed 11 Aug 2026 by DSREC
  as "service evaluation, no approvals required"
- No real patient, user, or pharmacy operational data anywhere in
  the artefact or the evaluation
- Reviewer notes anonymised (Reviewer 1 / 2), no audio/video, no
  professional-practice information captured
- Symptom-query safety wording (SMS_MESSAGE) is not just a UX
  choice; it operationalises the DSREC's underlying safeguard.

---

## Chapter-writing checklist

Before submitting the Methodology chapter as done:

- [ ] Every citation traces to a real paper / commit / file
- [ ] Every design choice is defended (not just described)
- [ ] Reviewer 1's validated points are cited where they support a
      design decision (price similarity → ranking weights;
      brand-first → middle-layer thesis; symptom safety → ethics)
- [ ] Reviewer 2's independently-confirmed themes are also cited
      (add after tonight's session)
- [ ] Protocol-vs-artefact drift is discussed honestly
- [ ] Word count is around 4 columns / 2500-3000 words
- [ ] The Methodology reads as if the author knew what they were
      doing from the start (Hevner's "Design as Search Process"
      re-frames iteration as intentional, not chaotic)
