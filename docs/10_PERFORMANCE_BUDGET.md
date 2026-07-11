# 10 — PERFORMANCE BUDGET

> Budgets are contracts, not aspirations. The Performance Governor enforces frame
> targets at runtime; the asset inspect gate ([`06_BLENDER_PIPELINE.md`](06_BLENDER_PIPELINE.md) §8)
> enforces size/tri budgets at build time. A number below is a ceiling you design
> under, not a limit you discover by profiling later.

---

## 1. The budget table

### 1.1 Download / memory
| Budget | Ceiling | Notes |
|--------|---------|-------|
| **Bootstrap JS + CSS** | **≤ 3 MB** | the code + inline CSS to first paint & handshake. Split: `three`, `gsap`, app (`vite.config.ts` manualChunks). Serves P9. |
| **First-screen assets** | **8–12 MB** | the `core` bundle: auth_door, auth_ring, data_particle, env/lut for the Prologue. Must land fast enough to prove tech in 20s. |
| **Per-scene streaming** | **10–25 MB** | each subsequent movement `bundle` (infra/augment/predict/vault/mirror), streamed ahead of its gate. |
| **Total transferred** | **60–120 MB** | whole film, all movements, one visit. |

### 1.2 GPU / frame
| Budget | Range | Notes |
|--------|-------|-------|
| **Simultaneous triangles** | **300K – 900K** | on screen at once. Registry tri_budgets sum ~489K authored; not all resident/visible simultaneously. |
| **Draw calls (normal)** | **80 – 160** | typical scene. Instancing (drones, racks, panels, particles) keeps this down. |
| **Draw calls (hero peak)** | **≤ 200** | Act II module exploded + HUD, Act III core + sims. Hard ceiling. |

### 1.3 Frame-rate targets by tier
| Tier | Device class | Target fps |
|------|--------------|-----------:|
| **A** | high-end desktop, WebGPU | **55–60** |
| **B** | mid desktop / WebGL2 | **30–45** |
| **C** | mobile (its own cut) | **30** |
| **D** | reduced-motion | mostly static; no fps target |

Falling below the tier's floor for a sustained window triggers a governor
step-down (§3), never a silent stutter.

---

## 2. Streaming strategy

- **Bundles map to movements** (`core → infra → augment → predict → vault →
  mirror`), matching the `bundle` field in `src/narrative/acts.ts` and
  [`07_ASSET_REGISTRY.yaml`](07_ASSET_REGISTRY.yaml).
- **Prefetch the next bundle during the current movement.** The Asset Streamer
  begins loading movement _N+1_ as soon as movement _N_ is stable, so the
  transition gate opens on already-resident assets.
- **The gate holds diegetically, never with a spinner.** If the next bundle is not
  resident when `globalProgress → 1.0`, the Narrative State Machine sets
  `transitionState = 'holding'` and plays a diegetic "provisioning" beat (a system
  line, a breath of the space) until residency, then opens. No web loader chrome
  ever appears (Constitution: everything is in-world).
- **Evict behind you.** After a gate opens and the new movement is stable, dispose
  the previous movement's GPU resources (geometries, textures, render targets) to
  stay inside the total-memory envelope. The `core` bundle (data_particle, env) is
  retained since it recurs (Act I fiber, Act III sims, Epilogue silhouette).
- **Compression:** GLB Draco (mesh) + KTX2/Basis (any textures). `vite.config.ts`
  never inlines `.glb`/`.ktx2` (`assetsInlineLimit: 0`) so they stream as separate
  requests and can be cached/prefetched independently.
- **Budget arithmetic:** `bootstrap (≤3) + first-screen (8–12) + Σ per-scene
  (5 × 10–25, with eviction) ≈ 60–120 MB` total. Any asset that would push a
  bundle past 25 MB must be split, instanced harder, or demoted to prerender on
  constrained tiers.

---

## 3. Tier fallbacks (Performance Governor)

The Governor picks a **starting tier** from the renderer probe (WebGPU? WebGL2?)
plus device signals (memory, DPR, pointer type, `prefers-reduced-motion`), then
**adapts down** if frame time regresses. It does not adapt *up* mid-movement
(avoids oscillation); it may re-evaluate at a gate.

| From → To | Trigger | What is dropped (in this order) |
|-----------|---------|----------------------------------|
| A → B | no WebGPU, or sustained < 55fps | volumetric density ↓, reflection resolution ↓, particle count ↓, DoF quality ↓ |
| B → B− | sustained < 30fps | bloom to cheap pass, shadow resolution ↓, instance counts ↓ |
| any → C | mobile / touch primary / low mem | switch to the **mobile director's cut** (vertical framings, prerender/2.5D for heavy travel beats) — not a downscale |
| any → D | `prefers-reduced-motion: reduce` | static frames, minimal transitions, no idle drift/parallax; press-and-hold alternative (doc 11) |

Order of sacrifice is fixed so downgrades are predictable and never touch the
**one center** of a scene: particles and volumetrics go before the hero asset's
fidelity; the subject's focal point is the last thing to degrade (P8).

**Tier C and D are authored cuts, not runtime downscales** — the Governor
*selects* them; the Director *designed* them (Constitution §3.5, P7).

---

## 4. Measurement plan

Budgets are verified continuously, not once.

### Build-time (fails the build)
- **glTF-Transform inspect** per GLB: tri count vs `tri_budget`, draw
  call/material count, tangents present, textures absent where declared
  factor-only, file size vs per-scene budget. (Doc 06 §8.)
- **Bundle size check:** Vite build output vs the 3 MB bootstrap ceiling and each
  movement bundle vs 10–25 MB. Regression fails CI.

### Runtime (instrumented, dev overlay)
- **Frame time / fps** rolling window per movement; logs the tier and any
  step-down with the movement + `localTime` where it happened.
- **Draw calls & triangles** via `renderer.info` each movement; assert ≤160
  normal / ≤200 hero and within the 300K–900K triangle band.
- **Memory:** GPU resource counts (geometries/textures/programs) before and after
  each gate to confirm eviction actually frees the previous movement.
- **Time-to-handshake-interactive:** wall-clock from navigation to the Prologue
  press-and-hold being live — the P9 metric. Tracked as a first-class number.

### Field verification (per [`12_ACCEPTANCE_CRITERIA.md`](12_ACCEPTANCE_CRITERIA.md))
- **Low-end profile:** a mid WebGL2 laptop and a real mid mobile device, not just
  a throttled desktop.
- **Load-fail:** a throttled/blocked bundle must hold the gate diegetically, never
  show a broken loader or a white flash.
- **Capture:** `npm run capture` (Playwright, `tools/capture/shoot.mjs`) grabs
  reference frames per movement for the frozen-frame test and for regression of
  the color ratio budget (doc 04).

---

## 5. Budget ownership

- **Blender mode** owns tri_budget and GLB size (registry + inspect gate).
- **Impl mode** owns draw calls, instancing, eviction, and frame time.
- **TD mode** owns the tier definitions and the governor's sacrifice order and is
  the final arbiter when a Director request exceeds budget: the answer is "cut
  something else," recorded in [`13_REVIEW_LOG.md`](13_REVIEW_LOG.md).
