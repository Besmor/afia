# DITL Reviewer 2 — Suggestions status ledger

Traceable record of every actionable item raised by Reviewer 2 during the
Thu 13 Aug DITL session, with disposition. Sourced from
`DITL Reviewer 2.docx` (session notes, French). Kept as a lookup while
writing the Methodology, Results, Discussion, and Future Work chapters.
Paired with `doctor_1_suggestions_status.md`; cross-references note where
the two reviewers converged independently.

**Session summary:** ~30 minutes (planned 45), Thu 13 Aug evening,
6 scenarios + debrief, anonymised as Reviewer 2, no recording. Reviewer 2's
lens is product-strategic: how would a Guinean patient or professional
actually use this? Where Reviewer 1 hunted bugs and safety concerns,
Reviewer 2 tested the mental model.

**Both reviewers answered "yes" to the usability question.** Reviewer 2:
"Oui sans équivoque." Direct endorsement of the middle-layer + dual-channel
approach for Conakry.

**Overall disposition ratio:** most R2 suggestions are product-strategic
future-work items rather than in-scope bugs. One small copy fix ("Infos
pharmacie") ships immediately; the rest goes to Discussion / Future Work.

## Cross-reference with Reviewer 1 (independent confirmation)

These themes surfaced independently in both sessions. Independent confirmation
across reviewers is the strongest qualitative finding a DITL evaluation can
produce, and they are the ones to cite most confidently in the Results and
Discussion chapters.

| Theme | Reviewer 1 quote | Reviewer 2 quote | Chapter placement |
|---|---|---|---|
| Brand-first shopping | "Ils achètent ce qui est écrit sur l'ordonnance" | "Sur l'ordonnance, j'écris le nom commercial. Chaque pays a son nom commercial propre" | Results (finding), Discussion (validates middle-layer thesis) |
| No-result walkaway | "Cette réponse va m'embrouiller et je vais me rendre à la pharmacie directement" | "En tant que citoyen lambda, si je cherche le nom commercial et que je ne vois rien, je me dirai que le produit n'est pas disponible" | Results (finding), Limitations (soft-landing gap) |
| Symptom-safety refusal appreciated | Ethics-critical warning about pregnant / hypertensive users | "Cette réponse me montre que le concepteur se protège et ceci est quelque chose de très important pour nous les médecins" | Ethics section (research contribution), Discussion |
| Filter chips ignored or expected-to-work | Tried and found non-functional | Did not even notice them | Results (broken promise / dead weight), Future Work (wire or remove) |
| Iterative-improvement evidence: dose preselection | Original theme: dose should preselect from the picked row | "Preselection is helping very much" | Methodology (Hevner "Design as Search Process" citation), Results |

## Shipped (from Reviewer 2 feedback)

| # | Item | Commit(s) | Task |
|---|---|---|---|
| S1 | Détail tab renamed "Infos Générales" → "Infos pharmacie" to clarify it describes the pharmacy, not the medication (R2 confusion during Scenario navigation) | (Thu evening inline edit) | #34 |

## Deferred (to Discussion / Limitations / Future Work chapters)

Each item is a validated R2 observation we consciously did not build in the
remaining time. Cite each honestly as a validated future-work item, not a
gap the reviewer discovered accidentally.

| # | Item | Notes for the chapter |
|---|---|---|
| D1 | Prescription-mode search: enter multiple medications from one prescription and find a single pharmacy that stocks all of them | Reviewer 2's exact wording: "Possibilité de chercher plusieurs médicaments à la fois, écrire toute l'ordonnance, voir est-ce que tous les médicaments de l'ordonnance sont disponibles dans la même pharmacie". Directly matches how prescription-holders shop in low-resource contexts (avoid multiple trips). Real product feature idea; out of MVP scope. |
| D2 | Disease- or symptom-driven search with safety guardrails | R2 said citizens WILL type "diabète" expecting the app to help. R1 flagged the risk of symptom-driven mis-medication (pregnancy, hypertension-as-cause). The reconciliation: acknowledge the user behaviour (D2), keep the current safety refusal (validated by both), and consider a middle path in future work: "diabète is usually treated with a class of medications; consult your doctor for a prescription then use Afia to find stock" — carefully worded, not prescriptive. |
| D3 | Single-line dense display in autocomplete (form + strength on the same line as the INN) | R2 example: `Amoxicilline 250 mg/5 ml – Sirop` as one line. Contradicts our current brand-first two-line layout from task #30. Note as a future A/B question rather than an immediate fix; the current layout was itself R1-driven. |
| D4 | Galenic-form categorisation and filtering | R2 wants forms (comprimé, sirop, suppositoire, comprimé effervescent, injectable) surfaced as filterable categories in results. Related to the filter-chips-functional gap already tracked (both reviewers). |
| D5 | Delivery capability | R2 suggestion: "La possibilité d'une livraison de produit". Substantial scope (payments, logistics partners, KYC). Documented as future-work rationale for the Discussion chapter. |
| D6 | Multi-brand hierarchy display in results | R2 wants: search by DCI/INN → generic first, other commercial names of the same molecule below. Currently we return one row per (INN, form, strength) with matched_brand hint. Grouping by molecule with brand children would need schema and UX work. |

## Informational — confirms existing design decisions

| # | Observation | Cited in |
|---|---|---|
| I1 | User flow described in Scenario 1: distance → open/closed → stock → price → decide → walk or Maps | Validates the information architecture of the Results and Detail screens. The order of decision-relevant signals matches what we chose to display. Cite in Design chapter. |
| I2 | "Card en bas confirme que le produit dont j'ai besoin est disponible et suffisamment en stock" (referring to the Détail Médicaments card) | Validates the Médicaments-tab default we implemented after R1 (task #26). R2 arrived at the tab and immediately got the answer to the "is my drug here?" question. |
| I3 | Symptom safety refusal endorsed as important for medical practitioners | Validates the safety branch (task #28) as clinically appropriate, not just legally defensive. Reinforces the research-contribution framing. |
| I4 | Reference platform: Medicament.ma (Moroccan pharma database) | Worth a brief comparison in Related Work / Future Work: comparable initiative in a francophone context with different maturity constraints. |
| I5 | "Ceci pourrait être très utile aux guinéens qui pourraient les empêcher de sortir sous la pluie" | Illustrative user-benefit vignette; useful for the Introduction or Discussion opening. |
| I6 | Almost every family in Conakry has at least one smartphone | Validates the smartphone-PWA channel choice (as opposed to SMS-only). Cite in Design rationale for dual-channel. |

## Reviewer 2's "answer to Claude's question" (post-session)

- **Dose preselection:** "Preselection is helping very much." (Direct validation
  of R1's theme 7 fix — Hevner "Design as Search Process" evidence.)
- **Filter chips:** "They didn't notice the filter." (Confirms R1 — chips are
  either invisible or a broken promise. Remove or wire in future work.)
- **Autocomplete row information density:** "They didn't seem to need more
  information from the list." (Weak but present divergence from R2's own D3
  above — worth noting the reviewer's own tension when writing this up.)
