/**
 * SOVEREIGN//77 — Motion math.
 * The film's camera and UI never snap. Everything moves with mass and inertia.
 * These helpers are the only sanctioned way to approach a target value.
 */

export const clamp = (v: number, lo = 0, hi = 1) => Math.min(hi, Math.max(lo, v));
export const lerp = (a: number, b: number, t: number) => a + (b - a) * t;
export const invLerp = (a: number, b: number, v: number) =>
  a === b ? 0 : clamp((v - a) / (b - a));
export const smoothstep = (t: number) => {
  t = clamp(t);
  return t * t * (3 - 2 * t);
};
export const smootherstep = (t: number) => {
  t = clamp(t);
  return t * t * t * (t * (t * 6 - 15) + 10);
};

/**
 * Frame-rate-independent damping. `lambda` is the decay constant: higher =
 * snappier. This is the exponential-decay lerp Freya Holmér popularized —
 * unlike a fixed-alpha lerp it behaves identically at 30 or 144 fps.
 */
export const damp = (current: number, target: number, lambda: number, dt: number) =>
  lerp(current, target, 1 - Math.exp(-lambda * dt));

/** Map value from one range to another with clamping + optional easing. */
export const remap = (
  v: number,
  inA: number,
  inB: number,
  outA: number,
  outB: number,
  ease: (t: number) => number = (t) => t,
) => lerp(outA, outB, ease(invLerp(inA, inB, v)));

/** A tiny seeded PRNG (mulberry32) so "system" noise is deterministic per session. */
export function rng(seed: number) {
  let a = seed >>> 0;
  return () => {
    a |= 0;
    a = (a + 0x6d2b79f5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

/** Signature hash → a stable 0..1 seed from a string (for the replica id). */
export function hashSeed(s: string): number {
  let h = 2166136261;
  for (let i = 0; i < s.length; i++) {
    h ^= s.charCodeAt(i);
    h = Math.imul(h, 16777619);
  }
  return h >>> 0;
}
