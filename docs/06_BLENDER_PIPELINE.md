# 06 — BLENDER PIPELINE

> Assets are **real Blender work**, authored in code, built headless, and
> reproducible from a clean checkout. No hand-tweaked `.blend` files are the
> source of truth — the **Python is the source of truth.** This is what makes the
> pipeline provable (a clean machine can regenerate every GLB) and is the basis of
> the "pipeline is proven" review-log entry ([`13_REVIEW_LOG.md`](13_REVIEW_LOG.md)).

Target: **Blender 4.5 LTS**, `bpy` module, headless (`--background` or the `bpy`
pip module invoked from `python3`).

---

## 1. Layout

```
tools/blender/
  sovereign_bpy.py        # shared authoring library (THE canonical layer)
  build_<asset>.py        # one per hero/mid asset; imports sovereign_bpy
tools/asset-pipeline/
  build_assets.py         # orchestrator: runs all build_*.py, then inspects
tools/capture/
  shoot.mjs               # Playwright frame capture (verification, not assets)

BLENDER/                  # working / reference space, organized by movement
  00_PREVIS/              # blockout, camera previs
  01_HANDSHAKE/ 02_INFRASTRUCTURE/ 03_AUGMENTATION/
  04_PREDICTION/ 05_BLACK_VAULT/ 06_MIRROR/
  ASSET_LIBRARY/          # shared kit parts, reference frames
  EXPORT/                 # staging for GLB before promotion to public/

public/assets/
  models/                 # shipped GLBs (Draco) — the runtime reads these
  env/                    # environment / IBL data
  lut/                    # grade LUTs applied at runtime (not baked in Blender)

docs/_ref/                # Cycles CPU lookdev reference frames (<asset>.png)
                          # the Blender-side ground truth for material parity (P6)
```

Run:
- **All assets:** `npm run assets` → `python3 tools/asset-pipeline/build_assets.py`.
- **One asset:** `python3 tools/blender/build_<asset>.py` (as noted in the
  `sovereign_bpy.py` docstring).

The registry of every asset, its build script, output path, tier and tri budget
is [`07_ASSET_REGISTRY.yaml`](07_ASSET_REGISTRY.yaml). The registry and the
`build_*.py` set must stay 1:1.

---

## 2. The shared library — `sovereign_bpy.py` conventions

`build_*.py` scripts must **only** compose primitives and helpers from
`sovereign_bpy.py`. Do not hand-roll geometry or materials in a per-asset script;
if a primitive is missing, add it to the shared lib so every asset benefits and
the film reads as one system.

Provided (see the source for signatures):

- **Scene lifecycle:** `reset()` (empty factory scene, metric units, AgX view
  transform for lookdev), `collection(name)`, `link(obj, col)`.
- **Materials:** `material(...)` factory (Principled BSDF, sRGB→linear via
  `srgb()`), and `mats()` — the **canonical material set** (`M_Obsidian`,
  `M_Graphite`, `M_Titanium`, `M_Ceramic`, `M_SmokedGlass`, `M_Data`,
  `M_Authority`, `M_Warning`, `M_Emergency`, …). `assign(obj, mat, slot)`.
- **Modifiers (the "surgical machining" look):** `bevel()`, `weighted_normal()`,
  `subsurf()`, `solidify()`, `mirror()`, `array()`, `shade_smooth()` (angle-based,
  4.1+ `shade_smooth_by_angle`), `apply_modifiers()`.
- **bmesh primitives:** `box()`, `cyl()`, `tube()` (hollow annulus / bezel),
  `torus()`, and `panel_cut()` (inset+recess for machined seam lines).
- **Export & finishing:** `join_all()`, `set_origin_bottom()`, `export_glb()`,
  `report()`.
- **Lookdev:** `lookdev_render()` — cold three-point Cycles CPU render (white
  key, low cold fill, cyan data rim) for Critic-mode verification without a GPU.

**Palette parity:** `PAL` in `sovereign_bpy.py` mirrors `src/util/palette.ts`.
Colors are authored as sRGB triples and converted to linear with `srgb()` for
Blender's scene-linear color sockets. **If you change a palette value, change it
in both files in the same commit** (see §7 parity).

### Authoring principles (enforced in review)
- **Silhouette + joinery over surface noise.** Detail comes from bevel + weighted
  normals + subdivision + `panel_cut()` seams, **never** from noise/grunge
  textures. (Art Direction §3.)
- **Deterministic.** No random seeds may leak into exported geometry (`reset()`
  starts from factory-empty). A rebuild must be byte-stable enough that diffs are
  meaningful.
- **Low-poly hero parts, precise.** Hit the tri budget in the registry; add
  resolution only where the silhouette needs it.

---

## 3. Neutral-PBR export contract

The web runtime owns look. Blender exports **neutral, un-graded PBR** so the
engine can tone-map and grade consistently across tiers.

Rules (implemented in `export_glb()`):
- **Format:** GLB, `export_format="GLB"`.
- **Apply modifiers on export** (`export_apply=True`) — the shipped mesh is the
  evaluated mesh.
- **Y-up** (`export_yup=True`, glTF convention).
- **Normals + tangents** exported (`export_normals`, `export_tangents=True`) —
  tangents are required for correct normal-mapped and anisotropic look in-engine.
- **Materials EXPORT**, factors only — **no baked textures, no baked view
  transform.** Base color / metallic / roughness / emission travel as glTF PBR
  factors. Cameras and lights are **not** exported (`export_cameras=False`,
  `export_lights=False`) — the engine owns camera and lighting.
- **Draco** mesh compression **on** (`export_draco_mesh_compression_enable=True`,
  level 6) for shipped assets. The runtime loads with a Draco decoder.

### AgX lookdev vs neutral export (critical distinction)
- **Blender uses AgX for lookdev only.** `reset()` and `lookdev_render()` set
  `view_transform = "AgX"` so reference frames look filmic on screen while
  authoring.
- **The exported GLB carries none of that.** glTF stores raw PBR factors; there
  is no view transform in the file. The **web runtime** applies tone-mapping
  (AgX/ACES-style via renderer) + the project grade LUT (`public/assets/lut/`).
- Therefore a lookdev PNG and the in-engine result will differ until the runtime
  grade matches the lookdev intent — that reconciliation is the **parity plan**
  (§7), not a bug to chase blindly.

---

## 4. Texture / KTX2 policy

- **Prefer factor-only materials** (as above). The canonical set is
  parametric — most hero assets need **zero texture maps.**
- **When a map is unavoidable** (e.g. a subtle roughness break on a large vault
  surface), author it, then transcode to **KTX2 (Basis Universal)** for shipping —
  never ship raw PNG/JPG at runtime. KTX2 is GPU-compressed and streams within the
  per-scene budget ([`10_PERFORMANCE_BUDGET.md`](10_PERFORMANCE_BUDGET.md)).
- `vite.config.ts` already refuses to inline `.glb`/`.ktx2`
  (`assetsInlineLimit: 0`) — they stream per scene.

---

## 5. Reference frames (Cycles CPU)

- Every hero/mid asset ships a **lookdev reference frame** rendered with
  `lookdev_render()` (Cycles, **CPU**, denoised, AgX view). CPU keeps it
  reproducible on any machine, including CI, with no GPU dependency.
- The reference frame is the **Blender-side ground truth** for the material
  parity check (§7) and for Critic-mode sign-off (P6).
- **Reference frames are written to `docs/_ref/<asset>.png`** (as-built
  convention — the orchestrator already emits `auth_door.png`,
  `cybernetic_module.png`, `prediction_core.png`, `maintenance_drone.png`, …
  there). They are committed as review artifacts and are **not** shipped to
  `public/`. `BLENDER/0X_*/` and `ASSET_LIBRARY/` remain the working `.blend`/
  block-out space.

---

## 6. Per-asset build script contract

Each `tools/blender/build_<asset>.py`:

1. `from sovereign_bpy import *` (or explicit imports).
2. `reset()` → build named collections.
3. Compose geometry from primitives + modifiers; `assign()` canonical materials.
4. `apply_modifiers()` / `join_all()` as appropriate; `set_origin_bottom()` so the
   asset drops into the engine at a known origin.
5. `export_glb("public/assets/models/<asset>.glb", draco=True)`; `report()`.
6. Optionally `lookdev_render("docs/_ref/<asset>.png", lens=<per art dir>)`.
7. Print the resulting KB (matches the registry `tri_budget`/size expectations).

The script must be **runnable standalone** (`python3 tools/blender/build_<asset>.py`)
and **idempotent** (re-running overwrites the same GLB deterministically).

The orchestrator `tools/asset-pipeline/build_assets.py` runs every `build_*.py`,
then runs the inspect step (§8), then diffs actual tri counts / file sizes against
[`07_ASSET_REGISTRY.yaml`](07_ASSET_REGISTRY.yaml) and fails on regression.

---

## 7. Blender ↔ web material parity plan (Principle P6)

Parity is **controlled**, not hoped for. The plan:

1. **Single palette definition, mirrored:** `PAL` (Blender) ≡ `PALETTE`
   (`palette.ts`). Changed together, in one commit.
2. **Single material vocabulary:** the `mats()` roles map 1:1 to engine
   `Material System` roles (same names: `M_Obsidian` → obsidian role, etc.). The
   engine does not invent materials outside this vocabulary.
3. **Neutral export + runtime grade:** Blender ships raw PBR factors; the engine
   applies one tone-map + one grade LUT for all assets, so parity is a *single*
   reconciliation, not per-asset guesswork.
4. **The reference frame is the target:** for each hero asset, place the engine
   camera/light to match `lookdev_render()`'s cold three-point rig, render an
   in-engine frame, and compare against the Cycles reference. Differences are
   resolved by adjusting the **runtime grade/tone-map**, never by baking look into
   the GLB.
5. **Sign-off:** Critic mode records the side-by-side (Blender ref vs engine
   frame) per hero asset in the review log. "Looks close" is not sign-off; the
   comparison frame is the artifact.

---

## 8. glTF-Transform inspect step

Every build runs a **`gltf-transform inspect`** pass (via the orchestrator) on
each shipped GLB and records:

- triangle count (vs registry `tri_budget`),
- mesh/primitive/draw-call count,
- material count and names (must be within the canonical `mats()` set),
- presence of **tangents**, Draco compression, and **absence** of textures where
  the asset is declared factor-only,
- file size (vs the per-scene streaming budget).

The inspect JSON is the machine-checkable contract between this doc and
[`07_ASSET_REGISTRY.yaml`](07_ASSET_REGISTRY.yaml) / [`10_PERFORMANCE_BUDGET.md`](10_PERFORMANCE_BUDGET.md).
A GLB that inspects outside budget, or introduces a material outside the
vocabulary, fails the build.

> If `gltf-transform` (the `@gltf-transform/cli`) is not yet vendored, the
> orchestrator falls back to a minimal in-repo GLB header/accessor parser that
> reports tri count and material names — the *inspect gate must exist* even before
> the full CLI is wired.
