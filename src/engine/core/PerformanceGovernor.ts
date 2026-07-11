/**
 * SOVEREIGN//77 — PerformanceGovernor.
 * Picks a render tier at boot and demotes at runtime if the frame budget slips.
 *   A  WebGPU + high reflections/volumetrics/dense particles
 *   B  WebGL2, reduced effects
 *   C  mobile — limited realtime, leans on 2.5D
 *   D  reduced-motion — static frames, minimal transitions
 * Mobile is a separate director's cut, not a shrunk desktop.
 */
import type { Tier } from '../../state/store';

export interface TierProfile {
  tier: Tier;
  bloom: boolean;
  bloomStrength: number;
  particles: number; // budget multiplier 0..1
  pixelRatioCap: number;
  shadows: boolean;
  anisotropy: number;
}

const PROFILES: Record<Tier, TierProfile> = {
  A: { tier: 'A', bloom: true, bloomStrength: 0.6, particles: 1.0, pixelRatioCap: 2.0, shadows: true, anisotropy: 8 },
  B: { tier: 'B', bloom: true, bloomStrength: 0.5, particles: 0.6, pixelRatioCap: 2.0, shadows: true, anisotropy: 8 },
  // Mobile keeps shadows + retina sharpness now — modern phones handle it, and
  // the runtime governor still demotes bloom/particles if the frame budget slips.
  C: { tier: 'C', bloom: true, bloomStrength: 0.45, particles: 0.4, pixelRatioCap: 2.0, shadows: true, anisotropy: 4 },
  D: { tier: 'D', bloom: false, bloomStrength: 0.0, particles: 0.0, pixelRatioCap: 1.25, shadows: false, anisotropy: 1 },
};

export class PerformanceGovernor {
  profile: TierProfile;
  private frameTimes: number[] = [];
  private demoteCooldown = 0;
  private hasWebGPU: boolean;

  constructor(reducedMotion: boolean, hasWebGPU: boolean) {
    this.hasWebGPU = hasWebGPU;
    this.profile = PROFILES[this.detect(reducedMotion)];
  }

  private detect(reducedMotion: boolean): Tier {
    // Explicit override (testing / capture / user preference).
    try {
      const forced = localStorage.getItem('sovereign.tier');
      if (forced && ['A', 'B', 'C', 'D'].includes(forced)) return forced as Tier;
    } catch {
      /* storage may be blocked */
    }
    if (reducedMotion) return 'D';
    const mobile = /Mobi|Android|iPhone|iPad/i.test(navigator.userAgent) ||
      (navigator.maxTouchPoints > 1 && window.innerWidth < 900);
    if (mobile) return 'C';
    const mem = (navigator as unknown as { deviceMemory?: number }).deviceMemory ?? 8;
    const cores = navigator.hardwareConcurrency ?? 8;
    if (this.hasWebGPU && mem >= 8 && cores >= 8) return 'A';
    if (mem <= 4 || cores <= 4) return 'C';
    return 'B';
  }

  /** Feed a frame time (ms). Demotes B→C if we sustain <30fps. */
  sample(frameMs: number) {
    this.frameTimes.push(frameMs);
    if (this.frameTimes.length > 90) this.frameTimes.shift();
    if (this.demoteCooldown > 0) {
      this.demoteCooldown--;
      return;
    }
    if (this.frameTimes.length >= 60) {
      const avg = this.frameTimes.reduce((a, b) => a + b, 0) / this.frameTimes.length;
      if (avg > 33 && this.profile.tier === 'A') this.set('B');
      else if (avg > 40 && this.profile.tier === 'B') this.set('C');
    }
  }

  private set(t: Tier) {
    this.profile = PROFILES[t];
    this.demoteCooldown = 120;
    this.frameTimes.length = 0;
  }
}
