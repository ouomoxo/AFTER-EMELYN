# 04 — ART DIRECTION

> The look is **Corporate Monolith × Surgical Technology × Digital Religion.**
> Machined, medical, reverent. Silhouette and joinery over surface noise. If a
> frozen frame could be a generic web/SaaS template, it has failed (Principle P1).

Source of truth for color values: `src/util/palette.ts` (TS) and the `PAL` table
in `tools/blender/sovereign_bpy.py` (Blender). This doc is the *grammar*; those
files are the *values*. Keep them in sync — see [`06_BLENDER_PIPELINE.md`](06_BLENDER_PIPELINE.md) §parity.

---

## 1. Color — ratio budget (enforced)

Color is rationed by **screen area**, not sprinkled. The budget is a hard target
measured on representative frames (see [`12_ACCEPTANCE_CRITERIA.md`](12_ACCEPTANCE_CRITERIA.md)
frame-capture step).

| Role | Name | Hex | Area budget | Meaning (semantic, fixed) |
|------|------|-----|------------:|---------------------------|
| Base void | **Obsidian Black** | `#050506` | **55%** | the void SOVEREIGN lives in |
| Structure | **Cold Graphite** | `#14161a` | **20%** | machined surfaces, mass |
| Light/authority | **Surgical White** | `#e8ecec` | **12%** | the system's authority & key light |
| Data | **Desaturated Cyan** | `#4fd4d0` | **7%** | data flow — **never decorative** |
| Caution | **Warning Amber** | `#e0a038` | **4%** | caution, review, hesitation |
| Danger | **Emergency Red** | `#e0322a` | **2%** | danger / **privilege escalation ONLY** |

Support values (still inside the six-color world, used sparingly): Obsidian Deep
`#020203`, Graphite Light `#282c32`, Surgical Dim `#9aa2a4`, Cyan Deep `#1c6b6a`.

### Semantic grammar (memorize)
- **Cyan = data.** If it glows cyan, it is information moving. Never use cyan for
  "sci-fi accent."
- **White = authority.** SOVEREIGN speaking, system light, the key.
- **Amber = warning.** Review states, hesitation, "are you sure," soft alarms.
- **Red = privilege.** Danger *and* privilege escalation — the rare moments the
  system exposes its real power. Because it is 2% of the frame, it *lands.*

Reference these as intent in code via `SEMANTIC` in `palette.ts`
(`data / authority / warning / danger / dormant`), never as raw hex in UI.

### Color don'ts (anti-cliché)
- **No indiscriminate neon pink/blue.** The palette is desaturated and cold; cyan
  is the only "glow" and it is data.
- **No emission on everything.** Emission means *this is energized information or
  authority.* A glowing edge that means nothing is a bug.
- **No RGB rainbow HUD.** UI is white/cyan/amber/red by grammar, on obsidian.

---

## 2. Typography

Three typefaces, three jobs. No more. Giant repeated English display type is an
anti-cliché — type is **instrumentation**, not wallpaper.

| Role | Family (intent) | Use |
|------|-----------------|-----|
| **Display** | one tight, cold grotesque (e.g. Neue Haas Grotesk / similar) | movement titles, the rare large word. Used *once* per scene at most. |
| **Mono** | one technical monospace (e.g. SF Mono / JetBrains Mono) | all system telemetry, readouts, the "system speaking," debug interface (Act IV). |
| **Body** | one neutral humanist sans (e.g. Inter / system-ui) | the very little running text that exists; captions. |

Rules:
- The **system speaks in mono.** Telemetry, `NEXT ACTION PROBABILITY`, the
  Epilogue readout — all mono, uppercase, wide tracking (`letter-spacing`
  ~0.3–0.42em as in `index.html`).
- Display type appears **small and rarely.** A movement label is a whisper, not a
  billboard. **No full-bleed hero words.**
- Numbers must **mean something and change** (P4). A frozen readout is decoration
  and is forbidden.
- Boot/first-paint copy is already defined in `index.html` (`INITIALIZING
  COGNITIVE INTERFACE`) — match its weight and tracking for continuity.

---

## 3. Materials language

Materials come from real Blender PBR (Principled BSDF, metallic-roughness). The
canonical set lives in `sovereign_bpy.py :: mats()`; use these roles, don't invent
one-off shaders.

| Material role | Blender name | Character | Where |
|---------------|--------------|-----------|-------|
| Obsidian (coated) | `M_Obsidian` | near-black, subtle clearcoat, deep reflection | hero bodies, vault stone accents |
| Obsidian matte | `M_ObsidianMatte` | light-drinking, no highlight | backgrounds, negative space |
| Graphite | `M_Graphite` | machined metal, mid roughness | structure, panels |
| Graphite worn | `M_GraphiteWorn` | slightly used industrial | infrastructure, drones |
| Titanium / polished | `M_Titanium` / `M_TitaniumPolish` | cold precious metal | module frame, vault fittings |
| Ceramic / matte | `M_Ceramic` / `M_CeramicMatte` | surgical white, medical | dermal shell, vault ceramic |
| Brass (oxidized) | `M_Brass` | faint warmth, restraint | vault ritual fittings only |
| Smoked glass | `M_SmokedGlass` | transmissive, dark, ior 1.5 | prediction core, vault covers |
| Carbon | `M_Carbon` | deep matte non-metal | muscle layer, gaskets |
| Data / soft | `M_Data` / `M_DataSoft` | cyan emissive (strong / gentle) | data lines, particles |
| Authority | `M_Authority` | white emissive | system light sources, key readouts |
| Warning / Emergency | `M_Warning` / `M_Emergency` | amber / red emissive | caution / privilege only |

Material principles:
- **Silhouette and joinery over surface noise.** The "surgical machining" look
  comes from **bevel + weighted normals + subtle subdivision + recessed panel
  lines** (see the modifier helpers in `sovereign_bpy.py`), *not* from noise
  textures or grunge maps.
- **Reflection must carry information.** Black metal that only exists to reflect a
  studio HDRI is an anti-cliché. Reflections should reveal the room, the data,
  the one light center — or be killed.
- **Emission is a privilege.** Only data (cyan), authority (white), and
  warning/danger (amber/red) emit. Everything else is lit, not self-lit.
- **The Black Vault palette of matter** (Act IV) is specifically: black basalt,
  polished obsidian, titanium, smoked glass, white ceramic, faintly oxidized
  brass, thin fiber lines. This is the reliquary material set — reverent, not
  server-room.

---

## 4. Lighting language

- **One light center per scene (P8).** Every scene has a single dominant source
  that is *motivated* (a shaft, the core, the sarcophagus glow). Fills are cold
  and low.
- **Key = surgical white; data rim = cyan.** The lookdev rig in `sovereign_bpy.py`
  (`lookdev_render`) encodes this: cold white key, low cold fill, cyan rim. Match
  it in-engine.
- **Darkness is the default.** 55% of the frame is obsidian. Light is carved out
  of black, never flooded.
- **Depth via haze, not fog spam.** A thin volumetric to give shafts of light
  body — subtle, never a smoke-machine.

---

## 5. The anti-cliché rules (the DO-NOT list)

These are enforced at review (Critic mode) and in [`12_ACCEPTANCE_CRITERIA.md`](12_ACCEPTANCE_CRITERIA.md).

1. **No indiscriminate neon pink/blue.**
2. **No glitch everywhere** — glitch only as a *logical* event (Act III rules).
3. **No meaningless HUD numbers** — every readout means something and updates.
4. **No hexagon-pattern spam** — no honeycomb "sci-fi" fill.
5. **No giant repeated English typography** — type is instrumentation.
6. **No black metal that only reflects** — reflections must carry information.
7. **No excess particles** — particles are data or physics, budgeted.
8. **No emission on everything** — emission is data/authority/warning only.
9. **No free-rotate 3D product viewer** — Act II is a clamped 20–30° arc.
10. **No Ready-Player-One holograms** — no floating translucent blue UIs
    hovering in world space for decoration.

### The frozen-frame test (the master gut check)
Pause on any frame. Ask:
- Could this be a generic web/SaaS template? → **fail P1.**
- If I deleted every glowing/glitching element, is it still clearly advanced,
  future, SOVEREIGN? → **must stay yes (P2).**
- Is there exactly one center of attention? → **must be yes (P8).**

If any answer fails, the frame is redesigned, not tweaked.
