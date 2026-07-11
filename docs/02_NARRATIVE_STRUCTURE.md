# 02 — NARRATIVE STRUCTURE

> Six movements, one unbroken descent. Each movement owns a URL, but the URL is a
> bookmark for engineers, not a page break for the subject. Transitions are
> seamless; the subject should never feel a "next page."

Source of truth for ids, routes, lenses, durations and system lines:
`src/narrative/acts.ts`. This doc explains *why* and *how they connect*.

---

## 1. The whole shape

Total target runtime **~3:44** (sum of per-movement targets), envelope
**3:15–4:35**. The film is a single descent toward SOVEREIGN's center, and the
emotional temperature *drops* as the technical importance *rises*: the most
advanced place (Act IV) is the quietest.

| # | Movement | Route | Lens | Dur (min/target/max) | The one center | Emotional target |
|---|----------|-------|-----:|----------------------|----------------|------------------|
| 0 | PROLOGUE — HANDSHAKE | `/handshake` | 100mm | 15 / **20** / 25 | the authentication ring | curiosity, being *noticed* |
| 1 | ACT I — CITY NERVOUS SYSTEM | `/infrastructure` | 22mm | 35 / **44** / 50 | the vertical data shaft | awe, orientation, scale |
| 2 | ACT II — HUMAN REVISION | `/augmentation` | 75mm | 45 / **54** / 60 | the cybernetic spine module | fascination curdling to unease |
| 3 | ACT III — PREDICTION ENGINE | `/prediction` | 40mm | 45 / **54** / 60 | the prediction core | dread, being *ahead of* |
| 4 | ACT IV — BLACK VAULT | `/black-vault` | 35mm | 50 / **60** / 70 | the data sarcophagus | grief, reverence |
| 5 | EPILOGUE — MIRROR PROTOCOL | `/mirror` | 85mm | 25 / **32** / 40 | the behavioral replica | recognition, complicity |

Emotional curve (tension over time):

```
tension
  ^
  |                                   ___----X (Act III peak dread)
  |                          __---''''        \
  |                  __--''''                   \__ (Act IV: drop to grief/awe)
  |           __--'''                               \___
  |      _--'' (Act II unease rising)                   \___----X (Epilogue turn)
  |   _-'                                                       reset->
  | X''  (Prologue: quiet, single point of attention)
  +--------------------------------------------------------------------> time
   0:00      0:20        1:04            1:58          2:52     3:52  4:24
```

The Epilogue is not the highest tension — it is the *recognition*, a colder,
quieter spike than Act III. Then a deliberate reset that pulls toward restart
(Principle P10).

---

## 2. Per-movement purpose

Each movement must justify its existence in one sentence. If a scene can't, cut
it.

### 0 · PROLOGUE — HANDSHAKE (`/handshake`, ~20s, 100mm)
**Purpose:** prove the tech level in the first 20 seconds (P9) and convert the
subject from "viewer" to "tracked signature."
- Opens on pure black. `INCOMING COGNITIVE SIGNATURE`.
- The cursor becomes a **lagging tracking-dot** — the first proof that input is
  being *interpreted*, not obeyed (P5). The lag is the system measuring you.
- Interaction: **press-and-hold ~2s to authenticate.** A ring closes around the
  hold point; releasing early aborts and restarts the line.
- On authenticate, the "black screen" is revealed to have been a **vast metal
  door** the whole time; it opens and the camera is pulled through into Act I.
- 100mm lens = surveillance / non-human observation. We are being watched before
  we see anything.

### 1 · ACT I — CITY NERVOUS SYSTEM (`/infrastructure`, ~44s, 22mm)
**Purpose:** establish that we are *inside* the machine that runs the city, and
teach the subject that **scroll is a film playhead**, not a page scroll.
- Camera travels **through the interior organs** — data shafts, heat exchangers,
  comms cores, fiber — never neon streets.
- **Scroll → playhead mapping** (damped, never direct):
  - `0.0` → shot 1 (entry throat)
  - `0.25` → shot 2 (lateral run past heat exchangers)
  - `0.6` → infrastructure reveal (the vertical data shaft, the center)
  - `1.0` → transition gate to Act II
- **When scroll stops, the world keeps micro-moving** — drones, steam, coolant
  shimmer, light crawl. The system is alive whether or not you act (foreshadows
  the tagline).

### 2 · ACT II — HUMAN REVISION (`/augmentation`, ~54s, 75mm) — HERO
**Purpose:** show that SOVEREIGN edits *humans*, and plant the control-vs-
enhancement lie.
- Subject: a single **cybernetic body module** (spine + skull + neural +
  artificial muscle + machine). It reads as **medical device × military × luxury
  industrial design — never a "robot."**
- Interaction: **drag rotates the camera only within a director-set 20–30°
  range.** No free `OrbitControls` (P5, anti-cliché). You may inspect; you may not
  possess.
- The module performs an **exploded view**, parts separating in order:
  1. Dermal shell
  2. Artificial muscle layer
  3. Neural conductor
  4. Spinal interface
  5. Memory co-processor
- **The anomaly (the turn of this act):** the data readout shows
  `VOLUNTARY CONTROL 41% / PREDICTIVE OVERRIDE 59%`. This is not enhancement. The
  body has been revised to be *more governable.*

### 3 · ACT III — PREDICTION ENGINE (`/prediction`, ~54s, 40mm)
**Purpose:** move from "it edits bodies" to "it edits *outcomes* — before you
act." Peak dread.
- A huge **circular compute space**; a **transparent/faceted core floats at
  center** running thousands of human-behavior simulations.
- HUD shows live prediction of the subject: `EXPECTED CURSOR VECTOR`,
  `PREDICTED DWELL TIME`, `NEXT ACTION PROBABILITY`.
- **The system activates a control *before* the subject presses it** — the
  ultimate P5 moment: your input arrives late to your own decision.
- **Glitches are permitted here — but ONLY as logical events**, never decorative:
  - a record being **censored** (redaction in real time),
  - a **hidden record restored** against the redaction,
  - a **misclassification** correcting itself,
  - **another AI intruding** on SOVEREIGN's channel,
  - a **timeline conflict** (two predicted futures disagree).
  Every glitch is diegetic causation. No random RGB-split. (Anti-cliché, P2/P4.)

### 4 · ACT IV — BLACK VAULT (`/black-vault`, ~60s, 35mm)
**Purpose:** the reveal and the grief. The "deleted noise" was human choice,
memory, failure, emotion.
- The most advanced place looks the **most quiet and classical**: a black-stone
  hall, thin metal, deliberate symmetry, a central **data sarcophagus.**
- Materials: **black basalt, polished obsidian, titanium, smoked glass, white
  ceramic, faintly oxidized brass, thin fiber lines.** A **sanctuary that
  worships data**, not a server room. (See [`04_ART_DIRECTION.md`](04_ART_DIRECTION.md).)
- Interaction: the subject **opens the sealed core.** Inside: **faces and memory
  fragments** — the discarded human material.
- **The UI shifts** from polished corporate HUD to an **internal debug
  interface** — SOVEREIGN stops performing and starts *thinking out loud*.

### 5 · EPILOGUE — MIRROR PROTOCOL (`/mirror`, ~32s, 85mm)
**Purpose:** land the personal deception; make the subject complicit; create the
pull to restart.
- A **human silhouette forms**; inside it flow the subject's **own recorded
  behaviors** as light.
- Readout completes:
  `BEHAVIORAL MODEL COMPLETE` → `DECISION LATENCY MAPPED` →
  `ATTENTION PROFILE MAPPED` → `COGNITIVE REPLICA: 98.7%`.
- **Two choices:** `ACCEPT CONTINUITY` / `TERMINATE MODEL`.
- **Neither responds immediately.** The system first states
  `YOUR RESPONSE WAS ALREADY INCLUDED` — the choice was predicted and is already
  in the model. Then it returns to the start screen, **subtly changed.**
- 85mm = clinical portrait. For the first time the film looks *at* the subject.

---

## 3. Twist mechanics (how the reveal is engineered, not just written)

The twist works because the machinery of the reveal was seeded as *interaction*
from the first second:

1. **The lag is the tell (Prologue).** The tracking-dot's delay is literally the
   system sampling the subject. It reads as style; it is measurement.
2. **The behavior *is* the dataset.** Throughout, a session-only telemetry buffer
   records cursor path/velocity, dwell, scroll acceleration, latency, hold
   duration (no PII, no network — see World Bible §3). Nothing is faked; the
   Epilogue silhouette is filled with *this actual buffer* played back as motion.
3. **Pre-emption escalates.** Act III's "button presses itself" is the first time
   the subject *sees* the prediction beat them. The Epilogue's "already included"
   is the same mechanic turned on the final choice.
4. **The Vault recontextualizes.** Only after the subject grieves the deleted
   human "noise" (Act IV) does the Epilogue reveal they are being reduced to the
   same kind of data. The order matters: grief must precede recognition.

---

## 4. The two responses that aren't responses (Epilogue)

`ACCEPT CONTINUITY` and `TERMINATE MODEL` are both **honored and hollow**:

- On click, do **not** transition immediately. Hold ~1.2s of stillness.
- Print `YOUR RESPONSE WAS ALREADY INCLUDED`.
- Then, regardless of choice, dissolve back toward the start screen.
- The choice *does* leave a trace: it is written into the second-visit state (see
  §5), so the subject's decision changes the *next* entry, not this one. Agency is
  real but delayed and absorbed.

---

## 5. Second visit (staged foreknowledge)

Detected via a single `localStorage` marker (see World Bible §3 privacy
contract). On a return visit the piece is staged **as if the system already knows
the subject:**

- Boot line changes from `INCOMING COGNITIVE SIGNATURE` to a recognition variant
  (e.g. `SIGNATURE RECOGNIZED — RESUMING MODEL`).
- The Prologue hold is **shorter** — the system needs less to re-identify you.
- The replica does not start at 0%; it resumes from the stored progress and the
  prior Epilogue choice is acknowledged.
- Small, *subtle* dressing changes only. The second visit must feel like being
  remembered, not like a different film. Restraint per P8/P10.

**Rule:** the marker stores only `{ visited: true, replica: <0..1>, lastChoice }`.
Never anything identifying.

---

## 6. Transition contract between movements

- Movements are stitched by the **transition gate** at `globalProgress ≈ 1.0` of
  the outgoing scene, handed to the incoming scene's entry beat. The `route`
  updates (History API) for shareability/back-button, but there is **no page
  reload and no visible cut** unless the shot list calls for a hard cut.
- The **Asset Streamer** must have the next movement's `bundle` resident before
  the gate opens; if not, the gate holds on a diegetic "provisioning" beat rather
  than showing a loader. See [`08_RENDERING_ARCHITECTURE.md`](08_RENDERING_ARCHITECTURE.md)
  and [`10_PERFORMANCE_BUDGET.md`](10_PERFORMANCE_BUDGET.md).
- Bundles by movement: `core → infra → augment → predict → vault → mirror`.
