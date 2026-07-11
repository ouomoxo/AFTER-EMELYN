# 11 — ACCESSIBILITY

> An art piece is not an excuse. SOVEREIGN//77 must be *experienceable* — not
> necessarily identical — for people who use reduced motion, keyboards, captions,
> or screen readers. The design goal is an **equivalent diegetic path**, not a
> stripped "accessible mode" that breaks the fiction.

The through-line: accessibility features are themselves **in-world**. A
reduced-motion visit is the system presenting a "low-stimulus access profile." A
keyboard path is an "input fallback." We never break character to say "accessible
version."

---

## 1. Reduced-motion cut (Tier D)

Triggered by `prefers-reduced-motion: reduce` (already respected in
`index.html`'s boot glyph). Tier D is a **first-class director's cut**, not a
disabled Tier A.

- **Static, composed frames** for each movement instead of camera travel — one
  strong still per beat (the frozen-frame test frames double as these).
- **Minimal transitions:** cross-dissolves only; **no** parallax, no idle
  micro-drift, no camera breath, no exploded-view animation (present the module
  pre-separated with labels).
- **No scroll-as-playhead physics:** movement advances by discrete
  step controls (Next/enter), not damped momentum scrolling.
- **The world still tells the story:** every system line and reveal is present as
  text and static image; nothing that carries plot is motion-only.
- **Prediction/glitch beats (Act III)** are shown as state changes (a record
  visibly redacted, then restored) without flashing or rapid displacement.

Tier D is selected by the Performance Governor from the media query and can also
be chosen manually via the in-world access control (§6).

---

## 2. Keyboard path through all six movements

Every interactive beat has a **non-pointer equivalent**. A keyboard-only subject
can complete the entire film.

| Movement | Pointer interaction | Keyboard equivalent |
|----------|--------------------|--------------------|
| PROLOGUE | press-and-hold ~2s to authenticate | **hold `Space`/`Enter`** for the same duration, or **toggle-press** alternative (§3) |
| ACT I | scroll = playhead | **`↓`/`PageDown`/`Space`** advance the playhead target in beats; `↑`/`PageUp` reverse |
| ACT II | drag within 20–30° arc | **`←`/`→`** nudge azimuth within the clamped arc; `Enter` steps the exploded view |
| ACT III | cursor tracked; control pre-empts | keyboard focus tracked the same way; **`Enter`** on the focused control (the system may still pre-empt it) |
| ACT IV | open the core | **`Enter`/`Space`** on the focused sarcophagus seam |
| EPILOGUE | choose ACCEPT / TERMINATE | **`Tab`** between the two, **`Enter`** to choose (the non-answer plays regardless) |

Rules:
- **Visible focus** styled as a system reticle (surgical white / cyan), never a
  default browser outline, but always present and high-contrast.
- **Logical focus order** matches reading order of the HUD; the one interactive
  element per beat is focusable, decorative HUD is not.
- **No keyboard trap.** `Esc` exposes the in-world access menu (§6) from anywhere.
- The `#stage` canvas is `aria-hidden` (as in `index.html`); all interaction and
  semantics live in the `#interface` DOM layer.

---

## 3. The press-and-hold alternative

Press-and-hold can be difficult (motor impairment, some assistive tech). Provide,
without leaving the fiction:

- **Keyboard hold:** hold `Space`/`Enter` for the same ~2s (with a visible ring).
- **Toggle mode:** a system-offered alternative where a single activation starts
  authentication and a second stops it, or authentication completes on a single
  press after a settable dwell — surfaced as `LOW-DEXTERITY ACCESS PROFILE`.
- **Reduced-motion + this:** in Tier D the hold is replaced by a single
  confirm-press; the ring animates minimally.
- The required hold duration is **configurable** via the access menu and shortened
  on second visit anyway (the system "needs less to re-identify you").

---

## 4. Captions for system lines

- **Every SYS line in [`05_SHOT_LIST.md`](05_SHOT_LIST.md) is on-screen text** in
  the `#interface` layer (mono, per Art Direction) — the film is legible without
  audio by construction.
- Provide a **caption track** for the *non-verbal* audio meaning too: `[low
  machine hum]`, `[data flow intensifies]`, `[silence]`, `[your input sounds]` —
  so the sound-design storytelling (doc 09) is not lost when muted or for
  d/Deaf subjects.
- Captions are toggleable and on by default when the tab is muted/autoplay-blocked.
- Caption styling stays in-world (system readout look) but meets contrast
  guidance (§5).

---

## 5. No seizure-risk flashing; contrast

- **No flashing above 3 flashes/second**, anywhere, on any tier (WCAG 2.3.1). The
  Act III "glitches" are **logical state changes**, not strobe — this is already a
  design rule (doc 05); here it is also a safety rule.
- Telegraph swells and transitions are **smooth**, never percussive strobe or
  full-frame white flashes. `index.html` guarantees no white flash at boot;
  maintain that everywhere.
- **Contrast:** system text (surgical white `#e8ecec` on obsidian `#050506`) is
  very high contrast. Cyan/amber/red readouts must meet ≥4.5:1 against their
  backdrop for any text-carrying element; where a semantic color would fail
  (small red text), pair it with a white label so meaning is never color-only
  (also covers color-blindness — the grammar is reinforced by *position and
  label*, not hue alone).
- **Motion intensity** never spikes without the audio telegraph, so nothing is a
  startle.

---

## 6. Screen-reader stance & the described path

This is an interactive 3D film; a literal DOM-narration of a `WebGPU` canvas is
meaningless. Our stance:

- **The `#stage` canvas is `aria-hidden`.** We do not pretend to narrate pixels.
- We provide a **Described Path**: a screen-reader-navigable, in-world
  document that presents the film as a sequence of **titled sections** (one per
  movement) with:
  - the movement title and the system line(s),
  - a concise prose description of what is seen and what it means,
  - the interactive choice as a real, operable control with an accessible name
    (e.g. "Authenticate", "Advance", "Open the archive", "Accept continuity /
    Terminate model").
- The Described Path is **synchronized** with the visual film for sighted+SR users
  (the current movement's section is exposed via a live region as movements
  change), and also usable **standalone** as a complete narrative experience.
- A **Skip / Enter-Described-Path** control is offered at boot via the access menu
  (`Esc`), announced early in focus order, so no one is forced through motion to
  find it.
- All controls have accessible names and roles; state changes (authenticated,
  layer revealed, choice registered, "response already included") are announced
  via `aria-live="polite"` in the `#interface` layer.

---

## 7. The privacy line is an accessibility & ethics line

The session-only telemetry (cursor/dwell/scroll/latency) that powers the story is
**never** persisted beyond the single second-visit marker, never PII, never sent
anywhere (World Bible §3). This is stated plainly in the access menu so no subject
is deceived about *actual* data collection — the horror is fictional and the data
practice is clean. Do not add analytics that would make the fiction real.

---

## 8. The access menu (`Esc`) — one in-world control surface

A single, keyboard-reachable, screen-reader-first menu, styled as a SOVEREIGN
"ACCESS PROFILE" panel, exposes:

- Reduced-motion (Tier D) toggle,
- Captions toggle,
- Hold-alternative / dwell settings,
- Mute,
- Enter Described Path,
- The privacy statement.

It is reachable from any movement, traps nothing, and returns focus where it left.
