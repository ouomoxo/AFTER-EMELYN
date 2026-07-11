/**
 * SOVEREIGN//77 — Global state (Zustand vanilla store, no React).
 * The engine writes; the DOM interface subscribes. One source of truth for the
 * narrative machine, the render tier, and the subject's behavioral summary.
 */
import { createStore } from 'zustand/vanilla';
import type { SceneId } from '../narrative/acts';

export type Tier = 'A' | 'B' | 'C' | 'D';
export type TransitionState = 'idle' | 'entering' | 'holding' | 'exiting' | 'gate';
export type InteractionState = 'observing' | 'engaged' | 'authenticating' | 'resolved';

export interface BehavioralSummary {
  /** Total cursor path length in px — "attention energy". */
  cursorTravel: number;
  /** Mean dwell (ms) on interactive targets. */
  meanDwell: number;
  /** Mean decision latency (ms) between prompt and action. */
  decisionLatency: number;
  /** Scroll velocity signature (0..1 normalized). */
  scrollTempo: number;
  /** Idle time accumulated (ms) — hesitation. */
  hesitation: number;
  /** Number of discrete intents issued. */
  intents: number;
  /** Derived 0..1 completion of the cognitive replica. */
  replica: number;
  /** 0..1 confidence of the predictive cursor model (how well it anticipates you). */
  prediction: number;
}

export interface SovereignState {
  booted: boolean;
  scene: SceneId;
  sceneIndex: number;
  /** 0..1 progress within the current scene (the film playhead). */
  progress: number;
  shot: number;
  transition: TransitionState;
  interaction: InteractionState;
  tier: Tier;
  /** Which render backend actually resolved at boot. */
  backend: 'webgpu' | 'webgl';
  reducedMotion: boolean;
  /** Portrait / touch device → the separate mobile director's cut. */
  mobile: boolean;
  muted: boolean;
  audioReady: boolean;
  secondVisit: boolean;
  /** The final mirror choice, once made. */
  choice: 'accept' | 'terminate' | null;
  behavior: BehavioralSummary;
  /** Diegetic system line currently being spoken. */
  systemLine: string;
  /** A queue of transient debug/system glyphs (used by prediction + vault). */
  glyphs: string[];
  /** Debug perf HUD toggle + live stats (for real-device profiling). */
  debug: boolean;
  perf: { fps: number; drawCalls: number; triangles: number };
}

const emptyBehavior: BehavioralSummary = {
  cursorTravel: 0,
  meanDwell: 0,
  decisionLatency: 0,
  scrollTempo: 0,
  hesitation: 0,
  intents: 0,
  replica: 0,
  prediction: 0,
};

export const store = createStore<SovereignState>(() => ({
  booted: false,
  scene: 'handshake',
  sceneIndex: 0,
  progress: 0,
  shot: 0,
  transition: 'idle',
  interaction: 'observing',
  tier: 'B',
  backend: 'webgl',
  reducedMotion: false,
  mobile: false,
  muted: false,
  audioReady: false,
  secondVisit: false,
  choice: null,
  behavior: { ...emptyBehavior },
  systemLine: '',
  glyphs: [],
  debug: false,
  perf: { fps: 0, drawCalls: 0, triangles: 0 },
}));

// Convenience helpers (avoid importing setState everywhere).
export const setState = store.setState;
export const getState = store.getState;
export const subscribe = store.subscribe;

export function patchBehavior(p: Partial<BehavioralSummary>) {
  store.setState((s) => ({ behavior: { ...s.behavior, ...p } }));
}
