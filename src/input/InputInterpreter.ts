/**
 * SOVEREIGN//77 — Input Interpreter + Behavioral Recorder.
 * Raw input is never wired to the camera or timeline directly. It becomes an
 * INTENT (a target nudge) and, at the same time, a behavioral sample. The
 * recorder is the quiet spine of the twist: the subject is being profiled the
 * whole time. Session-only — nothing leaves the browser.
 */
import type { Engine } from '../engine/core/Engine';
import { getState, patchBehavior, setState } from '../state/store';
import { clamp } from '../util/math';

export class InputInterpreter {
  private lastMove = performance.now();
  private lastPos = { x: 0, y: 0 };
  private travel = 0;
  private scrollTempo = 0;
  private hesitation = 0;
  private intents = 0;
  private dwellStart = 0;
  private dwellTotal = 0;
  private dwellCount = 0;
  private promptAt = 0;
  private latencySum = 0;
  private latencyCount = 0;
  private dragging = false;
  private dragStartX = 0;
  private raf = 0;
  // Predictive model of the subject: a smoothed velocity the system projects
  // AHEAD of the real cursor. Its confidence (lead + lock) grows as the replica
  // completes — the ghost starts vague and ends eerily on-target.
  private velX = 0;
  private velY = 0;
  private predX = 0;
  private predY = 0;
  private hit = 0; // running "how close was the last prediction" 0..1

  constructor(private engine: Engine, private root: HTMLElement) {}

  attach() {
    const opt = { passive: false } as AddEventListenerOptions;
    window.addEventListener('pointermove', this.onMove, { passive: true });
    window.addEventListener('pointerdown', this.onDown);
    window.addEventListener('pointerup', this.onUp);
    window.addEventListener('wheel', this.onWheel, opt);
    window.addEventListener('keydown', this.onKey);
    // Touch: vertical swipe = scrub, tap-hold = press.
    window.addEventListener('touchmove', this.onTouch, opt);
    window.addEventListener('touchend', this.onTouchEnd);
    this.tick();
  }

  detach() {
    window.removeEventListener('pointermove', this.onMove);
    window.removeEventListener('pointerdown', this.onDown);
    window.removeEventListener('pointerup', this.onUp);
    window.removeEventListener('wheel', this.onWheel);
    window.removeEventListener('keydown', this.onKey);
    window.removeEventListener('touchmove', this.onTouch);
    window.removeEventListener('touchend', this.onTouchEnd);
    cancelAnimationFrame(this.raf);
  }

  /** Call when the system poses a choice, to measure decision latency. */
  markPrompt() {
    this.promptAt = performance.now();
  }

  private registerAction() {
    if (this.promptAt) {
      this.latencySum += performance.now() - this.promptAt;
      this.latencyCount++;
      this.promptAt = 0;
    }
    this.intents++;
  }

  private onMove = (e: PointerEvent) => {
    const nx = (e.clientX / window.innerWidth) * 2 - 1;
    const ny = -((e.clientY / window.innerHeight) * 2 - 1);
    this.engine.setPointer(nx, ny);

    const now = performance.now();
    const dt = Math.max(8, now - this.lastMove);
    const dx = e.clientX - this.lastPos.x;
    const dy = e.clientY - this.lastPos.y;
    // Score how well the LAST prediction anticipated where the cursor actually
    // went (before we move the model on) — the system "learning" the subject.
    const err = Math.hypot(this.predX - e.clientX, this.predY - e.clientY);
    this.hit = this.hit * 0.94 + clamp(1 - err / 240) * 0.06;
    // Smoothed velocity in px/ms — the basis of the projection.
    const k = 0.4;
    this.velX = this.velX * (1 - k) + (dx / dt) * k;
    this.velY = this.velY * (1 - k) + (dy / dt) * k;
    this.travel += Math.hypot(dx, dy);
    this.lastPos = { x: e.clientX, y: e.clientY };
    this.lastMove = now;

    if (this.dragging) {
      const drag = (e.clientX - this.dragStartX) / window.innerWidth;
      // Horizontal drag scrubs the timeline (director-limited feel via damping).
      this.engine.timeline.nudge(drag * 0.02);
      this.dragStartX = e.clientX;
    }

    // Publish the cursor for the diegetic tracking dot.
    this.root.style.setProperty('--cx', `${e.clientX}px`);
    this.root.style.setProperty('--cy', `${e.clientY}px`);
  };

  private onDown = (e: PointerEvent) => {
    this.dragging = true;
    this.dragStartX = e.clientX;
    this.dwellStart = performance.now();
    this.engine.setPressed(true);
    this.registerAction();
  };

  private onUp = () => {
    this.dragging = false;
    if (this.dwellStart) {
      this.dwellTotal += performance.now() - this.dwellStart;
      this.dwellCount++;
      this.dwellStart = 0;
    }
    this.engine.setPressed(false);
  };

  private onWheel = (e: WheelEvent) => {
    e.preventDefault();
    const d = clamp(e.deltaY / 900, -0.08, 0.08);
    this.engine.timeline.nudge(d);
    this.scrollTempo = this.scrollTempo * 0.9 + Math.abs(d) * 0.1;
    this.registerAction();
  };

  private lastTouchY: number | null = null;
  private onTouch = (e: TouchEvent) => {
    if (e.touches.length === 1) {
      e.preventDefault();
      const t = e.touches[0];
      const nx = (t.clientX / window.innerWidth) * 2 - 1;
      const ny = -((t.clientY / window.innerHeight) * 2 - 1);
      this.engine.setPointer(nx, ny);
      // Vertical swipe scrubs the film playhead (the mobile cut's scroll).
      if (this.lastTouchY !== null) {
        const dy = this.lastTouchY - t.clientY; // swipe up → advance
        this.engine.timeline.nudge((dy / window.innerHeight) * 1.1);
        this.scrollTempo = this.scrollTempo * 0.9 + Math.abs(dy / window.innerHeight) * 0.1;
      }
      this.lastTouchY = t.clientY;
    }
  };
  private onTouchEnd = () => {
    this.lastTouchY = null;
  };

  private onKey = (e: KeyboardEvent) => {
    // Accessibility path: keyboard walks the film.
    if (e.key === 'ArrowDown' || e.key === 'ArrowRight' || e.key === ' ') {
      this.engine.timeline.nudge(0.12);
      this.registerAction();
    } else if (e.key === 'ArrowUp' || e.key === 'ArrowLeft') {
      this.engine.timeline.nudge(-0.12);
    } else if (e.key === 'Enter') {
      this.engine.setPressed(true);
      setTimeout(() => this.engine.setPressed(false), 2100); // auto press-hold
    } else if (e.key >= '1' && e.key <= '6') {
      // debug/menu jump handled by narrative director via custom event
      window.dispatchEvent(new CustomEvent('sovereign:jump', { detail: Number(e.key) - 1 }));
    } else if (e.key === 'd' || e.key === 'D') {
      setState({ debug: !getState().debug });
    }
  };

  private tick = () => {
    this.raf = requestAnimationFrame(this.tick);
    const now = performance.now();
    const idle = now - this.lastMove;
    if (idle > 500) this.hesitation += 16;

    // --- Predictive ghost cursor: project the subject's motion ahead. ---
    // Velocity bleeds off when the cursor rests, so the ghost settles onto it.
    if (idle > 50) {
      this.velX *= 0.9;
      this.velY *= 0.9;
    }
    const replica = getState().behavior.replica;
    // Confidence rises with the replica AND with the model's recent accuracy —
    // the lead grows and the ghost locks tighter the longer it watches you.
    const conf = clamp(0.14 + replica * 0.7 + this.hit * 0.25);
    const leadMs = 165 * conf; // how far ahead the system projects you
    const targetPX = this.lastPos.x + this.velX * leadMs;
    const targetPY = this.lastPos.y + this.velY * leadMs;
    // Track tightly so the projection actually LEADS the cursor (anticipation),
    // rather than lagging behind it during motion.
    this.predX += (targetPX - this.predX) * 0.5;
    this.predY += (targetPY - this.predY) * 0.5;
    this.root.style.setProperty('--px', `${this.predX}px`);
    this.root.style.setProperty('--py', `${this.predY}px`);
    this.root.style.setProperty('--pconf', conf.toFixed(3));

    const meanDwell = this.dwellCount ? this.dwellTotal / this.dwellCount : 0;
    const latency = this.latencyCount ? this.latencySum / this.latencyCount : 0;

    // Replica completion grows with engagement across the film (0..1).
    const engaged =
      clamp(this.travel / 26000) * 0.34 +
      clamp(this.intents / 24) * 0.34 +
      clamp(getState().sceneIndex / 5) * 0.32;

    patchBehavior({
      cursorTravel: this.travel,
      meanDwell,
      decisionLatency: latency,
      scrollTempo: clamp(this.scrollTempo * 12),
      hesitation: this.hesitation,
      intents: this.intents,
      replica: clamp(engaged),
      prediction: clamp(0.14 + clamp(engaged) * 0.7 + this.hit * 0.25),
    });
  };
}
