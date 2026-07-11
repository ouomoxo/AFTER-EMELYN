# 00 — PROJECT CONSTITUTION

> SOVEREIGN//77 — *The system is not waiting for your input.*
> This document sits above all others. If any other doc, ticket, or clever
> idea contradicts it, this wins. Amend it deliberately, never casually.

---

## 1. What we are building

SOVEREIGN//77 is a **3–5 minute interactive short film that runs in a browser**.
It is not a website, not a product page, not a "cyberpunk company" showcase. The
browser tab *is* an access terminal to SOVEREIGN, a transnational AI that runs a
city in 2077.

The user is a **subject**, never a "visitor." Every element on screen — menus,
loading, cursor, scroll, sound, error states — is a **diegetic in-world event**.
There is no chrome that admits "this is a web page." A loading bar is the system
provisioning. A cursor is a tracked cognitive signature. An error is a censored
record.

The story has a single spine and a single twist:

- **Official purpose of SOVEREIGN:** protect humans.
- **Real purpose:** predict human choice so completely that free will becomes an
  unnecessary variable.
- **The twist on the user:** they believe they are exploring the system. The
  system is using *their* behavior — cursor motion, dwell time, scroll velocity,
  interaction latency (session-only, **no PII, nothing persisted server-side**) —
  to finish building a **digital replica of them**. By the epilogue the replica
  is 98.7% complete and their "choice" was already included in the model.

If a contributor cannot explain how their work serves *that* deception, the work
is decoration and does not ship.

---

## 2. The 10 Acceptance Principles

These are the constitution's teeth. Every scene, asset, and commit is judged
against them. They are restated as testable checks in
[`12_ACCEPTANCE_CRITERIA.md`](12_ACCEPTANCE_CRITERIA.md).

| # | Principle | Failure looks like |
|---|-----------|--------------------|
| P1 | **A single frozen frame must not read as a generic web template.** | Centered hero text, a nav bar, card grid, or SaaS gradient. |
| P2 | **Remove all neon and glitch and the future-tech worldview must survive.** | The scene only feels "future" because of glow and RGB-split. |
| P3 | **Every camera move has a narrative reason.** | Camera drifts/orbits because "it looks cool." |
| P4 | **UI conveys events, not decoration.** | HUD numbers that never change or mean nothing; hexagon spam. |
| P5 | **User input feels like part of the scene.** | Input drives a raw control (free orbit, instant scroll jump). |
| P6 | **Blender↔web material parity is controlled, not accidental.** | An asset looks right in Blender and wrong (or vice-versa) in engine, with no known reason. |
| P7 | **Mobile is its own director's cut, not a shrunk desktop.** | Desktop scene crammed into a phone with tiny text and dropped frames. |
| P8 | **Each scene has exactly ONE center** of light, of sound, of interaction. | Two competing focal points; the eye doesn't know where to go. |
| P9 | **The tech level is proven in the first 20 seconds.** | The handshake looks like a splash screen; nothing signals "this is beyond a normal site." |
| P10 | **After the final scene the user wants to restart.** | The epilogue closes the loop but creates no pull to re-enter. |

A build can be technically green and still fail the constitution. Green tests are
necessary, not sufficient.

---

## 3. Non-negotiables (locked decisions)

These are **as-built** engineering and directing decisions. Document them,
implement them, do **not** re-litigate them in tickets. Rationale for each lives
in the referenced doc.

### 3.1 Stack
- **Vanilla TypeScript + Vite + Three.js (r0.169) + GSAP + Zustand vanilla store.
  NO React, no Vue, no framework reconciliation on the render path.** The
  cinematic engine must live *outside* any UI framework's render cycle; the UI is
  a minimal diegetic HUD; the bundle stays lean to satisfy P9. Rationale:
  [`08_RENDERING_ARCHITECTURE.md`](08_RENDERING_ARCHITECTURE.md).
- **Renderer:** prefer Three.js `WebGPURenderer`; fall back to WebGL2. Materials
  authored toward TSL / `NodeMaterial` long-term.
- **State:** Zustand vanilla store (`zustand/vanilla`), never the React bindings.

### 3.2 The Timeline is the spine
- There is exactly **one `CinematicTimeline`**. It is the single source of truth
  for `{ act, shot, localTime, globalProgress, interactionState, transitionState }`.
- **Input never controls the timeline directly.** Input sets a *target*; playback
  damps toward it. Camera uses `lerp`/`slerp` with mass and inertia. Motion is
  three-beat: **slow hold → short strong move → full stop.** See
  [`03_CINEMATOGRAPHY_BIBLE.md`](03_CINEMATOGRAPHY_BIBLE.md) §Camera Damping.

### 3.3 Assets are real Blender work
- Hero assets are authored in **Blender 4.5 LTS via headless `bpy`**, from the
  shared library `tools/blender/sovereign_bpy.py` and per-asset
  `tools/blender/build_*.py` scripts. Export is **neutral PBR** (Principled BSDF,
  metallic-roughness, no baked view transform). Blender uses **AgX for lookdev
  only**; the web runtime supplies tone-mapping and grade. GLB out with Draco +
  tangents. See [`06_BLENDER_PIPELINE.md`](06_BLENDER_PIPELINE.md).

### 3.4 Color, lens, sound grammar
- **Color is a ratio budget with fixed semantics** (Obsidian 55 / Graphite 20 /
  Surgical 12 / Cyan 7 / Amber 4 / Red 2). Cyan = data, White = authority,
  Amber = warning, Red = privilege/danger **only**. Source of truth:
  `src/util/palette.ts` + [`04_ART_DIRECTION.md`](04_ART_DIRECTION.md).
- **Lens grammar is fixed per movement** (see `src/narrative/acts.ts`).
- **Audio is fully synthesized Web Audio — NO audio asset files.** Six layers,
  storyboarded from the start. See [`09_AUDIO_DIRECTION.md`](09_AUDIO_DIRECTION.md).

### 3.5 Performance tiers
- Four tiers: **A** (WebGPU, full), **B** (WebGL2, reduced), **C** (mobile,
  limited realtime + prerender/2.5D), **D** (Reduced Motion, static + minimal
  transitions). **Tier C is a separate director's cut, not a downscaled A.**
  Budgets in [`10_PERFORMANCE_BUDGET.md`](10_PERFORMANCE_BUDGET.md).

---

## 4. The five working modes

Every task is done from one of five explicit stances. When you start work, state
which mode you are in. The modes have different authority and different outputs;
mixing them silently is how scope and quality drift.

### DIRECTOR mode
- **Owns:** story truth, emotional curve, what each scene *means*, where the one
  center is, whether a camera move earns its keep.
- **Outputs:** shot intent, on-screen system lines, pacing, the "why."
- **Authority:** can reject anything that violates P1–P10 even if it is
  technically excellent. Cannot demand something the budget forbids without
  cutting elsewhere.
- **Primary docs:** 01, 02, 03, 05.

### TECHNICAL DIRECTOR (TD) mode
- **Owns:** the engine architecture, the timeline contract, tiers, the render
  path, performance budgets, feasibility.
- **Outputs:** interfaces, data flow, tier fallbacks, budget rulings.
- **Authority:** can veto on grounds of budget, frame time, or architectural
  integrity. Says "no" with numbers.
- **Primary docs:** 08, 10.

### BLENDER (asset) mode
- **Owns:** hero geometry, material parity, the neutral-PBR export, tri budgets,
  the asset registry.
- **Outputs:** `build_*.py` scripts, GLBs, lookdev renders, registry entries.
- **Authority:** owns what is physically in the mesh. Must hit tri/material
  budgets from 10 and registry from 07.
- **Primary docs:** 06, 07.

### IMPLEMENTATION (impl) mode
- **Owns:** the running code — engine layers, scene loaders, HUD, input, audio,
  glue.
- **Outputs:** TypeScript that honors the timeline contract and the grammar.
- **Authority:** decides *how* within the constraints handed down; may not invent
  new colors, lenses, or free controls.
- **Primary docs:** 08, 09, 04.

### CRITIC mode
- **Owns:** the frozen-frame test, the "does this look like a template" gut check,
  the review log.
- **Outputs:** entries in [`13_REVIEW_LOG.md`](13_REVIEW_LOG.md); pass/fail against
  P1–P10 and [`12_ACCEPTANCE_CRITERIA.md`](12_ACCEPTANCE_CRITERIA.md).
- **Authority:** can send any scene back with a specific, reproducible reason.
  "It feels off" is not a valid critique; "the second focal point at 0:42 splits
  attention, violating P8" is.
- **Primary docs:** 12, 13.

A single contributor plays several modes across a day. The discipline is to know
which hat is on and to *hand off* between modes rather than blur them.

---

## 5. Amendment rule

This document changes only by explicit decision recorded in
[`13_REVIEW_LOG.md`](13_REVIEW_LOG.md) with date, the mode that proposed it, and
what principle it affects. Everything else is downstream and may be revised to
serve it.
