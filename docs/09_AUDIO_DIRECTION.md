# 09 — AUDIO DIRECTION

> Sound is **fully synthesized at runtime via the Web Audio API. There are NO
> audio asset files.** Every tone, room, click and drone is generated from
> oscillators, noise, filters, and convolution built in code. This is a locked
> decision (Constitution §3): it keeps the bundle lean (P9), makes audio
> parametric and reactive to the timeline, and guarantees the "final twist" can
> strip music down to the subject's own input sounds with no asset juggling.

The **Audio Director** subscribes to the `CinematicTimeline` and mixes six
layers. It is a peer of the Camera Director — audio is directed, not decorated.

---

## 1. The six layers

| # | Layer | Synthesis approach | Role |
|---|-------|--------------------|------|
| L1 | **Low-frequency room tone** | filtered noise + low sine bed, per-scene convolution reverb (synth impulse) | the *size* and material of the space; always present, barely conscious |
| L2 | **Real machine physics sound** | additive/FM partials, resonant band-pass on noise, amplitude tied to on-screen motion | coolant, drones, servos, the door — *motivated* by what moves |
| L3 | **Data / system feedback** | short sines/FM blips, granular cyan "data" texture, rate tied to data flow | the sound of information moving (pairs with cyan on screen) |
| L4 | **Musical drone** | slow detuned oscillator stack, evolving filter, no rhythm | emotional temperature; the only "music"; recedes toward the center |
| L5 | **Interface clicks** | tight enveloped impulses, subtle pitch per action | confirmation of *meaningful* interaction only — not every button beeps |
| L6 | **Deliberate silence** | scheduled gain floors / gates | negative space; the loudest tool we have |

L1 and L4 are beds; L2 and L3 are motivated by the scene; L5 is sparse and
earned; L6 is composed, not accidental.

---

## 2. Per-scene sound center (exactly one, per P8)

Each movement has **one** dominant sound center, mirroring its one light/interaction
center. The mix bows to it.

| Movement | Sound center | Dominant layers | Music (L4) |
|----------|--------------|-----------------|------------|
| PROLOGUE | the authentication ring winding | L3 (the sampling), L6 (silence around it) | faint, distant |
| ACT I | the vertical data shaft roar | L2 (machine) + L1 (huge room) | present, awe |
| ACT II | the module's parts separating | L2 (precise servo) + L5 (each layer a soft click) | tense, thin |
| ACT III | the prediction core hum | L3 (data, dense) + L2 | strained, high |
| ACT IV | the sarcophagus stillness | L1 (deep room) + L6 (silence) | dissolving |
| EPILOGUE | the subject's own input sounds | **L5 only** (see §5) | **removed** |

Golden rule of depth: **the closer to SOVEREIGN's center, the more machine sound
(L2/L3) dominates music (L4).** By Act IV the drone is nearly gone; by the
Epilogue there is no music at all. Depth = machine, not melody.

---

## 3. Ducking, telegraph, silence (the three timing rules)

### 3.1 Duck before big transitions
Before every movement gate and every major reveal, **duck the beds (L1/L4)** so
the transition reads. The duck is scheduled ahead of the visual, then released as
the new scene establishes. GSAP/Web Audio `setTargetAtTime` on the layer gains,
cued from `transitionState = 'gate-arming'`.

### 3.2 Telegraph with sub-bass, 100–300ms early
Put a **sub-bass swell (L1/L2) 100–300ms *before* a visual hit** to telegraph it.
The body feels the event a beat before the eye sees it — this is what makes the
door open, the pre-emption, and the sarcophagus unseal feel inevitable rather than
surprising. The lead time is scheduled off the timeline, not reacted to after the
fact.

### 3.3 Silence is composed
- **Not every button beeps.** L5 fires only on *meaningful* interaction
  (authenticate, open the core, the final choice). Inspecting, scrolling, and
  hovering are near-silent — the world tone (L1/L2) is their feedback.
- Use **L6 as punctuation**: a held silence before the Act II anomaly, before the
  Act IV faces, and before the Epilogue "already included." Silence sets up the
  line.

---

## 4. Motivated, reactive mixing

- **L2 amplitude tracks on-screen motion** (drone crossing frame, coolant, the
  door). If nothing is moving, the machine layer is quiet — this reinforces the
  Act I "world keeps micro-moving when scroll stops" (a low L2 bed persists on
  idle so the space never goes dead).
- **L3 rate tracks data flow** — denser fiber pulses and more simulations = more
  data blips. When cyan is on screen, L3 is present; they are the same signal in
  two senses.
- **Telemetry-reactive, session-only:** subtle audio may respond to the subject's
  own input tempo (faster cursor → slightly more L3 activity), using the same
  session-only telemetry buffer (no PII, no network; World Bible §3). This makes
  the subject feel *heard* by the system before they understand why.

---

## 5. The final-twist audio (Epilogue)

The Epilogue's sound design *is* the twist made audible:

1. **Remove music.** L4 is gone by the time the silhouette forms.
2. **Strip to the subject.** The mix reduces to **L5 — but re-cast:** the clicks,
   scrolls, and hold-releases the subject *made across the whole film*, recorded
   session-only, are **played back** as the silhouette fills. The subject literally
   hears their own behavior become the model.
3. **The non-answer.** On the final choice, cut to **L6 (silence)** for ~1.2s
   before `YOUR RESPONSE WAS ALREADY INCLUDED` — the line lands in a vacuum.
4. **The reset.** As the view returns to the start, a single low L1 swell seeds
   the loop, telegraphing (per §3.2) that entering again has already begun.

This is only possible because audio is synthesized and parametric: there is no
"epilogue music stem" to fade — there is a live mix the Director collapses to the
subject's own trace.

---

## 6. Accessibility & muted playback

- The film must be **fully legible with audio muted** (autoplay policies, quiet
  rooms). All system speech is on-screen mono text and captioned
  ([`11_ACCESSIBILITY.md`](11_ACCESSIBILITY.md)); no plot point is audio-only.
- The Audio Director starts **suspended** until a user gesture (the Prologue
  press-and-hold doubles as the audio-unlock gesture) to satisfy browser autoplay
  rules — diegetically, the system "comes online" when you authenticate.
- Provide a persistent, unobtrusive mute affordance styled as a system control
  (not a floating UI chrome button).
- No audio may be used as a seizure/startle device; telegraph swells are smooth,
  not percussive jump-scares.
