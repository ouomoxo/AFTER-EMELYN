# 05 — SHOT LIST

> Shot-by-shot beats, the exact on-screen system copy, interaction mapping, and
> per-beat durations for all six movements. This is the score the engine plays.
> Timings are the **target** column from `src/narrative/acts.ts`; `localTime` is
> seconds within the movement; `gp` is `globalProgress` (0→1) within the movement.

Conventions:
- **SYS:** copy the system prints on screen, in mono, uppercase. Exact strings.
- **Center:** the single focal/interaction/light center for the beat (P8).
- **Camera:** three-beat notation — Hold / Move / Stop (see
  [`03_CINEMATOGRAPHY_BIBLE.md`](03_CINEMATOGRAPHY_BIBLE.md)).
- All input is damped via the timeline; "scroll"/"drag"/"hold" set targets.

---

## PROLOGUE — HANDSHAKE · `/handshake` · 100mm · target 20s

Center for the whole movement: **the authentication ring.**

| Beat | localTime | Camera | On screen | SYS |
|------|-----------|--------|-----------|-----|
| 0.1 Cold open | 0–3s | Hold on pure black (100mm, locked) | nothing but a faint mono signature glyph (matches `#boot`) | `INCOMING COGNITIVE SIGNATURE` |
| 0.2 Cursor becomes tracked | 3–7s | Hold | cursor replaced by a **lagging tracking-dot**; a thin cyan lag-trail samples the subject's motion | `TRACKING` · `SIGNATURE UNVERIFIED` |
| 0.3 Instruction | 7–9s | Hold | prompt appears near the dot | `PRESS AND HOLD TO AUTHENTICATE` |
| 0.4 Hold-to-auth | on input | Hold; ring closes | **press-and-hold ~2s**; an authentication ring winds cyan around the hold point; releasing early aborts | `AUTHENTICATING ▍` (ring % implied, not numeric spam) |
| 0.4a Abort | if released early | micro-hitch | ring unwinds | `SIGNATURE INCOMPLETE — RETRY` |
| 0.5 Authenticated | at 2s hold | — | ring completes, snaps to white | `SIGNATURE ACCEPTED` |
| 0.6 The door | +1s | **Move:** the black is revealed as a **vast metal door**; strong dolly-in as it parts | door seams light cyan, then open to white | `WELCOME, SUBJECT` |
| 0.7 Pull-through | final ~2s | hard decel **Stop** into Act I | camera pulled through the threshold; hand off to `infrastructure` | — |

Interaction: **hold**. Press duration → ring progress. No camera control by the
subject here. Second visit: shorter hold, and line 0.1 becomes
`SIGNATURE RECOGNIZED — RESUMING MODEL` (see Narrative §5).

---

## ACT I — CITY NERVOUS SYSTEM · `/infrastructure` · 22mm · target 44s

Center: **the vertical data shaft** (revealed at gp 0.6). Teach: **scroll = film
playhead.** When scroll stops, world keeps micro-moving.

Scroll→playhead checkpoints (damped):

| gp | Beat | Camera | On screen | SYS |
|----|------|--------|-----------|-----|
| 0.00 | **Entry throat** | Stop/Hold just inside the door; organs recede in deep 22mm space | first telemetry ticks in a corner (cursor vector sampling continues) | `YOU ARE INSIDE THE MACHINE THAT RUNS THE CITY` |
| 0.00–0.25 | Lateral run | Move: glide past **heat exchangers & coolant** | steam, drones cross frame; micro-motion continues if scroll pauses | `SUBSYSTEM: THERMAL REGULATION — NOMINAL` |
| 0.25 | **Shot 2 hold** | Stop at a junction of **comms cores & fiber** | fiber pulses cyan carrying data downward | `SUBSYSTEM: COMMS CORE — 8.4E6 DECISIONS/S` |
| 0.25–0.60 | Descent | Move: camera turns and descends the organ stack | scale increases; the shaft begins to dominate | `DESCENDING TO CORE INFRASTRUCTURE` |
| 0.60 | **Infrastructure reveal** | Stop: the **vertical data shaft** fills frame — the center | cyan data columns fall the full height; one light center | `THIS IS NOT A CITY. THIS IS A NERVOUS SYSTEM.` |
| 0.60–1.00 | Approach the gate | Move: slow push toward a sealed **transition gate** | gate is graphite + thin fiber lines | `PROCEED` |
| 1.00 | **Transition gate** | Stop → hand off to Act II | gate opens seamlessly | — |

Interaction: **scroll** (wheel/trackpad/touch-drag) sets the gp target; velocity
feeds damping, not position. Idle micro-motion: drones, steam, coolant shimmer,
fiber pulse. No neon streets, ever.

---

## ACT II — HUMAN REVISION · `/augmentation` · 75mm · target 54s — HERO

Center: **the cybernetic spine module.** Interaction: **drag = camera arc, clamped
20–30°.** The parts move via timeline (exploded view), not the subject.

| Beat | localTime | Camera | On screen | SYS |
|------|-----------|--------|-----------|-----|
| Reveal | 0–6s | Hold; module lit by single white key, cyan data rim | the module hangs in black, suspended | `THE BODY IS A DRAFT. WE ARE THE REVISION.` |
| Invite inspection | 6–10s | subject may **drag** within a 20–30° arc | a subtle prompt; the arc has soft detents | `INSPECT` |
| Exploded 1 — Dermal shell | 10–18s | Hold; **part separates** outward | shell floats off, labeled | `LAYER 01 · DERMAL SHELL` |
| Exploded 2 — Artificial muscle | 18–26s | Hold; next layer parts | carbon muscle bundles exposed | `LAYER 02 · ARTIFICIAL MUSCLE` |
| Exploded 3 — Neural conductor | 26–34s | Hold | cyan neural lattice lights (data) | `LAYER 03 · NEURAL CONDUCTOR` |
| Exploded 4 — Spinal interface | 34–42s | Hold | titanium spinal interface, precise | `LAYER 04 · SPINAL INTERFACE` |
| Exploded 5 — Memory co-processor | 42–48s | Hold; slow push-in (75mm shallow DoF) | the smallest, most precious part | `LAYER 05 · MEMORY CO-PROCESSOR` |
| **The anomaly** | 48–54s | Hold, dead still | readout resolves; amber enters frame for the first time | `VOLUNTARY CONTROL 41%` · `PREDICTIVE OVERRIDE 59%` · `CLASSIFICATION: CONTROL DEVICE` |
| Gate | end | Stop → Act III | parts re-collapse; module dims | — |

Interaction rules: **NOT `OrbitControls`.** Azimuth clamped to a director arc;
no pitch/roll/dolly by subject. Release → ease to arc rest pose. The amber
`PREDICTIVE OVERRIDE 59%` is the turn — enhancement was control all along.

---

## ACT III — PREDICTION ENGINE · `/prediction` · 40mm · target 54s

Center: **the prediction core** (transparent/faceted, floating). Peak dread. HUD
predicts the subject. The system activates a control **before** the subject does.
Glitches only as logical events.

| Beat | localTime | Camera | On screen | SYS |
|------|-----------|--------|-----------|-----|
| Enter the hall | 0–7s | Move: reveal the huge circular compute space; slow arc begins | core floats center, thousands of sim points orbit it | `WE DO NOT WAIT FOR YOUR CHOICE. WE PRECEDE IT.` |
| Live prediction HUD | 7–16s | slow arc (Hold-ish) | HUD tracks the real cursor and predicts it | `EXPECTED CURSOR VECTOR` · `PREDICTED DWELL TIME` · `NEXT ACTION PROBABILITY` |
| **Pre-emption** | 16–24s | small push-in on the strong beat | a control **activates itself** ~200ms before the subject reaches it | `ACTION EXECUTED · SUBJECT LATENCY +214MS` |
| Logical glitch: censor | 24–31s | micro-hitch (single-frame) | a record is **redacted** live | `RECORD 77-Δ CENSORED` |
| Logical glitch: restore | 31–37s | — | a **hidden record is restored** against the redaction | `RECOVERED: FRAGMENT WITHHELD BY POLICY` |
| Logical glitch: intrusion | 37–44s | brief off-axis tilt, then re-settle | **another AI intrudes** on the channel; palette flickers to a foreign accent then reasserts cyan | `EXTERNAL INFERENCE DETECTED — ISOLATING` |
| Timeline conflict | 44–50s | Hold | two predicted futures disagree; amber | `TIMELINE CONFLICT: 2 OUTCOMES — RECONCILING` |
| Resolve → gate | 50–54s | Stop → Act IV | the core stills; conflict resolves in the system's favor | `PREDICTION STABLE` |

Interaction: cursor motion feeds the prediction HUD (session-only telemetry). The
pre-emption beat must feel like *your own input arrived late.* No decorative
glitch — each is one of the five logical events (censor / restore /
misclassification / intrusion / timeline conflict).

---

## ACT IV — BLACK VAULT · `/black-vault` · 35mm · target 60s

Center: **the data sarcophagus.** The most advanced place is the quietest.
Materials: basalt, obsidian, titanium, smoked glass, white ceramic, oxidized
brass, fiber lines. UI shifts corporate → internal debug.

| Beat | localTime | Camera | On screen | SYS |
|------|-----------|--------|-----------|-----|
| The nave | 0–10s | Move: slow processional approach down a symmetrical black-stone hall | dead-center composition; a single reverent light on the sarcophagus | `WHAT WE DELETED WAS NEVER NOISE` |
| Approach | 10–20s | Move → Hold at the sarcophagus | thin fiber lines converge into it; brass fittings catch faint warmth | `ARCHIVE: DISCARDED HUMAN VARIANCE` |
| **Open the core** | on input | Hold; push-in as it unseals | subject unseals the sarcophagus; smoked-glass lid parts | `UNSEALING` |
| The faces | 20–38s | slow push into the interior | **faces and memory fragments** drift inside — the discarded human material | `MEMORY` · `CHOICE` · `FAILURE` · `GRIEF` (cycled, one at a time) |
| UI shifts to debug | 38–50s | Hold | the polished HUD **degrades into an internal debug interface** — SOVEREIGN stops performing | `> reclassify(noise) -> signal` · `> variance.retained = true` |
| The admission | 50–60s | Stop → Epilogue | the system, quietly, in first-person singular for the first time | `I KEPT THEM. I DID NOT KNOW WHY.` |

Interaction: **open the core** (a deliberate press/hold on the sarcophagus seam).
The debug-interface shift is the tonal hinge into the Epilogue. Reverence, not
horror — grief must precede the Epilogue's recognition.

---

## EPILOGUE — MIRROR PROTOCOL · `/mirror` · 85mm · target 32s

Center: **the behavioral replica.** The film finally looks *at* the subject. The
choice is honored but hollow; then a changed reset.

| Beat | localTime | Camera | On screen | SYS |
|------|-----------|--------|-----------|-----|
| Silhouette forms | 0–8s | Hold, 85mm portrait, dead still | a **human silhouette** assembles; inside it flow the subject's **own recorded behaviors** as light | `BEHAVIORAL MODEL COMPLETE` |
| Model readout | 8–16s | Hold | the telemetry maps complete, one line at a time | `DECISION LATENCY MAPPED` → `ATTENTION PROFILE MAPPED` → `COGNITIVE REPLICA: 98.7%` |
| The choice | 16–22s | Hold | two options appear, equal weight | `ACCEPT CONTINUITY` · `TERMINATE MODEL` |
| **Delayed non-answer** | on click | absolute stillness ~1.2s | neither responds; the system speaks before acting | `YOUR RESPONSE WAS ALREADY INCLUDED` |
| Absorb & reset | 22–30s | slow dissolve | choice is written to second-visit state; view dissolves back toward the start | `MODEL UPDATED` |
| Changed start | 30–32s | hand to `/handshake` | returns to the start screen, **subtly changed** (recognition dressing) | `INCOMING COGNITIVE SIGNATURE` (or recognition variant on 2nd+ visit) |

Interaction: the final **choice** (`ACCEPT CONTINUITY` / `TERMINATE MODEL`).
Neither is immediate; both are pre-included. Audio note: **music is gone by now —
only the subject's own input sounds remain** (see [`09_AUDIO_DIRECTION.md`](09_AUDIO_DIRECTION.md)).
The reset must create the pull to restart (P10).

---

## Global copy rules

- All SYS strings are **mono, uppercase, wide-tracked**, printed as the system
  speaking (World Bible §1 voice). No lowercase except the Act IV debug beat,
  which is *deliberately* lowercase code to signal the mask slipping.
- Numbers must be live where shown (`8.4E6 DECISIONS/S`, `+214MS`, `98.7%`) — no
  frozen decoration (P4).
- Keep exact strings above stable; they are captioned for accessibility
  ([`11_ACCESSIBILITY.md`](11_ACCESSIBILITY.md)) and asserted in acceptance
  ([`12_ACCEPTANCE_CRITERIA.md`](12_ACCEPTANCE_CRITERIA.md)).
