# 12 — ACCEPTANCE CRITERIA

> This is the checklist a build is judged against before it can be called done.
> It turns the 10 Constitution principles into **testable checks**, defines
> **per-scene "done,"** and fixes the **verification methods**. Critic mode owns
> this document and records results in [`13_REVIEW_LOG.md`](13_REVIEW_LOG.md).

A check is `PASS` only with evidence (a captured frame, a profile trace, a
recorded run). "Looks fine" is not evidence.

---

## 1. The 10 principles as testable checks

| # | Principle | Test | Pass condition |
|---|-----------|------|----------------|
| P1 | Frozen frame ≠ generic web template | Capture 1 frame per movement (`npm run capture`); blind review | No reviewer identifies it as a web/SaaS template; no nav bar, card grid, centered-hero, or stock gradient present |
| P2 | Worldview survives without neon+glitch | Render each movement with emission + glitch layers disabled | Scene still reads as advanced/future/SOVEREIGN from structure, material, light, composition alone |
| P3 | Every camera move has a reason | Enumerate each move in the shot list; annotate its narrative purpose | Zero moves whose only justification is "looks cool"; each expressible as hold→move→stop with a why |
| P4 | UI conveys events, not decoration | Inspect every HUD element over a run | Every readout changes and maps to a real state; no frozen numbers, no hex-fill, no decorative HUD |
| P5 | Input feels part of the scene | Drive each interactive beat; inspect input path | All input goes input→intent→damped target; no free orbit, no 1:1 tracking, no instant scroll jump |
| P6 | Blender↔web parity is controlled | Side-by-side: Cycles lookdev ref vs in-engine frame per hero asset | Differences are explained by the single runtime grade/tone-map, not per-asset mystery; sign-off recorded |
| P7 | Mobile is its own cut | Run Tier C on a real mid device | Vertical framings are authored (not desktop crops); heavy travel uses prerender/2.5D; 30fps held |
| P8 | Exactly one center per scene | Frame + audio + interaction audit per movement | One focal point, one sound center, one interactive element per beat; no competing second bright/loud point |
| P9 | Tech proven in first 20s | Measure time-to-handshake-interactive + first-impression review | Handshake is live and unmistakably "beyond a normal site" within 20s of navigation |
| P10 | User wants to restart | Post-Epilogue intent (playtest) + second-visit staging present | The reset creates a pull to re-enter; second visit is staged as recognized |

---

## 2. Per-scene "done" definition

A movement is **done** only when all rows are `PASS`.

### PROLOGUE — HANDSHAKE (`/handshake`)
> **Rebuilt 2026-07 (hero slice).** Old flat scanner-panel door replaced by a
> monumental pressure-door environment (wall / portal / thick armored leaves /
> lock dogs / hydraulics / lit tunnel / floor). Evidence: in-engine WebGL2
> captures `docs/_ref/web/hs_{1_establish,3_press,4_open}.png` (landscape tier A)
> and `m_hs_establish.png` (portrait tier C); Blender refs `docs/_ref/door_*.png`.
- [x] First paint is obsidian; **no white flash** — establishing frame is
      near-black (`hs_1_establish.png`, `m_hs_establish.png`).
- [x] `INCOMING COGNITIVE SIGNATURE` shows; cursor becomes a **lagging
      tracking-dot** (visible in every handshake capture).
- [x] Press-and-hold ~2s authenticates; early release aborts and restates —
      `hs_3_press.png` (`AUTHENTICATING`, camera pushed to the eye).
- [x] Black is revealed as a **vast metal door**; one three-beat push-through
      into the tunnel with no visible page load — establishing→push→open reads
      across `hs_1/hs_3/hs_4`; `hs_4_open.png` shows the leaves parted and the
      camera pulled into the glowing eye/tunnel.
- [ ] Keyboard hold + reduced-motion alternative both complete auth (doc 11) —
      *not re-verified after rebuild.*
- [ ] **P9:** interactive within the 20s window — *not timed after rebuild.*
- [~] Lens grammar: **DEVIATION** — reframed from a single 100mm surveillance
      hold to a wide low **establishing** (42mm) that pushes to ~58mm on the
      core, so the monumental architecture + floor scale read (the critic's
      requirement). Cold-observation intent preserved; focal length changed by
      design. Logged in `13_REVIEW_LOG.md`.

### ACT I — CITY NERVOUS SYSTEM (`/infrastructure`)
- [ ] Camera travels through **interior organs**, never neon streets.
- [ ] **Scroll = playhead** at checkpoints 0.0 / 0.25 / 0.6 / 1.0, damped (no
      jump).
- [ ] **World micro-moves when scroll stops** (drones/steam/light).
- [ ] The **vertical data shaft** is the single center at gp 0.6.
- [ ] Correct SYS lines fire per shot list.
- [ ] 22mm scale reads (organs dwarf the subject).

### ACT II — HUMAN REVISION (`/augmentation`)
> **Rebuilt 2026-07 (hero slice).** Old stacked-primitive spine replaced by an
> anatomically-credible surgical augmentation: articulated vertebrae
> (centrum/facets/pedicles/arch/spinous/transverse), hydraulic actuators,
> braided muscle, branching neural conductor, seamed ceramic shells (vent + service
> hatch), asymmetric medical connectors, a finned co-processor. 81.5k tris,
> 370KB Draco (+2048² AO-baked variant, tier A/B). Evidence: in-engine captures
> `docs/_ref/web/mod_{1_assembled,2_explode}.png`, `m_mod.png`; Blender refs
> `docs/_ref/{cybernetic_module,module_assembled,module_memory,cybernetic_module_baked}.png`.
- [x] Module reads as **medical×military×luxury, not a robot** — assembled +
      exploded refs and in-engine captures.
- [x] Drag rotates camera **only within ±14°** — constrained damped orbit in
      `AugmentationScene`, not `OrbitControls` (input→intent→damped target).
- [x] Exploded view separates the named layers in order with labels —
      `mod_2_explode.png` shows dermal shells parted, interior (braided muscle,
      articulated spine, cyan neural, co-processor) revealed, `SPINAL INTERFACE`.
- [ ] Anomaly `VOLUNTARY 41% / OVERRIDE 59%` + classification — code fires at
      progress > 0.82; *anomaly frame not captured yet.*
- [~] Hero fidelity within tri band (81.5k ✓, band 300K–900K scene-wide); **draw
      calls not profiled** after rebuild.

### ACT III — PREDICTION ENGINE (`/prediction`)
- [ ] Circular hall + floating faceted **core** as center; sims orbit it.
- [ ] HUD shows live `EXPECTED CURSOR VECTOR / PREDICTED DWELL TIME / NEXT ACTION
      PROBABILITY` and they actually track the subject.
- [ ] A control **activates before** the subject (pre-emption reads as "your input
      arrived late").
- [ ] Glitches are **only** the five logical events; **no** decorative glitch, no
      strobe (also a doc 11 safety check).

### ACT IV — BLACK VAULT (`/black-vault`)
- [ ] Quiet, classical, symmetrical; reliquary materials (basalt/obsidian/
      titanium/smoked glass/ceramic/brass/fiber) — **not a server room**.
- [ ] Opening the core reveals **faces/memory fragments** (the "deleted noise").
- [ ] UI **shifts corporate → internal debug**; the mask slips (lowercase code).
- [ ] The one reverent light center is the **sarcophagus**.
- [ ] Emotional read is **grief/reverence**, set up before the Epilogue.

### EPILOGUE — MIRROR PROTOCOL (`/mirror`)
- [ ] Human silhouette fills with the subject's **own recorded behaviors**.
- [ ] Readout completes to `COGNITIVE REPLICA: 98.7%` (not 100%).
- [ ] `ACCEPT CONTINUITY / TERMINATE MODEL` — **neither responds immediately**;
      `YOUR RESPONSE WAS ALREADY INCLUDED` prints first.
- [ ] **Music is gone; only the subject's input sounds remain** (doc 09 §5).
- [ ] Returns to a **subtly changed** start; **P10** pull to restart present.
- [ ] Choice is written to second-visit state.

---

## 3. Verification methods

| Method | Tool / how | Gates |
|--------|-----------|-------|
| **Frame capture** | `npm run capture` → `tools/capture/shoot.mjs` (Playwright): one composed frame per movement | P1, P2 (with emission/glitch off), P8, color ratio budget (doc 04) |
| **Color ratio check** | histogram the captured frames against the 55/20/12/7/4/2 budget | Art Direction §1 |
| **Profiling** | dev overlay: fps window, `renderer.info` draw calls/triangles, memory before/after gates | draw ≤160/≤200, tri 300K–900K, eviction works (doc 10) |
| **Low-end** | real mid WebGL2 laptop; step-down observed & graceful | Tier B floor 30fps; sacrifice order preserves the center |
| **Mobile** | real mid phone, portrait | P7 (authored vertical cut, 30fps, prerender/2.5D where declared) |
| **Reduced-motion** | `prefers-reduced-motion: reduce` → Tier D | doc 11 §1; full story legible statically; no flashing |
| **Load-fail** | throttle/block a bundle | gate **holds diegetically**, no spinner, no white flash (doc 10 §2) |
| **Muted** | tab muted / autoplay blocked | all plot legible via text + captions (doc 09 §6, doc 11 §4) |
| **Second visit** | seed the `localStorage` marker | recognition staging (Narrative §5); marker holds only `{visited, replica, lastChoice}`, **no PII** |
| **Privacy audit** | network panel across a full run | **zero** telemetry egress; only the single marker in `localStorage` (World Bible §3) |
| **Keyboard-only** | complete all 6 movements with no pointer | doc 11 §2; visible system-styled focus; no trap |
| **Described Path** | screen reader through the described path | doc 11 §6; standalone-complete narrative; live-region movement changes |

---

## 4. Release gate

A build ships only when:
1. All 10 principle checks (§1) are `PASS` with evidence.
2. All six movements are `done` (§2).
3. All verification methods (§3) pass, including the **privacy audit** (non-negotiable).
4. Build-time budget gates pass (inspect + bundle size, doc 10 §4).
5. Critic mode records sign-off in [`13_REVIEW_LOG.md`](13_REVIEW_LOG.md), naming
   any accepted deviations and the principle they touch.

Any single `FAIL` on a privacy, seizure-safety, or "one center" (P8) check is a
**hard block** — these are not negotiable against schedule.
