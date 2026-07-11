# 03 — CINEMATOGRAPHY BIBLE

> The camera is SOVEREIGN's attention. It is never a free-flying tourist. Every
> move is a decision the system makes about where to look. If a move has no
> narrative reason, it does not happen (Principle P3).

---

## 1. Lens grammar (fixed)

Focal length is a *meaning*, not a taste. It is locked per movement in
`src/narrative/acts.ts` and may not be changed without a Director-mode entry in
the review log.

| Focal range | Meaning | Used for |
|-------------|---------|----------|
| **20–24mm** | vast structure, spatial compression, the machine is bigger than you | Act I interiors, establishing organs |
| **35–45mm** | movement, human point of view, "you are walking here" | Act III floor, Act IV hall, general travel |
| **65–85mm** | parts, body, data detail, intimacy/clinical scrutiny | Act II module, Epilogue portrait |
| **100mm+** | surveillance, non-human observation, being watched | Prologue handshake |

Per-movement assignment (as-built):

| Movement | Lens | Why this lens |
|----------|-----:|---------------|
| PROLOGUE | 100mm | The system observes the subject from a non-human distance before anything is shown. Compression flattens the "door" into pure black. |
| ACT I | 22mm | The city's organs must dwarf the subject; wide compression makes the shafts feel infinite. |
| ACT II | 75mm | The module is a precious object under clinical scrutiny; long lens isolates it from context. |
| ACT III | 40mm | Human-POV inside the computation; we stand *in* the hall, not above it. |
| ACT IV | 35mm | Reverent, architectural, symmetrical — a nave. Slightly wider than Act III to feel the room's stillness. |
| EPILOGUE | 85mm | The film finally looks *at* the subject: a clinical portrait of the replica. |

**Rule:** a single film-wide `PerspectiveCamera` whose `.fov` is driven from the
active movement's lens (converted mm→fov for the composed sensor, see §4). Do not
spawn per-scene cameras with arbitrary FOVs.

---

## 2. Camera damping & the three-beat move

The camera has **mass and inertia.** Input and timeline set a *target*; the
camera integrates toward it. It never snaps, never teleports, never 1:1-tracks a
raw input.

### The three-beat move (the only move we make)
Every significant camera gesture is composed of three beats:

1. **Slow hold** — the camera is nearly still, breathing (sub-pixel drift). This
   is where the subject reads the frame.
2. **Short strong move** — a decisive, brief translation/rotation with real
   acceleration and deceleration (ease-in-out, weighted). It *commits*.
3. **Full stop** — a hard settle to a new hold. No endless drift, no float.

This cadence is what makes SOVEREIGN read as *deliberate* rather than a game
camera. A move that is all drift feels like a screensaver (fails P1/P3); a move
that snaps feels like a UI (fails P5).

### Damping model (implementation contract)
- Position: `pos.lerp(targetPos, 1 - exp(-k_pos * dt))` — frame-rate-independent
  exponential smoothing, **not** a fixed-alpha lerp.
- Rotation: `quat.slerp(targetQuat, 1 - exp(-k_rot * dt))`.
- `k_pos`, `k_rot` are per-beat: **low** during holds (heavy, ~0.8–1.5),
  **higher** during the strong move (~4–7), then back down to settle.
- A small critically-damped spring may be layered for the settle so beat 3 lands
  without overshoot.
- **Micro-motion when idle:** even on a hold, a low-amplitude, low-frequency
  Perlin/`sin` breath (< 0.15° rotation, < 1cm translation) keeps the frame
  alive. This is the same principle as "world keeps micro-moving when scroll
  stops" (Act I). It must be *below conscious notice.*

### Input → camera (never direct)
Input drives the timeline's *target*, which drives the camera. See
[`08_RENDERING_ARCHITECTURE.md`](08_RENDERING_ARCHITECTURE.md) for the full
`input → intent → damped playback` flow. Concretely:
- **Scroll (Act I):** sets `globalProgress` target; camera follows the timeline's
  spline. Scroll velocity feeds damping strength, not position directly.
- **Drag (Act II):** sets a target azimuth **clamped to a 20–30° arc**; camera
  slerps within it. Releasing eases back toward the arc's rest pose. **No pitch
  freedom, no roll, no dolly.** This is not `OrbitControls`.
- **Hold (Prologue):** press duration drives the authentication ring's progress;
  the camera does not move until authentication completes, then executes one
  three-beat push through the door.

---

## 3. Camera paths per movement

Paths are authored as splines/keyframes on the `CinematicTimeline`, evaluated by
the Camera Director. Below is intent; exact keys live with the shot list
([`05_SHOT_LIST.md`](05_SHOT_LIST.md)).

- **PROLOGUE (100mm):** locked frame on black. One move only: on auth, a single
  strong dolly-in "through the door," decelerating hard as Act I resolves.
- **ACT I (22mm):** a continuous **playhead-driven travel** through the organs. It
  is one long move quantized by the scroll checkpoints (0.0 / 0.25 / 0.6 / 1.0),
  each checkpoint a hold. Between checkpoints the camera glides; at checkpoints it
  settles and the world micro-moves.
- **ACT II (75mm):** the camera is essentially **on a turntable arc** around the
  module, but the subject only controls a 20–30° slice of it; the exploded-view
  separation is a timeline event, not a camera move. Camera holds long; the *parts*
  move.
- **ACT III (40mm):** slow arc around the floating core; the strong-move beats are
  triggered by prediction events (the "button presses itself" beat gets a small
  push-in). Glitch events may momentarily *interrupt* the hold with a single-frame
  hitch — logical, not decorative.
- **ACT IV (35mm):** symmetrical, processional. Dead-center compositions. The one
  strong move is the **approach to the sarcophagus** and the push into it when the
  core opens.
- **EPILOGUE (85mm):** near-static portrait. The only motion is the silhouette
  filling with the subject's telemetry. The "already included" beat holds
  absolutely still.

---

## 4. Framing, aspect & safe areas

We compose for cinema but survive every viewport. **No forced letterbox bars.**

- **Desktop target composition: 2.39:1.** But we render the full viewport and use
  a **multi-safe-area** system so the subject survives 16:9 and mobile vertical.
- Define three nested safe rectangles per shot:
  - **Cinema safe (2.39:1):** ideal composition; the "poster" frame.
  - **Wide safe (16:9):** the one center (per P8) must remain readable and
    correctly weighted here.
  - **Vertical safe (mobile 9:19.5-ish):** mobile is its **own cut** (Tier C, P7)
    — reframe the subject for vertical rather than cropping the desktop frame.
- **mm → fov:** the composed frame's vertical FOV is derived from the movement
  lens against a **36mm-equivalent horizontal sensor at 2.39:1**, then the actual
  render FOV is adjusted so the *cinema-safe* region matches that lens. Wider
  viewports letterbox via composition (empty obsidian above/below the subject),
  never via hard black bars drawn on top.
- **The one center rule (P8):** in every shot exactly one element owns the light,
  the eye, and the interaction. Framing places it on a deliberate third or dead
  center (Act IV), never competing with a second bright point.

---

## 5. Movement, lighting motivation & lens discipline (do-not list)

- **No free-orbit product viewer.** Ever. (Anti-cliché.) Act II is a clamped arc.
- **No random drift / floaty screensaver camera.** Idle = micro-breath only.
- **No lens that contradicts meaning.** Don't shoot the Act II module on a 22mm
  "because it fills frame"; intimacy is a 75mm decision.
- **No camera move without a beat structure.** If it can't be expressed as
  hold→move→stop, it's not a move, it's drift.
- **Motivated light travels with the camera.** Each scene has one light center
  (P8); camera moves reveal it, they don't discover new competing sources.
- **Depth of field is a scalpel, not a filter.** Use shallow DoF at 75/85mm to
  isolate the module and the replica; keep Act I deep so the scale reads.
