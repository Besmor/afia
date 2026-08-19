# Figma Inspection — 2026-08-08

**File:** Projet AFIA 🌐 MVP (`od3Y2imwIHNxUCHErcIA0w`)

## ⚠️ Blocker: Figma MCP tool-call limit reached mid-inspection

The Figma account connected to this workspace is on a **Starter** plan. Figma's
published rate-limit table caps Starter access at a small number of MCP tool
calls per month regardless of seat type, and we hit that ceiling partway
through this inspection (`get_design_context` began returning: "You've reached
the Figma MCP tool call limit on the Starter plan. Upgrade your plan for more
tool calls."). Retrying did not help; this is a hard monthly quota, not a
transient error.

**Practical effect:** the Design System tokens and the first three screens
below are fully inspected. Screens 4 to 11 (dose picker through the maps
popup) were **not reached** and contain no invented content, per the
"ask, do not invent" rule for Figma work.

**Options to unblock, ranked:**
1. Upgrade the Figma seat/plan to Professional or above (Dev/Full seat gets
   200 calls/day, 15/min) — fastest path given the 19 Aug deadline.
2. Wait for the monthly quota to reset (unknown reset date; not worth betting
   the timeline on it).
3. Have the designer export the remaining 8 screens as PNG/PDF plus a shared
   Figma "Inspect" read-only view so we can eyeball layout, spacing and
   colours manually without MCP calls.

Whoever resumes this should re-run the same node IDs listed under each
"NOT INSPECTED" screen below once access is restored, then fold results back
into this file.

---

## Design System

Source node: `🚧 DESIGN System` canvas (`6521:24859`). This canvas is a
full component-library page (buttons, inputs, toasts, tags, avatars, sliders,
maps, etc.) rather than a single frame, so it could not be pulled in one call;
it was inspected via its `Color` (`6720:4825`) and `Text` → `Typography`
(`6722:5008`) sub-frames plus a sample of individual components (`Button`,
`Search Bar`, `Text Field`, `List Item`, `Toast`, `Tag`).

### Colours

| Token | Hex | Usage notes |
|---|---|---|
| Gray_02 / 10 | `#FFFFFF` | White, base surface |
| Gray_02 / 20 | `#F5F5F5` | |
| Gray_02 / 30 | `#EDEDED` | Default border colour on cards, search bar, list items |
| Gray_02 / 40 | `#E0E0E0` | |
| Gray_02 / 50 | `#C2C2C2` | Placeholder text, inactive border |
| Gray_02 / 60 | `#9E9E9E` | Inactive tab-pill text |
| Gray_02 / 70 | `#757575` | Inactive nav-bar label |
| Gray_02 / 80 | `#616161` | Secondary body text |
| Gray_02 / 90 | `#424242` | |
| Gray_02 / 100 | `#0A0A0A` | Primary text / home indicator |
| Background 01 | `#ECFDE7` | Design-system doc background tint (not seen yet on app screens) |
| Main color | `#24A70E` | Labelled "Vert foncé / vert santé" |
| Main red | `#D80027` | |
| Main red 2 | `#E74551` | |
| Primary 01 | `#46C12D` | Primary button fill (labelled "Vert menthe vif" swatch is Primary/accent-01 `#91F265`, not this one — see ambiguity below) |
| Primary 02 | `#1FA60F` | Active nav-bar icon/label, secondary-button border+text |
| Secondary 01 | `#C8DFB8` | |
| Secondary 02 | `#DAFBCD` | |
| Secondary 03 | `#67B44B` | Design-system doc-page header background (meta, not app UI) |
| Secondary 04 | `#589A40` | "Trouvez vos médicaments" heading colour |
| Secondary 05 | `#3D6B2B` | |
| Secondary 06 | `#185E02` | Design-system doc-page icon chip background (meta, not app UI) |
| Accent color | `#007AFF` | |
| Accent color 01 | `#91F265` | Labelled "Vert menthe vif" |
| Accent color 02 | `#A9F4F4` | |
| Accent color 022 | `#E1F5F5` | |
| Accent color 03 | `#25C4C4` | |
| Accent color 04 | `#FFB2B2` | |
| Accent color 05 | `#FFC20F` | |
| Primary / main (semantic) | `#5E47D2` | Purple — semantic "Primary" system colour, distinct from brand Primary 01/02 above. Likely inherited from a generic UI kit and unused in the Afia screens seen so far |
| Danger / main | `#A82525` | Used for form validation error border/text (Text Field component) |
| Warning / main | `#E0CE2C` | |
| Info / main | `#0023DD` | |
| Success / main | `#21725E` | |
| (+Secondary/Hover/Focus/Pressed/Border variants for each of Primary/Danger/Warning/Info/Success) | see raw variable dump | Full state-colour ramps exist but no app screen exercises them yet |

**Variable also present:** `spacing/sm` = `8` (px) — the only named spacing
token found; see Spacing section below.

### Typography

The design-system "Text" page documents one type scale, but the actual app
screens (Accueil, Recherche, Recherche-Sélection) use **different font
families entirely**. Both are recorded here — see Ambiguities.

**Documented type scale** (`Text` → `Typography`, node `6722:5008`), all
line-height 1.4, letter-spacing 0 unless noted:

| Style | Family | Size | Weight |
|---|---|---|---|
| H1 | Inter | 48 | 400 (Bold variant 700) |
| H2 | Inter | 40 | 400 (Bold variant 700) |
| H3 | Inter | 33 | 400 (Bold variant 700) |
| H4 | Inter | 28 | 400 (Bold variant 700) |
| H5 | Inter | 23 | 400 (Bold variant 700) |
| Title1 | Inter | 19 | 400 (Bold variant 700) |
| Title2 | Inter | 16 | 400 (Bold variant 700) |
| Body | Inter | 13 | 500 (Medium) |
| Caption | Roboto | 11 | 600 (SemiBold) |

Component-doc meta labels (headers, "how to use" callouts inside the
component-library pages themselves) additionally use Inter Regular/SemiBold/
Bold/Black at 8–24px — this is design-system documentation chrome, not
app UI, and should not be ported to code.

**Fonts actually used on app screens (Accueil / Recherche / Recherche-
Sélection):**

| Family | Weight/style seen | Size(s) | Usage |
|---|---|---|---|
| Baloo Tamma | Regular | 32px, 20px, 15px | Page heading ("Trouvez vos médicaments"), primary button label |
| Manrope | Bold, SemiBold, Medium, ExtraBold | 11–16px | Nav-bar labels, search input text/placeholder, list rows, quantity labels |
| Inter | Regular | 17px | iOS status-bar clock only (not real content) |

### Spacing

No dedicated "Spacing" token page exists in the design system. Only one
named spacing variable was found: `spacing/sm = 8px`. All other spacing is
ad hoc per component. Observed values across Button, Search Bar, Text Field,
List Item, Toast, Tag and the Accueil/Recherche screens, roughly forming an
8px-ish scale:

`2, 4, 6, 8, 10, 12, 14, 16, 20, 22, 24, 28, 32, 35px` (gaps and padding)

Recommend adopting an 8pt-based scale (4/8/12/16/20/24/32) for implementation
and treating odd values (6, 10, 14, 22) as component-specific exceptions
rather than new scale steps.

### Radii and shadows

No shadow/elevation tokens or effect styles were found anywhere inspected
(Color frame, Typography frame, or any of the six components sampled). Flat
design, no drop shadows observed on cards, buttons, or toasts.

Radii observed (no named tokens; values baked into each component):

- `12px` — text field input border
- `16px` — cards, list items, toast, "how to use" doc chips
- `18.413px` — colour-swatch cards in the design-system Color page (documentation only, not app UI)
- `24px` — primary/secondary buttons, search bar, dose/unit segmented inputs
- `200px` — filter/tag pills (fully rounded)
- `400px` — icon-only circular buttons (history button, back button, filter button)

### Other variables

- `tone [day]/900`, `absolute/1000` = `#000000` — seen referenced on Accueil/
  Recherche but not used visibly (likely shadow or overlay colours reserved
  for a dark-mode or modal treatment not yet exercised on these screens).
- No spacing/radius/shadow "collections" exist as Figma Variables — everything
  found was either a colour variable or a hand-set pixel value in the layer.

---

## Screen: 1. Accueil (Home)

- **Node ID:** `5886:1633`
- **Dimensions:** 393 × 852 (iPhone-class mobile viewport)
- **Layout description:** Status bar (mock, `BaseStatusBar`, backdrop-blur) → decorative background blob image (full-bleed, low z-index) → header row (Afia wordmark + logo mark, "Accueil" page label, circular history button, top ~y80) → large centred heading "Trouvez vos médicaments" (Baloo Tamma 32px, `#589A40`) → search input pill (placeholder "Quel médicaments recherchez-vous") → primary CTA button "Rechercher" (full-width pill, `#46C12D`) → bottom tab bar (Navigation-bar, 4 items) with iOS home-indicator bar.
- **Components used:** `BaseStatusBar`, background illustration (SVG), header (`Afia` wordmark + `Logo`), circular icon button (`ClockCounterClockwise`), search input (pill, disabled/placeholder state), primary `Button`, `Navigation-bar` (House/MagnifyingGlass/Ticket/User tabs), `Home Indicator`.
- **Notable states / interactions:** Nav bar shows "Accueil" as the active tab (green icon+label, `#1FA60F`/Manrope Bold); other three tabs are inactive (`#757575`/Manrope Medium). Search input is a static/placeholder pill here, not an active text field — tapping it presumably routes to screen 2 (Recherche). History button top-right has no visible active state captured.
- **Design tokens referenced:** `Background 01 #ECFDE7`, `Primary/Primary02 #1FA60F`, `Primary/Primary 01 #46C12D`, `Secondary/Secondary 04 #589A40`, `Gray_02/30 #EDEDED` (input border), `Gray_02/50 #C2C2C2` (placeholder text), `Gray_02/70 #757575` (inactive tab), `accent color/accent-color 01 #91F265` (present in variable set, not visibly used on this screen).

## Screen: 2. Recherche (Search entry)

- **Node ID:** `5886:2009`
- **Status: NOT FULLY INSPECTED** — the Figma MCP rate limit was hit before
  the layout/component call (`get_design_context`) returned; only the colour
  variables referenced by this node were retrieved before the block.
- **Design tokens referenced (confirmed):** `Background 01 #ECFDE7`,
  `Primary/Primary02 #1FA60F`, `Primary/Primary 01 #46C12D`,
  `Secondary/Secondary 04 #589A40`, `Gray_02` ramp (10/20/30/50/60/70/80/90/100),
  `accent color/accent-color 01 #91F265`. This palette is identical to screen
  1's, suggesting a close visual continuation of the home screen (consistent
  with "search entry" being a lightly-modified Accueil).
- **Everything else (dimensions, layout, component hierarchy, states) is
  outstanding.** Re-run `get_design_context` (and ideally `get_screenshot`)
  on `5886:2009` once Figma access is restored.

## Screen: 3. Recherche - Selection (Search autocomplete)

- **Node ID:** `5886:2066`
- **Dimensions:** 393 × 852
- **Layout description:** Same shell as screens 1–2 (status bar, background
  blob, heading "Trouvez vos médicaments", bottom nav bar with home
  indicator). Below the heading: a filled search input showing the query
  already entered ("adderall (générique)") with a grey border (`#C2C2C2`,
  i.e. focused/filled state vs. screen 1's neutral `#EDEDED` border). Below
  that, a white card (rounded 24px, border `#F5F5F5`) listing **4 repeated
  rows**, each with a Pill icon, two-line label ("**Un** adderall
  (générique)" / "Ou **une** pilule"), and a Check icon on the first row
  only. A full-width primary "Rechercher" button sits below the card.
- **Components used:** search input (filled state), selection-list card,
  repeated list row (`Pill` icon + two-line Manrope label + optional `Check`
  icon), primary `Button`, `Navigation-bar`, header, status bar.
- **Notable states / interactions:** This is **not a free-text autocomplete
  dropdown** as the screen name implies — it reads as a **unit/quantity
  clarifier** ("one tablet" vs "one pill", i.e. disambiguating dosage form),
  with the first option pre-selected (Check icon visible only on row 1). All
  four rows currently render identical placeholder copy, which reads like
  unfinished prototype content rather than 4 distinct real options — flagged
  below as an ambiguity to raise with the designer.
- **Design tokens referenced:** same palette as screens 1–2, plus no new
  colours. Fonts: Baloo Tamma 32px/20px (heading/button), Manrope
  SemiBold/ExtraBold 11–14px (input text, list rows).

## Screen: 4. Recherche - Selection - Dose (Dose picker)

- **Node ID:** `5886:2123`
- **Status: NOT INSPECTED** — blocked by the Figma MCP rate limit before this
  node was reached. No layout, component, colour, or typography data
  gathered. Re-run once access is restored.

## Screen: 5. Vue Liste - Résultats des recherches

- **Node ID:** `5886:2174`
- **Status: NOT INSPECTED** — same blocker. This is a critical screen (the
  results list is the core "which pharmacy has drug X" view) — prioritise
  re-inspecting this one first once quota resets.

## Screen: 6. Vue Liste - Résultats - filters popup

- **Node ID:** `6460:12359`
- **Status: NOT INSPECTED** — same blocker.

## Screen: 7. Vue Maps - Résultats des recherches

- **Node ID:** `5886:2595`
- **Status: NOT INSPECTED** — same blocker. Note for later: we already know
  (from `docs/decisions` context) that pharmacy proximity uses
  walking-distance ranking (Friesen et al. 2025) — check whether the map
  screen's pin/list affordances match that framing once inspected.

## Screen: 8. Vue Maps - Pharmacie sélectionnée

- **Node ID:** `5886:2673`
- **Status: NOT INSPECTED** — same blocker.

## Screen: 9. Détails pharmacie - médicaments

- **Node ID:** `5886:2733`
- **Status: NOT INSPECTED** — same blocker.

## Screen: 10. Détails pharmacie - Info générales

- **Node ID:** `5886:2865`
- **Status: NOT INSPECTED** — same blocker.

## Screen: 11. Détails pharmacie - Maps popup

- **Node ID:** `5887:4714`
- **Status: NOT INSPECTED** — same blocker. This is the MVP flow's exit
  point (hands off to an external map app), so its scope should be small —
  worth confirming that assumption once inspected, since it affects whether
  we need any map-SDK deep-linking logic at all.

---

## Cross-screen observations

*(Based only on the 3 screens actually inspected — Accueil, Recherche,
Recherche-Sélection. Revisit this section once screens 4–11 are inspected;
patterns below may well extend to the rest of the flow.)*

- **Reused components across screens:** `BaseStatusBar`, background blob
  illustration, header (Afia wordmark + logo + page label + circular history
  button), `Navigation-bar` (bottom tab bar, 4 items), primary `Button`
  ("Rechercher" pill), search input pill, `Home Indicator`. All three
  inspected screens share the exact same shell — only the content between
  the heading and the button changes.
- **Recurring patterns:**
  - Same page heading ("Trouvez vos médicaments", Baloo Tamma 32px,
    `#589A40`) repeats verbatim across screens 1–3, even though screens 2–3
    represent different steps in the flow. Worth confirming this is
    intentional (a persistent flow title) vs. placeholder copy left over
    from duplicating frames.
  - Search input border colour toggles between `#EDEDED` (neutral/empty,
    screen 1) and `#C2C2C2` (filled/focused, screen 3) — this is the only
    interactive-state signal seen so far.
  - Nav bar active-tab colour (`#1FA60F` + Manrope Bold) vs inactive
    (`#757575` + Manrope Medium) is consistent everywhere.
- **Component-library candidates (3+ occurrences):** `Button` (primary
  pill), search input pill, circular icon button (`rounded-[400px]`, used
  for history/back/filter icons), list-row card (`rounded-[16px]`, border
  `#EDEDED`, icon + label + trailing icon — seen in both the design-system
  `List Item` component and screen 3's selection rows), `Navigation-bar`.
- **Ambiguities or things worth clarifying with the designer:**
  1. **Two incompatible font systems.** The design-system "Text" page
     specifies Inter/Roboto as the type scale, but every real screen uses
     Manrope (body/UI text) and Baloo Tamma (headings/buttons) instead. We
     will implement using the fonts actually seen on screens (Manrope +
     Baloo Tamma), not the documented Inter/Roboto scale, but this should be
     confirmed with the designer — the Typography page may simply be stale.
  2. **"Primary 01" vs the swatch labelled "Vert menthe vif".** The named
     token `Primary/Primary 01 = #46C12D` is used for the button fill, but
     the large colour-swatch card labelled "Vert menthe vif" (mint green) in
     the Color page is actually `#91F265` (`accent-color 01`), not
     `#46C12D`. The token *names* and the *swatch labels* don't line up
     one-to-one — treat the raw hex values as ground truth, not the label
     text, until clarified.
  3. **Screen 3's content looks unfinished.** All four rows in the
     "selection" list render identical text ("Un adderall (générique) / Ou
     une pilule") — likely placeholder/duplicate-frame content rather than
     4 real distinct options. Confirm intended real content before building.
  4. **Screen 3 doesn't match its name.** "Recherche - Selection (Search
     autocomplete)" implies a text-matching dropdown of medication names,
     but the actual content is a dosage-form/quantity clarifier. Confirm
     where the *actual* autocomplete-matching UI lives in the flow (it may
     be screen 2, which we couldn't inspect).
  5. Several full semantic colour ramps (Primary/Danger/Warning/Info/Success
     × main/Secondary/Hover/Focus/Pressed/Border) exist in the design system
     but are not exercised by any screen inspected so far — likely inherited
     from a generic starter UI kit rather than Afia-specific. Don't assume
     these need implementing unless a later screen actually uses them.

---

## Missing states (author will invent during implementation)

The designer did not create dedicated frames for these; per the task brief,
we will invent minimal French placeholders during implementation rather than
waiting on design:

- **No results found** (list view): *"Aucune pharmacie trouvée pour ce médicament à proximité. Essayez un autre nom ou élargissez votre recherche."*
- **Location permission denied** (landing): *"Nous avons besoin de votre position pour trouver les pharmacies les plus proches. Veuillez autoriser l'accès à la localisation dans les réglages."*
- **Network / API error:** *"Impossible de se connecter au serveur. Vérifiez votre connexion et réessayez."*
- **Empty search query** (submit with nothing typed): *"Veuillez indiquer le nom d'un médicament pour lancer la recherche."*

These should reuse the `Toast` component's "Error"/"Warning" variants
(`#FFDEDE` / `#FFF4E4` backgrounds, `#1F2024` title text, Manrope
ExtraBold/Medium) already documented in the design system, keeping visual
consistency even though no designer-authored frame exists for them.

---

## Recommended next steps for FT-5 and FT-6

1. **Resolve the Figma access blocker first** (see top of document) — screens
   4–11 are unseen, and screen 5 (results list) in particular is the core
   product surface. Building the results page from screenshots/memory of the
   Figma design without re-inspecting it would violate the "do not invent"
   rule.
2. **Component build order**, based on what's confirmed reused 3+ times
   already (Accueil/Recherche/Recherche-Sélection alone): `Button` (primary
   pill variant only — Secondary/Terciary not seen on real screens yet),
   search input pill, circular icon button, `Navigation-bar`, page header
   (wordmark + logo + title + history button), status bar mock (likely skip
   entirely in the PWA — a real browser has its own status bar; do not
   reproduce it as UI).
3. **Tailwind vs CSS Modules:** the design system has no formal spacing/
   radius/shadow token collection (see Design System → Spacing/Radii above)
   — everything is a hand-set pixel value per component, and the exported
   reference code is already Tailwind-based (arbitrary-value classes like
   `rounded-[24px]`, `px-[12px]`). Given the project brief leaves the choice open
   "after Figma inspection": **recommend Tailwind**. It maps almost
   1:1 onto the arbitrary pixel values Figma exports, avoids hand-rolling a
   token system the design doesn't actually have, and every MCP-returned
   snippet so far is already in this format, minimising translation effort
   under the 19 Aug deadline.
4. **Fonts to install:** Manrope and Baloo Tamma (Google Fonts, both have
   open licences) are the two fonts actually used on real screens — prioritise
   wiring these up over the documented-but-unused Inter/Roboto scale.
5. **Images/SVGs needing export to `frontend/public/`:** from screens 1–3
   alone: Afia wordmark SVG, logo mark SVG (+ inner "Frame13" detail), the
   full-bleed decorative background blob SVG (appears on all 3 screens,
   likely a shared asset), and icon set (House, MagnifyingGlass, Ticket,
   User, ClockCounterClockwise, Pill, Check) — all currently only reachable
   via short-lived (~7 day) Figma asset URLs, so they must be downloaded
   before those links expire, not linked directly. Re-run this step for
   whatever additional icons/images turn up once screens 4–11 are inspected.
