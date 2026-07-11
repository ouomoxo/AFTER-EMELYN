/**
 * SOVEREIGN//77 — CinematicTimeline.
 * The single playhead of the film. Scroll/drag/click DO NOT move it directly;
 * they set `target`, and the timeline damps toward it with mass. This is what
 * makes the experience feel like film playback rather than a scrollbar.
 */
import { clamp, damp } from '../../util/math';

export interface CinematicState {
  act: number;
  shot: number;
  localTime: number;
  globalProgress: number;
  interactionState: string;
  transitionState: string;
}

export class CinematicTimeline {
  /** Where the film wants to be (0..1 within the current scene). */
  target = 0;
  /** Where the film actually is — always chasing target. */
  progress = 0;
  /** Seconds elapsed inside the current scene. */
  localTime = 0;
  /** Current shot index, derived from progress via shot boundaries. */
  shot = 0;
  /** How eager the playhead is to reach target. Scenes may retune this. */
  responsiveness = 2.4;
  /** When true (e.g. handshake), progress is driven by script, not input. */
  scripted = false;

  private shotBoundaries: number[] = [0, 0.25, 0.6, 1.0];

  reset(scripted = false) {
    this.target = 0;
    this.progress = 0;
    this.localTime = 0;
    this.shot = 0;
    this.scripted = scripted;
  }

  setShotBoundaries(b: number[]) {
    this.shotBoundaries = b;
  }

  /** Nudge the target by a normalized delta (from the Input Interpreter). */
  nudge(delta: number) {
    if (this.scripted) return;
    this.target = clamp(this.target + delta);
  }

  setTarget(t: number) {
    this.target = clamp(t);
  }

  /** Script-drive the playhead directly (handshake / mirror / transitions). */
  drive(progress: number) {
    this.progress = clamp(progress);
    this.target = this.progress;
  }

  update(dt: number) {
    this.localTime += dt;
    if (!this.scripted) {
      this.progress = damp(this.progress, this.target, this.responsiveness, dt);
    }
    // derive shot
    let s = 0;
    for (let i = 0; i < this.shotBoundaries.length; i++) {
      if (this.progress >= this.shotBoundaries[i]) s = i;
    }
    this.shot = s;
  }

  /** True once the playhead has effectively reached the end (gate condition). */
  get atGate() {
    return this.progress > 0.985 && this.target > 0.985;
  }

  snapshot(act: number, interaction: string, transition: string): CinematicState {
    return {
      act,
      shot: this.shot,
      localTime: this.localTime,
      globalProgress: this.progress,
      interactionState: interaction,
      transitionState: transition,
    };
  }
}
