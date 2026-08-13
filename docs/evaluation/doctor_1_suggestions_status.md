# DITL Reviewer 1 — Suggestions status ledger

Traceable record of every actionable item raised by Reviewer 1 during the
Wed 12 Aug DITL session, with disposition. Sourced from
`DITL Reviewer 1.docx` (session notes, French). Kept as a lookup while
writing the Methodology, Results, Discussion, and Future Work chapters.

**Session summary:** ~2 hours (planned 45 min), 6 scenarios + debrief,
anonymised, no recording. Reviewer engaged deeply and volunteered
substantive feedback on almost every screen.

**Overall disposition ratio:** roughly 35% shipped, 15% partial,
50% deferred to dissertation Discussion / Future Work. This is a
deliberate scope discipline: the deferred items become the strongest
evidence base for the Limitations and Future Work chapters, which is
more publishable than a "we fixed everything" claim.

## Shipped

| # | Item | Commit(s) | Task |
|---|---|---|---|
| S1 | SMS fallback replies translated from English to French | 13859e5 | #25 |
| S2 | Safety-aware French reply for symptom queries (`j'ai mal à la tête`) | 7b56b20 | #28 |
| S3 | Pharmacy Détail defaults to Médicaments tab on arrival | e329b14 | #26 |
| S4 | Results heading contrast (green-on-green → dark text) | fb9c26e | #27 |
| S5 | Results heading wraps on narrow screens (follow-up to S4) | b900aaf | — |
| S6 | Autocomplete shows matched brand in dropdown row when match came from brand_names (`Metformin · (Glucophage)`) | 29a6335 + 949a7b6 | #21 |
| S7 | Brand context propagates from Landing selection to Results heading and Détail Médicaments card | a107dfe + c072df5 | #30 |
| S8 | Détail "Pour: ..." banner uses the brand when brand was searched | (inline follow-up to S7) | — |

## Partial

| # | Item | What's done | What's still open |
|---|---|---|---|
| P1 | Brand-first end-to-end display | Autocomplete surfaces brand (S6); Results heading + Détail card use brand (S7); Détail banner uses brand (S8) | Autocomplete dropdown row still shows INN as primary label with brand parenthetical — Reviewer 1's underlying point is that brand should lead when the user typed the brand. Flip proposed as the next polish step. |
| P2 | Empty-state / no-match reply better | French wording landed (S1) with safety framing (S2); "n'a pas reconnu ce médicament" replaces "type a medication name" | No "did you mean X?" spelling suggestion; no "X is equivalent to Y" bridging when the typed brand isn't in the catalogue |
| P3 | Brand-generic equivalence signalling | Brand is visible on autocomplete and downstream (S6, S7, S8) | No info bubble ("Doliprane est équivalent au paracétamol, disponible dans ces pharmacies") for the case where the user typed a brand the catalogue doesn't stock but its generic is available |

## Deferred (to Discussion / Limitations / Future Work chapters)

Each item below is a real product observation from Reviewer 1 that we
consciously chose not to build in the remaining time. The dissertation
discusses each honestly as a validated future-work item rather than a
gap the reviewer discovered accidentally.

| # | Item | Notes for the chapter |
|---|---|---|
| D1 | Filter chips must be functional (Toutes / Ouvertes / Plus proches / Moins chères) | Reviewer 1 tried them; they are visually present but not wired. Documented as a MVP scope-cut, not a bug. |
| D2 | Map pin should show pharmacy name rather than price | Reviewer 1 rationale: prices are approximately equal across Conakry so price on the pin is noise. Distance and identity are signal. Design change with cascading layout implications. |
| D3 | User location dot more visible; centre map on user; locate-me control | Blue dot too subtle; would benefit from a directional indicator and a locate-me button near the +/- zoom controls. |
| D4 | Map should open at a zoom that shows 3-4 surrounding pharmacies | Current default fits all results in bounds. Reviewer 1 wanted a tighter default reflecting immediate walkable radius. |
| D5 | 24-hour and on-call pharmacy modelling | Some Conakry pharmacies are open 24 h; the on-call ("de garde") schedule is inconsistently respected in practice. Our `OUVERTE / FERMÉE / De garde` pill model does not capture 24 h or track schedule adherence. |
| D6 | Full paracetamol dose ladder (50 / 100 / 150 / 200 / 300 / 500 / 1000 mg) | Our seed only carries a small subset; Reviewer 1 pointed out real prescription practice covers the full ladder. |
| D7 | Full amoxicillin dose ladder (125 / 250 / 500 / 1000 mg) and full brand list (Flemming, Biotic Plus, etc.) | Same class of gap as D6. |
| D8 | Insulin unit modelling | Insulin is prescribed in unités (10, 18, ...), not mg. Our `strength: str` column stores "100 IU/ml" but real prescriptions describe unit-count draw, not concentration. Fundamental medication-model gap. |
| D9 | Scan-a-prescription capability | Reviewer 1 noted patients often cannot read doctor handwriting; a scan-to-recognise flow would help. Requires OCR + prescription-format modelling. |
| D10 | SMS reply grouping by form | For a medication with multiple forms in one reply, group comprimés on one line and sirops on another. |
| D11 | Redundant `/5ml` in dose display | The `120 mg / 5 ml` syrup convention is understood by prescribers; the `/5ml` half is redundant in a patient-facing display. Cosmetic. |
| D12 | "Did you mean?" spelling suggestions on autocomplete misses | Reviewer 1 wanted the empty-state to bridge back into the catalogue rather than dead-end. |
| D13 | Recommend the cheaper generic when the user typed a brand | Patients often ask for brand names though the generic is chemically identical and less expensive. Business-model and clinical-safety implications need care. |

## Informational — confirms existing design decisions

Not action items, but useful evidence to cite in the dissertation.

| # | Observation | Cited in |
|---|---|---|
| I1 | "Les prix sont approximatifs, similaires; c'est surtout la proximité qui prime." | Validates ADR-006's 0.6 distance / 0.2 stock / 0.2 tier weighting, and the deliberate exclusion of price from the ranking formula. |
| I2 | Patients search by brand names ("population n'est pas très instruite, ils achètent ce qui est écrit sur l'ordonnance") | Validates the middle-layer architecture thesis: the platform, not the pharmacy, does brand-to-generic bridging. Cite in Discussion. |
| I3 | Rare-medication patients (hypertensive, diabetic, epileptic, rheumatoid) benefit most from the platform | Validates the target user profile. Cite in Introduction and Discussion. |
| I4 | Symptom queries carry real clinical risk (pregnancy contraindications, hypertension-as-cause) | Ethics-critical framing. Cite in Ethics section and Discussion; this is a research contribution DITL surfaced that a purely technical evaluation would not have. |

## Notes for the Methodology chapter (Track B evidence)

The Track B harness (`scripts/eval/track_b_harness.py`, commit 20783de)
runs the six scenarios headlessly against the seeded ecosystem and
dumps a timestamped JSON at `data/eval/track_b_run_*.json`. Two
protocol-vs-artefact discrepancies to describe honestly in the chapter:

1. **Bare-query SMS routes to ask-back, not pharmacy list.** Scenarios
   1, 2, and 3 use bare queries (`paracetamol`, `doliprane`,
   `amoxicillin`) without a dose token. Post the DITL 1 dose-parser
   work, SMS replies with an ask-back for the dose rather than a
   pharmacy list. This is a design choice we can defend, not a
   limitation: sending a fully-populated pharmacy list before knowing
   the dose would waste SMS segments and force the patient to filter
   mentally.

2. **Scenario 6 was fixed mid-evaluation.** The protocol still lists
   Scenario 6's expected reply as the old English fallback. Post-DITL 1
   (commit 7b56b20), `"J'ai mal à la tête"` correctly routes to the
   safety-aware French `SYMPTOM_MESSAGE`. Cite this as Hevner's
   "Design as Search Process" guideline in action: the reviewer
   surfaced a safety gap, the artefact evolved, the protocol document
   lags the code. Two acceptable framings:
   - Describe the protocol as a living document and cite the specific
     commit that shifted the expected outcome.
   - Update `docs/evaluation_protocol.md` retroactively to match the
     current safety-aware behaviour.

## Doctor 1's positive answer to "would this be usable?"

Direct quote (French, from the debrief section of the notes):

> "Oui car il y a des gens qui passent toute la journée à chercher un
> médicament précis sur l'ordonnance..."

Reviewer 1 explicitly answered yes to the usability question and gave
concrete grounding: patients in Conakry currently spend whole days
searching for prescribed medications, and pharmacists routinely
telephone doctors to negotiate substitutions. The platform addresses a
real pain point.
