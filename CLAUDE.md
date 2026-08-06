# CLAUDE.md — Context for Claude Code

This file primes Claude Code with the context needed to work on Afia effectively. Read this first every session.

## What Afia is

A middle-layer pharmaceutical access platform for Guinea (specifically Conakry). Two user-facing channels (PWA + SMS) over a shared FastAPI backend, evaluated against a synthetic pharmacy ecosystem. Full context in README.md.

## Non-negotiables

- **Ethics constraint: synthetic data only.** No real patient, user, or pharmacy operational data anywhere in the system. All pharmacy records, inventory, and user scenarios are programmatically generated and grounded in the 15-pharmacy digital-maturity scan.
- **Scope: critical path only for MVP.** Landing/search → results → pharmacy detail. Do NOT implement onboarding, profile, favourites, notifications, offline UX, or any other Figma screen for the MVP. Those are documented as future work.
- **Deadline: 19 August 2026.** ~13 days from build kickoff (6 Aug). Every implementation decision should be judged against "does this reach a working evaluable prototype in time?"
- **Language:** UK English throughout code comments, commit messages, and docs. No em-dashes (author preference).
- **First person plural ("we") in documentation.** Not "I".

## Stack (locked)

- Backend: Python 3.11+, FastAPI, SQLite, SQLAlchemy 2.0, Pydantic v2
- Frontend: React 18, Vite, TypeScript, Tailwind or CSS Modules (decide after Figma inspection)
- SMS: local Python mock module; no Twilio, no external SMS provider
- Testing: pytest (backend), Vitest (frontend)
- Deployment: local demo only

## Design source

Figma design system exists (professionally designed, supervisor-approved). Use the Figma MCP integration to pull component specs directly. Do not redesign. If a Figma component is ambiguous, ask the user; do not invent.

## Architecture principles

- **Middle-layer.** Backend is the single source of truth. PWA and SMS both call the same HTTP API. No business logic in the frontend.
- **Search-first.** The core user need is "which pharmacy nearby has drug X in stock". Everything else is scaffolding.
- **Walking-distance ranking.** Pharmacy proximity uses walking-realistic distances (not driving-time), per Friesen et al. 2025.
- **Grounded synthetic data.** The synthetic ecosystem's distributions come from the real scan. Document any calibration decision in `data/synthetic/README.md` as it is made.
- **NLP parser is intentionally light.** Catalogue-matching, not a general NLU system. Free-form user query → normalised medication name from a fixed catalogue.

## What to build first (in order)

1. **Backend:** synthetic pharmacy schema (SQLAlchemy models) → seed script → basic FastAPI health endpoint. Commit.
2. **Backend:** medication search endpoint (GET /search?q=... returns ranked pharmacy list with stock). Commit.
3. **Backend:** SMS mock service (accepts a text string, parses it, calls the search service, returns a response string). Commit.
4. **Frontend:** Vite + React + TS scaffold + Figma design system tokens. Commit.
5. **Frontend:** Landing/search page implemented from Figma. Commit.
6. **Frontend:** Results page implemented from Figma. Commit.
7. **Frontend:** Pharmacy detail page implemented from Figma. Commit.
8. **Integration:** wire PWA to backend, end-to-end test. Commit.
9. **Evaluation prep:** DITL scenario scripts, log capture. Commit.

## Commit discipline

- Small, atomic commits. One logical change per commit.
- Conventional commit messages: `feat:`, `fix:`, `docs:`, `test:`, `chore:`, `refactor:`.
- Do not commit synthetic data files larger than 1 MB. Regenerate from seed instead.

## What NOT to do

- Do not add auth or user accounts. Out of MVP scope.
- Do not integrate a real SMS provider. Local mock only.
- Do not add analytics or telemetry. Ethics constraint.
- Do not implement any Figma screen outside the critical path unless explicitly asked.
- Do not spend time on deployment infrastructure. Local demo only.
- Do not add em-dashes to any output.

## Where things live

- `docs/decisions/` — architecture decision records (ADRs), one file per decision
- `docs/evaluation_protocol.md` — DITL protocol (written during eval phase)
- `data/scan/` — anonymised Conakry pharmacy scan (source of grounding)
- `data/synthetic/` — generated synthetic ecosystem (versioned, seeded)
- `scripts/` — dev utilities (seeding, mock SMS CLI)

## Reference to dissertation

- Related Work section is complete in `../Dissertation writing/Afia_Dissertation_v0.1.docx`
- Literature review synthesis in `../Literature review/Lit_Review_Sprint.md`
- Any citation in this codebase should trace back to a paper in those files
