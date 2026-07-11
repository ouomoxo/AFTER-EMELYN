# 13 — REVIEW LOG

> A running, append-only critique log. Every Critic-mode pass, every accepted
> deviation, every constitutional amendment, and every phase transition is
> recorded here with a date and the mode that raised it. Newest entries at the
> top. This log is the project's memory — decisions not written here did not
> happen.

Entry format:
```
## YYYY-MM-DD — <title>
**Mode:** DIRECTOR | TD | BLENDER | IMPL | CRITIC
**Affects:** <principle(s) / doc(s)>
**Status:** OBSERVED | ACCEPTED | BLOCKED | RESOLVED | AMENDMENT
<body: what, why, and the decision>
```

---

## 2026-07-11 — Documentation contract set established
**Mode:** DIRECTOR + TD
**Affects:** all docs 00–13, CLAUDE.md
**Status:** RESOLVED
The full `/docs` contract set and root `CLAUDE.md` were authored as the binding
engineering + directing reference. Constitution (00) is now supreme; all other
docs are downstream. The six movements, color/lens/audio grammar, tiers A–D, the
`CinematicTimeline` spine, and the Blender neutral-PBR pipeline are documented
**as-built** against the existing scaffold (`src/narrative/acts.ts`,
`src/util/palette.ts`, `tools/blender/sovereign_bpy.py`, `index.html`,
`vite.config.ts`, `package.json`). Locked decisions were documented, not
re-opened.

---

## 2026-07-11 — Blender pipeline capability is PROVEN
**Mode:** BLENDER
**Affects:** P6, docs 06 / 07
**Status:** RESOLVED
The headless authoring pipeline is proven at the **library** level:
`tools/blender/sovereign_bpy.py` (bpy 4.5 LTS) provides the complete chain end to
end —
- **headless bpy build:** factory-empty `reset()`, metric units, deterministic
  scene lifecycle, bmesh primitives (`box/cyl/tube/torus`), machining modifiers
  (`bevel/weighted_normal/subsurf/panel_cut`), and the canonical `mats()`
  material set (Principled BSDF, sRGB→linear);
- **Cycles CPU lookdev render:** `lookdev_render()` — cold three-point rig (white
  key / low cold fill / cyan data rim), AgX view transform, denoised, **GPU-free**
  so it reproduces on any machine/CI;
- **neutral GLB export:** `export_glb()` — apply-modifiers, Y-up, normals +
  tangents, materials EXPORT (factors only, **no baked view transform**), Draco
  level 6.

This satisfies the "assets are real Blender work, reproducible from code"
requirement (Constitution §3.3). The mechanism is demonstrably in place.

**Concrete evidence already present:** Cycles CPU lookdev renders are landing in
`docs/_ref/` — `auth_door.png`, `cybernetic_module.png`, `prediction_core.png`,
`maintenance_drone.png`. Two were reviewed:
- `cybernetic_module.png` — the hero, correctly exploded into its five layers
  (surgical-white ceramic dermal shell / carbon muscle bundles / cyan neural
  lattice / titanium spinal discs / co-processor) on obsidian, reading as a
  **spinal medical device, not a robot** (Act II brief + color grammar hold).
- `auth_door.png` — a vast concentric machined iris with a **cyan (data)** ring,
  **surgical-white (authority)** ring, obsidian aperture, and two small **amber
  (warning)** marks; no red present (none warranted). Palette grammar is exact.
Remaining: author the per-asset `build_*.py` scripts and wire the `glTF-Transform
inspect` + budget gate so each render is paired with a within-budget GLB (P6).

---

## 2026-07-11 — Phase plan (status)
**Mode:** TD
**Affects:** all
**Status:** OBSERVED

| Phase | Goal | State |
|-------|------|-------|
| **P0 · Scaffold** | Vite + TS + Three + GSAP + Zustand; obsidian boot; palette + acts data; bpy library | **DONE** (present in repo) |
| **P1 · Docs contract** | docs 00–13 + CLAUDE.md as binding reference | **DONE** (this set) |
| **P2 · Engine spine** | `CinematicTimeline`, Camera Director (three-beat damping), Narrative State Machine walking `ACTS`, Input Interpreter (input→intent→damped), renderer probe (WebGPU→WebGL2) | TODO |
| **P3 · First asset + parity** | `build_auth_ring.py` + `build_auth_door.py`; inspect gate; engine frame vs Cycles ref sign-off (P6) | TODO |
| **P4 · Prologue vertical slice** | `/handshake` fully playable incl. hold-to-auth, door reveal, audio unlock, captions, keyboard/reduced-motion paths; hit P9 (20s tech proof) | TODO |
| **P5 · Movements I–IV** | build hero assets (cybernetic_module, prediction_core, vault_sarcophagus) + infra kit; scroll-playhead; clamped drag; pre-emption; vault debug UI | TODO |
| **P6 · Epilogue + loop** | silhouette from telemetry, 98.7% readout, non-answer, second-visit staging, final-twist audio, restart pull (P10) | TODO |
| **P7 · Tiers + a11y + budget** | Tier C mobile cut, Tier D reduced-motion, streaming/eviction, full acceptance pass (doc 12) | TODO |

---

## 2026-07-11 — CRITIC: canonical hex for Emergency Red is inconsistent in index.html
**Mode:** CRITIC
**Affects:** doc 04 palette parity, P1 boot integrity
**Status:** OBSERVED (hand to IMPL)
`index.html` declares the boot CSS variable as `--emergency: # e0322a;` — there is
a **stray space after `#`**, which makes the custom property value invalid CSS
(the variable resolves to an invalid color). The canonical value is `#e0322a`
(matches `src/util/palette.ts :: CSS.emergency` and `sovereign_bpy.py :: PAL`).
Low blast radius today (the var is not yet consumed at boot), but it violates the
"single source of truth, values mirrored across TS/CSS/Blender" rule (doc 04 §1 /
doc 06 §7). **Action for IMPL:** correct to `--emergency: #e0322a;`. Logged rather
than silently fixed because palette values are a governed contract — the change
should be a deliberate, attributable edit.

---

## 2026-07-11 — CRITIC: assets script path vs per-asset invocation — clarify, don't conflate
**Mode:** CRITIC / TD
**Affects:** doc 06, CLAUDE.md run commands
**Status:** RESOLVED
Two Blender entry points coexist and both are correct; documented so they are not
"reconciled" by mistake:
- `npm run assets` → `python3 tools/asset-pipeline/build_assets.py` — the
  **orchestrator** (runs every `build_*.py`, then the inspect + budget gate).
- `python3 tools/blender/build_<asset>.py` — a **single asset**, as referenced in
  the `sovereign_bpy.py` docstring.
Both are recorded in doc 06 §1 and CLAUDE.md. No change required; flagged to
prevent a future "there are two build scripts" false-bug.

---

## Template for the next entry
```
## YYYY-MM-DD — <title>
**Mode:**
**Affects:**
**Status:**
<body>
```
