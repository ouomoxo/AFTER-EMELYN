# CLAUDE.md — SOVEREIGN//77

Persistent brief for future sessions. Read this first, then the relevant doc in
`/docs`. The docs are contracts; when in doubt, they win over vibes.

## The vision (3 lines)
1. A **3–5 min interactive short film in the browser**: the user is a **subject**
   accessing SOVEREIGN, a 2077 AI that runs a city — officially to protect humans,
   really to predict them until free will is an unnecessary variable.
2. The twist: while the subject thinks they explore the system, the system uses
   **their behavior** (cursor/dwell/scroll/latency — **session-only, no PII, no
   network**) to finish a **digital replica** of them. Tagline: *"THE SYSTEM IS NOT
   WAITING FOR YOUR INPUT."*
3. **Everything is diegetic** — menus, loading, cursor, scroll, sound, errors are
   in-world events. Never a "web page," never a "visitor."

## Locked stack (do NOT propose alternatives — see docs/08)
- **Vanilla TypeScript + Vite + Three.js r0.169 + GSAP + Zustand vanilla store.
  NO React** (engine lives outside any UI framework's reconciliation; UI is
  minimal diegetic HUD; lean bundle proves tech in 20s).
- Renderer: **WebGPU → WebGL2 fallback**; materials toward **TSL/NodeMaterial**.
- **One `CinematicTimeline`** is the spine `{ act, shot, localTime, globalProgress,
  interactionState, transitionState }`. **Input never drives it directly** — input
  → intent → *target* → **damped** playback. Camera = lerp/slerp with mass; motion
  is **three-beat: slow hold → short strong move → full stop**.
- Assets are **real Blender 4.5 headless bpy** (neutral PBR GLB, Draco, tangents;
  AgX for lookdev only; web supplies tone-map + grade). See docs/06.
- Audio is **fully synthesized Web Audio — NO audio files** (6 layers). See docs/09.
- Tiers **A** (WebGPU full) / **B** (WebGL2 reduced) / **C** (mobile — *its own
  cut*) / **D** (reduced-motion static). See docs/10.

## How to run
```bash
npm run dev            # vite dev server (localhost:5173)
npm run build          # tsc --noEmit && vite build
npm run typecheck      # tsc --noEmit
npm run preview        # serve the build (port 4173)
npm run assets         # python3 tools/asset-pipeline/build_assets.py (build ALL GLBs + inspect gate)
npm run capture        # node tools/capture/shoot.mjs (Playwright frame capture for acceptance)
python3 tools/blender/build_<asset>.py   # build ONE asset from the bpy library
```

## Color grammar (source of truth: src/util/palette.ts — mirror in Blender PAL)
Ratio budget by screen area — **enforced**:
`Obsidian #050506 55% · Graphite #14161a 20% · Surgical #e8ecec 12% · Cyan
#4fd4d0 7% · Amber #e0a038 4% · Emergency #e0322a 2%`.
**Semantics (fixed): Cyan = data · White = authority · Amber = warning · Red =
privilege/danger only.** Reference intent via `SEMANTIC`, never raw hex in UI.

## Lens grammar (source of truth: src/narrative/acts.ts)
`20–24mm` vast structure/compression · `35–45mm` movement/human POV · `65–85mm`
parts/body/data detail · `100mm+` surveillance/non-human. Per movement: Prologue
100 · Act I 22 · Act II 75 · Act III 40 · Act IV 35 · Epilogue 85. Compose for
2.39:1, **no forced letterbox**, multi-safe-area (survives 16:9 + mobile vertical).

## The six movements (routes; seamless transitions)
`/handshake` PROLOGUE · `/infrastructure` ACT I · `/augmentation` ACT II (hero) ·
`/prediction` ACT III · `/black-vault` ACT IV · `/mirror` EPILOGUE. Full beats +
exact on-screen system lines in **docs/05_SHOT_LIST.md**. Second visit
(localStorage marker `{visited, replica, lastChoice}`) is staged as recognized.

## Two rules to never break
- **Each scene has exactly ONE center** of light, of sound, of interaction (P8).
- **Every camera move needs a narrative purpose** (P3) — expressible as
  hold→move→stop, or it doesn't happen.

## Anti-clichés (the DO-NOT list — docs/04 §5)
No indiscriminate neon pink/blue · no glitch everywhere (Act III glitches are only
logical events) · no meaningless/frozen HUD numbers · no hexagon spam · no giant
repeated English typography · no black metal that only reflects · no excess
particles · no emission on everything · **no free-rotate product viewer** (Act II
is a clamped 20–30° arc) · no Ready-Player-One holograms.
Frozen-frame test: a paused frame must not look like a generic web template; strip
neon+glitch and the future-tech worldview must survive.

## Where things live
```
index.html                     obsidian boot (no white flash); #stage (canvas) + #interface (HUD)
src/narrative/acts.ts          the 6 movements: id, route, lens, duration, center, systemLine, bundle
src/util/palette.ts            canonical colors + SEMANTIC grammar (single source of truth)
src/{engine,input,audio,ui,state,data}/   engine layers (aliases @engine/@input/... in tsconfig)
tools/blender/sovereign_bpy.py shared bpy authoring library (mats(), primitives, export, lookdev)
tools/blender/build_*.py       per-asset build scripts (author these; keep 1:1 with docs/07)
tools/asset-pipeline/build_assets.py   orchestrator + inspect/budget gate
tools/capture/shoot.mjs        Playwright frame capture (acceptance)
public/assets/{models,env,lut}/  shipped GLBs (Draco) + IBL + runtime grade LUTs
BLENDER/0X_*/                   per-movement working/reference space (not shipped)
docs/00..13 + 07_ASSET_REGISTRY.yaml   the binding contracts (00 Constitution is supreme)
```

## Working modes (declare which you're in — docs/00 §4)
**DIRECTOR** (story/emotion/one-center) · **TD** (engine/budget/timeline) ·
**BLENDER** (geometry/material parity/registry) · **IMPL** (running code) ·
**CRITIC** (frozen-frame test + docs/13 review log). Log decisions in
**docs/13_REVIEW_LOG.md** — unwritten decisions didn't happen.

## Non-negotiable ethics/safety
Session-only telemetry, **no PII, no network egress**, one localStorage marker
only. No flashing >3/s, no white flash, no startle. All plot legible muted (text +
captions) and via the keyboard + Described Path (docs/11). These are hard release
blocks (docs/12 §4).
