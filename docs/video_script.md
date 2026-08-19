# Presentation Video — script and storyboard

Target: **10 minutes (±10%)**, MP4, submitted via QM+ via EchoVideo.
Deadline: 19 Aug 2026 (same as dissertation, reflective essay, supporting material).

## Rules from QMPlus (must follow)

- Must appear on camera for a **meaningful portion** (intro, transitions,
  conclusion) — not required for full 10 min. Voice-over only during
  demos and screencasts is explicitly allowed (per Claire's forum reply
  to Agnese).
- Can be edited from multiple clips — does not have to be one continuous
  take (per Claire's forum reply to Lukas).
- Cannot read/copy large text from the dissertation paper.
- Cannot speed up the recording.
- Reference the sources cited in the video presentation (final slide
  with references list — per Claire's forum reply to Rohith).
- If using background music: keep volume down so voice stays clear.
- No specific template required, but the QMUL branded PowerPoint
  template is available and downloaded in the `Video presentation`
  folder.

## Materials to have ready before recording

1. **Slides deck** (PowerPoint or Keynote), roughly 8-10 slides:
   - Slide 1: Title (project name, name, student number, supervisor,
     programme, QMUL logo)
   - Slide 2: Problem statement (Guinea, digital-maturity scan finding)
   - Slide 3: Existing approaches and gaps
   - Slide 4: Architecture (the mermaid diagram from README, redrawn as
     a clean figure)
   - Slide 5: Two-track evaluation methodology (brief)
   - Slide 6: Key finding — independently-confirmed themes table
   - Slide 7: DSR "Design as Search Process" evidence — symptom-safety
     branch
   - Slide 8: Contributions recap (three)
   - Slide 9: References (Harvard style, key citations only)
   - Slide 10: Closing/thanks + repo URL
2. **Backend + frontend running** on `localhost:8000` and `localhost:5173`.
3. **Browser tab** pre-loaded on Landing, Kaloum district picker
   already dismissed (denied geolocation, picked Kaloum).
4. **Spare terminal** with venv activated, ready for `python scripts/sms_mock.py "..."` commands.
5. **Recording software** — QuickTime (macOS built-in, simplest) or OBS
   Studio (more control) or Loom (fast).
6. **Room lighting** — user's room light confirmed sufficient. Face the
   light source, not away from it.
7. **Microphone check** — do a 15-second test recording, play back,
   confirm audio is clear.

## Segment plan — edit these together in post

Total target: ~10 minutes. Each segment is a separate take; if any one
fails, only that segment needs re-recording.

### Segment 1 — Face-cam intro (0:00 - 0:30)

**On camera.** No slides.

*Spoken:*

> "Hi, I'm Abdourahamane Besmor BAH, MSc Advanced Computer Science at
> Queen Mary University of London, supervised by Waleed Iqbal. This
> is my project: Afia — a middle-layer pharmaceutical access platform
> for Guinea. Over the next ten minutes I'll walk you through the
> problem it addresses, the design and implementation, the evaluation,
> and the key findings."

**Length: ~25 seconds.**

### Segment 2 — Problem statement (0:30 - 1:30)

**Slide 2 (Problem) with face-cam picture-in-picture in bottom-right corner** OR face-cam only with the slide behind you.

*Spoken:*

> "Guinea faces a critical medication accessibility crisis, linked
> to a broader digitalisation gap. Patients often spend hours going from
> one pharmacy to another, looking for particular products on their prescription.
> A digital-maturity scan of fifteen pharmacies in Guinea's capital,
> Conakry, that I conducted for this project, found that none of them
> currently expose an API or maintain a functional online inventory.
> Only four have any online presence at all, and only one of those
> offers a partial e-commerce interface, with placeholder prices and no
> real stock signals."

**Length: ~50 seconds.**

### Segment 3 — Existing approaches and gaps (1:30 - 2:15)

**Slide 3 (Gaps) with voice-over.** No face.

*Spoken:*

> "Existing approaches don't fit this context. Pharmacy inventory
> systems are heterogeneous and often entirely offline, while many
> users lack reliable internet access, which rules out smartphone-only
> solutions. No prior work in the literature applies SMS to
> consumer-facing medication availability search, and the West African
> urban setting is underrepresented in the existing SMS mHealth
> evidence base. This is the gap Afia addresses."

**Length: ~40 seconds.**

### Segment 4 — Approach overview (2:15 - 3:00)

**Slide 4 (Architecture diagram) with voice-over.** No face.

*Spoken:*

> "Afia is a middle-layer platform. It couples a Progressive Web App
> for smartphone users with an SMS interface for users on basic mobile
> phones, over a shared FastAPI backend. The backend is the single
> source of truth: both channels call the same HTTP API. This makes the platform
> deployable today via a grounded synthetic pharmacy ecosystem,
> extensible to real pharmacy APIs as they emerge. The backend is
> Python 3.11 with FastAPI and SQLite; the PWA is React with TypeScript
> on Vite; the SMS gateway is a local Python mock."

**Length: ~45 seconds.**

### Segment 5 — PWA live demo (3:00 - 6:00)

**Screen recording of the browser with voice-over.** No face during
this segment (the demo is the star).

**Viewport choice**: try Android Studio emulator first (open Chrome
inside the emulator, navigate to `http://10.0.2.2:5173` — that's how
the Android emulator reaches the host machine's `localhost:5173`).
15-minute timebox on emulator setup; if it drags past that, fall
back to Chrome DevTools mobile viewport (`Cmd+Opt+M` in Chrome — one
click, no setup, visually 90 percent as good).

*Actions and matching voice-over:*

- (00:20) **Deny geolocation on Landing.** When browser prompts for
  location, click Block.
  > "First, I'll deny the geolocation permission. Many users in
  > Conakry either don't have location enabled or don't grant it.
  > The app falls back to a district picker, so I select Kaloum
  > manually. The platform is designed to work in this constrained
  > context by default, not as a workaround."

- (00:15) **Landing page.** Type `doli` in the search bar slowly.
  > "Users search by the name they read on their prescription. Reviewer 1
  > from my evaluation noted that Guinean patients look for the
  > commercial name, so when I type 'doli' the autocomplete shows
  > 'Doliprane' as the primary label, with the underlying molecule,
  > paracetamol, as secondary context."

- (00:20) **Pick a suggestion.** Dose picker preselects.
  > "The row I picked has a specific strength, so the dose picker
  > preselects it — 500 milligrams. No extra click needed to search."

- (00:15) **Click Rechercher.** Results list appears.
  > "The results are ordered by a walking-realistic distance, in-stock
  > quantity, and a trust score derived from each pharmacy's
  > digital-maturity tier — 60 percent, 20 percent, 20 percent
  > respectively."

- (00:20) **Point at a pharmacy card.** Show the OUVERTE pill, price,
  distance, on-call badge.
  > "Each card shows whether the pharmacy is currently open, its price
  > in Guinean Francs, distance to the user, and whether it's on-call
  > for after-hours access."

- (00:20) **Toggle Maps.** Show walking-radius zoom.
  > "Toggling to the map view centres on the user at street-level zoom
  > — a walking-radius view, per Reviewer 1's feedback. Pins for
  > further pharmacies are reachable by zooming out."

- (00:20) **Click a pin.** Popover with phone number, price, En stock.
  > "Clicking a pin surfaces a popover with the pharmacy's contact
  > number, current stock status, and a tap-to-call phone link."

- (00:25) **Click the Directions button** on the popover. Opens
  OpenStreetMap walking-directions in a new tab.
  > "The directions button opens OpenStreetMap in a new tab, pre-
  > populated with a walking route from my current position to the
  > selected pharmacy. This uses the same walking-realistic distance
  > model that drives the ranking, ensuring internal consistency
  > between how we score results and how we route to them."

- (00:15) **Click voir la pharmacie.** Detail page opens on Médicaments tab.
  > "Opening the detail page lands on the Médicaments tab by default,
  > since the user came from a medication search. The brand name they
  > searched — Doliprane — leads, with paracetamol as secondary
  > context."

- (00:15) **Point at the Détail top strip.** Show "Pour: Doliprane, 500 mg".
  > "The full brand-first context carries through the interface end to
  > end."

**Length: ~2:40 (aim for 3 min max).**

### Segment 6 — SMS live demo (6:00 - 7:15) - ✅

**Terminal recording** with voice-over, no face. Split screen with
browser optional.

*Actions and matching voice-over:*

- Run: `python scripts/sms_mock.py "paracetamol 500mg"`
  > "The SMS channel uses the same backend as the Progressive Web App. Sending a bare medication and dose, here Paracetamol 500mg, returns the top three pharmacies, with stock, price and distance from the Conakry centroid. The result is in French".

- Run: `python scripts/sms_mock.py "paracetamol 500mg kaloum"`
  > "Since feature-phone SMS doesn't carry device location, users can
  > append a district name. Watch what happens when I add 'kaloum', Conakry's city-centre district. the Kaloum pharmacy jumps from third to first, and every distance updates, because the search is now anchored to the Kaloum centroid instead of the default Conakry centre."

- Run: `python scripts/sms_mock.py "j'ai mal à la tête"`
  > "J'ai mal à la tête means I have a headache. This is the most consequential design decision the evaluation
  > surfaced. If the query is symptom-shaped rather than
  > medication-shaped, the platform refuses to suggest a drug and
  > directs the user to a doctor or pharmacist. This branch was
  > introduced in direct response to a pregnancy-safety concern raised
  > by Reviewer 1, and independently endorsed by Reviewer 2 as
  > clinically appropriate. It's an ethical property of the artefact
  > that the DITL methodology surfaced."

- Run: `python scripts/sms_mock.py "zoloft"`
  > "For a brand not in the catalogue, the fallback is also in French, gently redirecting the user to check the spelling."

**Length: ~1:15.**

### Segment 7 — Evaluation methodology (7:15 - 8:00)

**Slide 5 (Two-track methodology) with voice-over.** No face.

*Spoken:*

> "The platform is evaluated under a two-track Design Science Research
> methodology. Track A is Doctor-in-the-Loop: two qualified medical
> professionals, referred to as Reviewer 1 and Reviewer 2, each spent
> an hour and half in average, walking through six scripted scenarios on
> the platform. Track B is a scripted headless harness that runs the
> same six scenarios against the seeded ecosystem and dumps
> deterministic JSON output. Together, Track A and Track B cover the
> qualitative and quantitative dimensions Hevner's design evaluation
> guideline calls for."

**Length: ~45 seconds.**

### Segment 8 — Key finding (8:00 - 9:00)

**Slide 6 (Confirmed themes table) with face-cam picture-in-picture** for the first sentence, then voice-over for the rest.

*Spoken:*

> "Both reviewers endorsed the platform's usability without
> qualification. Reviewer 2's exact phrase was 'oui sans équivoque' —
> unequivocally yes. Five themes were independently confirmed across
> both sessions, including brand-first shopping behaviour, the
> walkaway risk when a search returns no result, the appreciation of
> the symptom-safety refusal, the design failure of non-functional
> filter controls, and the effectiveness of the dose preselection
> introduced after Reviewer 1's session. Independent confirmation
> across two professionals is the strongest qualitative signal a DITL
> evaluation at this scale can produce."

**Length: ~55 seconds.**

### Segment 9 — Contributions recap (9:00 - 9:40)

**Slide 8 (Contributions) with face-cam picture-in-picture.**

*Spoken:*

> "The project contributes three substantive outputs. First, an
> empirical characterisation of pharmacy digital maturity in Conakry,
> based on the fifteen-pharmacy scan — the first documented at this
> granularity for this market. Second, a middle-layer platform
> architecture for markets where digital maturity is near zero.
> Third, a grounded synthetic evaluation approach for a Conakry
> pharmacy ecosystem, designed to be replaced by real data in a future
> deployment without changes to the evaluation pipeline."

**Length: ~40 seconds.**

### Segment 10 — Face-cam close (9:40 - 9:55)

**On camera.**

*Spoken:*

> "The full code and dissertation are available on GitHub. Thank you
> for watching."

**Length: ~15 seconds.**

### Segment 11 — References slide (9:55 - 10:00)

**Static slide** with the ~5 most-cited references (Friesen et al. 2025;
Hevner et al. 2004; Agarwal et al. 2020; Osorio-Marulanda et al. 2024;
Tharumia Jagadeesan and Wirtz 2021). No voice-over needed — this is
compliance with Claire's forum guidance that video presentations should
reference their cited sources.

**Length: ~5 seconds.**

## Recording sequence tonight

Do them in this order (easiest and lowest-risk first):

1. **Terminal SMS commands (Segment 6)** — no face, no slides, purely
   command line. Fastest to nail. If you get a good take: bank it.
2. **PWA demo (Segment 5)** — screencast only, no face. Second easiest.
3. **Slide voice-overs (Segments 3, 4, 7)** — no face, just narration
   over static slides. Third.
4. **Face-cam intro + close (Segments 1, 10)** — face required. Do when
   you feel photogenic.
5. **Face-cam picture-in-picture segments (2, 8, 9)** — most complex
   setup. Last.

## Editing (Tuesday morning)

- **Tool**: iMovie (Mac) is fastest, or QuickTime for basic trimming, or
  Shotcut/OpenShot if you want more control.
- **Rough cuts first**: assemble segments in order, don't obsess over
  transitions.
- **Voice consistency**: if one segment sounds louder or softer than the
  others, normalise levels in the editor.
- **Simple transitions**: hard cuts or short cross-dissolves. No fancy
  effects.
- **Length check**: total between 9:00 and 11:00 (10 min ±10%). If over,
  trim the demo segments first — they're the easiest to compress
  without losing content.
- **Export**: MP4, 1080p, aim for under 500 MB (EchoVideo upload
  handles it, but smaller = faster).

## Uploading

- Upload to **EchoVideo** first (allow processing time).
- Then submit via QM+ using "Existing Video" — do NOT change any
  sharing settings, submission automatically grants examiner access
  (per Claire's forum reply to Asli).
- Do NOT try to upload 5 minutes before deadline. Processing time is
  real.

## What to skip if time is short tonight

If it's 01:30 and you don't have all segments recorded:

- **Priority 1 (must land tonight to save Tuesday)**: Segments 5 (PWA
  demo) and 6 (SMS demo). These are the longest and hardest to redo.
- **Priority 2 (can slip to Tuesday morning)**: Segments 1, 2, 10
  (face-cam pieces) — quick to redo fresh.
- **Priority 3 (fastest to add Tuesday)**: Segments 3, 4, 7, 9, 11
  (slide voice-overs) — just needs a mic and slides.

## Success criteria for tonight

Not "video is done", just "won't be starting from zero tomorrow":

- [ ] Storyboard read through and adjusted to your taste
- [ ] Slides deck built (using the QMUL PowerPoint template already downloaded)
- [ ] Recording software chosen, tested, mic level checked
- [ ] At least Segments 5 and 6 (PWA + SMS demos) recorded and saved
- [ ] Rough face-cam intro (Segment 1) recorded

Anything beyond that is bonus.
