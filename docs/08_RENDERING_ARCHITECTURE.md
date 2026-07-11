# 08 — RENDERING ARCHITECTURE

> One engine, one timeline, no framework on the render path. This doc is the TD's
> contract. The stack decisions here are **locked** (Constitution §3) — document
> them as-built; do not propose alternatives.

---

## 1. Stack (as-built)

- **Language/build:** Vanilla **TypeScript + Vite**. ESNext modules; `three` and
  `gsap` are split into their own chunks (`vite.config.ts :: manualChunks`).
- **3D:** **Three.js r0.169**, `WebGPURenderer` preferred, WebGL2 fallback.
- **Animation:** **GSAP** for timeline tweening/easing of scalar targets and HUD.
- **State:** **Zustand vanilla store** (`zustand/vanilla`) — *not* the React
  bindings.
- **DOM host:** `index.html` provides `#stage` (Three.js canvas host, the world),
  `#interface` (DOM HUD, the diegetic UI), and `#boot` (pre-JS obsidian paint).
- **Path aliases** (`tsconfig.json`): `@engine @narrative @audio @input @ui
  @state @util @data`.

### Why NO React (the technical-director call)
1. **The engine must live outside any UI framework's reconciliation.** The render
   loop is a `requestAnimationFrame`/WebGPU-driven timeline, not a component tree.
   React's diffing, effects, and re-render scheduling add a layer of
   unpredictability and GC pressure directly on the frame budget we cannot afford
   at 55–60fps with a heavy scene.
2. **The UI is minimal, diegetic HUD** — a handful of mono readouts and one or two
   interactive prompts per scene. It does not need a component framework; it needs
   to be a thin DOM layer the engine drives imperatively from store state.
3. **Bundle leanness serves P9** ("prove the tech level in 20s"). No framework
   runtime means a smaller bootstrap and a faster first meaningful paint on the
   handshake — which is itself the tech-level proof.

The tradeoff (manual DOM updates, no JSX ergonomics) is accepted deliberately.
The HUD is small enough that hand-written imperative updates from the store are
*simpler*, not harder, than a reconciler here.

---

## 2. Engine layers

```
┌──────────────────────────────────────────────────────────────────────┐
│  DOM INTERFACE LAYER  (#interface)                                     │
│  diegetic HUD · system lines · prompts · captions · debug UI (Act IV)  │
│  imperative, driven from the Zustand store; never on the render path   │
└──────────────▲───────────────────────────────────────────────────────┘
               │ store subscribe (state → DOM)
┌──────────────┴───────────────────────────────────────────────────────┐
│  NARRATIVE STATE MACHINE                                               │
│  walks src/narrative/acts.ts · owns movement entry/exit · transitions  │
│  · second-visit staging · writes interactionState/transitionState      │
└──────────────▲───────────────────────────────────────────────────────┘
               │ intent
┌──────────────┴──────────────┐   ┌──────────────────────────────────────┐
│  INPUT INTERPRETER           │   │  AUDIO DIRECTOR (Web Audio API)      │
│  raw events → INTENT →       │   │  6 synthesized layers · ducking ·    │
│  damped playhead TARGET      │   │  telegraph sub-bass · per-scene       │
│  (never direct control)      │   │  sound center · NO audio files        │
└──────────────▲──────────────┘   └──────────────────▲───────────────────┘
               │ target                                │ cue
┌──────────────┴───────────────────────────────────────┴────────────────┐
│  CINEMATIC TIMELINE  (THE SPINE — one instance)                        │
│  { act, shot, localTime, globalProgress, interactionState,            │
│    transitionState } · input sets targets, playback DAMPS toward them  │
└──────────────▲───────────────────────────────────────────────────────┘
               │ evaluate(t)
┌──────────────┴───────────────────────────────────────────────────────┐
│  THREE.JS CINEMATIC ENGINE                                             │
│   Scene Loader ─ Camera Director ─ Timeline eval ─ Material System     │
│   ─ Post FX ─ Performance Governor ─ Asset Streamer                    │
│   renders into #stage (WebGPU → WebGL2)                                │
└───────────────────────────────────────────────────────────────────────┘
```

### Layer responsibilities
- **DOM Interface Layer:** renders the HUD from store state. Owns nothing about
  3D. Captions and the Act IV debug interface live here.
- **Narrative State Machine:** the only thing that knows "which movement" and how
  they stitch. Walks `ACTS`; opens/holds the transition gate; applies second-visit
  dressing. Sets `interactionState`/`transitionState` on the timeline.
- **Audio Director:** fully synthesized Web Audio (see
  [`09_AUDIO_DIRECTION.md`](09_AUDIO_DIRECTION.md)). Subscribes to timeline cues.
- **Input Interpreter:** the `input → intent → damped playback` funnel (§5).
- **Cinematic Engine sub-systems:**
  - **Scene Loader** — builds/tears down the movement's Three scene graph.
  - **Camera Director** — single `PerspectiveCamera`; drives FOV from the movement
    lens; executes three-beat damped moves ([`03_CINEMATOGRAPHY_BIBLE.md`](03_CINEMATOGRAPHY_BIBLE.md)).
  - **Timeline eval** — samples the `CinematicTimeline` each frame.
  - **Material System** — the canonical material roles (parity with
    `sovereign_bpy.py :: mats()`); tone-map + grade LUT applied here.
  - **Post FX** — bloom (data/authority only), DoF, grade; tier-gated.
  - **Performance Governor** — measures frame time, picks/adjusts tier (§4).
  - **Asset Streamer** — loads per-movement `bundle` GLBs (Draco) ahead of the
    gate; holds the gate on a diegetic beat if not resident.

---

## 3. Renderer: WebGPU → WebGL2, and TSL/NodeMaterial direction

- **Capability probe at boot:** try `WebGPURenderer`; on failure or missing
  adapter, fall back to WebGL2. The probe result feeds the initial performance
  tier (§4).
- **Materials are authored toward TSL / `NodeMaterial`.** The runtime Material
  System expresses the canonical roles as node materials so the *same* graph runs
  on WebGPU (TSL) and degrades on WebGL2. This keeps a single material definition
  across renderers and is the long-term home for the data/authority emissive
  behaviors (runtime-driven emission on `M_Data`, the auth ring arc, fiber
  pulses).
- **Neutral-in, graded-out:** GLBs arrive as neutral PBR (Blender contract, doc
  06). The Material System applies **one tone-map + one grade LUT** for all
  assets so Blender↔web parity is a single reconciliation (P6).

---

## 4. Performance tiers A–D

The **Performance Governor** selects a starting tier from the renderer probe +
device signals, then may step down if frame time regresses. Full budgets in
[`10_PERFORMANCE_BUDGET.md`](10_PERFORMANCE_BUDGET.md).

| Tier | Target | Renderer | What's on | Frame target |
|------|--------|----------|-----------|--------------|
| **A** | high-end desktop | WebGPU | full reflections, volumetrics, particles, DoF, bloom | 55–60fps |
| **B** | mid desktop / no WebGPU | WebGL2 | reduced reflections, lighter volumetrics, fewer particles | 30–45fps |
| **C** | **mobile — its own cut** | WebGL2 | limited realtime + **prerender / 2.5D**; reframed vertical compositions (P7) | 30fps |
| **D** | **Reduced Motion** | either | static frames + minimal transitions; no parallax/idle drift; press-and-hold replaced (see [`11_ACCESSIBILITY.md`](11_ACCESSIBILITY.md)) | n/a (mostly static) |

**Tier C is authored, not derived:** mobile gets its own vertical framings and may
substitute prerendered sequences for the heaviest movements (hybrid strategy §6).
Tier D is triggered by `prefers-reduced-motion` and is a first-class path, not a
graceful-degradation afterthought.

---

## 5. The CinematicTimeline (the spine) & input flow

### 5.1 Interface (contract)
```ts
type InteractionState =
  | 'idle'        // scene playing itself; world micro-moves
  | 'engaged'     // subject actively driving a target (scroll/drag/hold)
  | 'preempted'   // system acted before the subject (Act III / Epilogue)
  | 'locked';     // input ignored during a committed transition beat

type TransitionState =
  | 'stable'
  | 'gate-arming' // approaching globalProgress ~1.0
  | 'gate-open'   // handing off to next movement
  | 'holding';    // gate held on a diegetic beat (bundle not resident)

interface CinematicTimeline {
  act: SceneId;              // from src/narrative/acts.ts
  shot: number;              // index of the current beat within the movement
  localTime: number;         // seconds within the movement
  globalProgress: number;    // 0..1 within the movement (the "playhead")
  interactionState: InteractionState;
  transitionState: TransitionState;

  // Input NEVER writes these directly. It writes a target; playback damps.
  setTarget(progress: number, opts?: { velocity?: number }): void;
  tick(dt: number): void;    // advances damped playback toward target
  sample(): CameraKey;       // camera pose + fov for Camera Director
}
```
There is **exactly one** instance. Everything (camera, audio, HUD, streaming)
reads from it; nothing else holds a parallel notion of "where we are."

### 5.2 input → intent → damped playback (the golden rule)
```
raw event (wheel / pointermove / pointerdown+hold / touch)
        │
        ▼
INPUT INTERPRETER
   • normalize per device (wheel line/px, touch delta, hold duration)
   • classify INTENT: advance | inspect(azimuth) | authenticate(hold) | choose
   • rate-limit + smooth (kill jitter, no 1:1 tracking)
        │  intent
        ▼
CINEMATIC TIMELINE.setTarget(progress, {velocity})
        │  target (NOT position)
        ▼
tick(dt): damp globalProgress → target  (exp smoothing, velocity-weighted)
        │
        ▼
Camera Director: three-beat move toward sample() pose (lerp/slerp, mass/inertia)
```
Consequences that must hold:
- **Scroll never jumps the playhead**; it moves a target the playback eases to.
- **Drag (Act II) sets a clamped azimuth target (20–30°)**, never a raw camera
  rotation — this is why it is *not* `OrbitControls`.
- **Hold (Prologue) drives ring progress**, a scalar target, not motion.
- **Pre-emption (Act III/Epilogue):** the system sets `interactionState =
  'preempted'` and fires the action's target *ahead* of the subject's input —
  the mechanic behind "the button presses itself."
- When idle, the timeline still `tick`s: world micro-motion and camera
  micro-breath continue (P5 aliveness).

---

## 6. Hybrid realtime + prerender strategy

Not every movement must be fully realtime on every tier. The engine supports a
**hybrid** per-movement, per-tier decision:

- **Realtime (default, Tiers A/B):** full Three scene, damped camera, live
  particles. Required for the interactive beats (Prologue hold, Act II drag, Act
  III pre-emption, Act IV open, Epilogue choice) — interactivity cannot be
  prerendered.
- **Prerender / 2.5D (Tier C, and heavy establishing beats):** the
  *non-interactive* travel beats (e.g. Act I organ fly-through establishing, Act
  III hall reveal) may be served as prerendered sequences or 2.5D parallax plates
  on mobile, with realtime overlays only for the interactive moment. The Asset
  Streamer chooses the variant by tier.
- **Boundary rule:** an interactive beat is **always realtime**; a purely
  cinematic beat **may** be prerendered on constrained tiers. The subject must
  never lose agency to a video where the shot list promises interaction.
- Prerendered sequences are produced from the same Blender scenes (Cycles/EEVEE),
  keeping look parity; they ship as KTX2 image sequences or compressed video
  within the streaming budget.

---

## 7. Boot & first paint (P9 support)

- `index.html` paints obsidian **before JS** (inline critical CSS, `#boot`). There
  must never be a flash of white — the first frame is a cold-start terminal.
- `main.ts` takes over `#boot`, initializes the renderer probe, loads the `core`
  bundle, and enters `/handshake`. The 20-second tech proof begins the instant the
  tracking-dot cursor and door reveal land — so the `core` bundle must be inside
  the bootstrap budget (≤3MB JS/CSS, first-screen assets 8–12MB; doc 10).
