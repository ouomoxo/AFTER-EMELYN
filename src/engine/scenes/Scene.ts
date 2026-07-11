/**
 * SOVEREIGN//77 — Scene base.
 * Each movement owns its own THREE.Scene (clean isolation + disposal). The
 * Engine swaps which scene the composer renders. A scene declares its lens,
 * camera choreography, interaction, and the ONE center of attention.
 */
import * as THREE from 'three';
import type { CameraDirector } from '../core/CameraDirector';
import type { CinematicTimeline } from '../core/CinematicTimeline';
import type { AssetLoader } from '../loaders/AssetLoader';
import type { TierProfile } from '../core/PerformanceGovernor';
import type { AudioDirector } from '../../audio/AudioDirector';
import type { SceneId } from '../../narrative/acts';

export interface SceneContext {
  camera: CameraDirector;
  timeline: CinematicTimeline;
  loader: AssetLoader;
  audio: AudioDirector;
  profile: TierProfile;
  /** Normalized pointer −1..1, already smoothed. */
  pointer: THREE.Vector2;
  /** Whether reduced-motion is active (Tier D). */
  reducedMotion: boolean;
  /** Portrait / touch device → scenes reframe for the vertical cut. */
  portrait: boolean;
  /** Whether this is a returning subject. */
  secondVisit: boolean;
  /** Post-FX hooks a scene may drive (logical glitch, manual fade). */
  fx: {
    corruption: (v: number) => void;
  };
}

export abstract class Scene {
  abstract id: SceneId;
  three = new THREE.Scene();
  /** Set true once build() resolves. */
  ready = false;
  /** Emitted when the scene wants the Engine to advance to the next movement. */
  requestAdvance = false;

  protected env?: THREE.Texture;

  abstract build(ctx: SceneContext): Promise<void>;
  abstract enter(ctx: SceneContext): void;
  abstract update(ctx: SceneContext, dt: number, time: number): void;

  /** Optional pointer/press hooks (handshake, augmentation, prediction, mirror). */
  onPress?(ctx: SceneContext, down: boolean): void;
  onPointer?(ctx: SceneContext, x: number, y: number): void;

  exit(_ctx: SceneContext): void {}

  dispose() {
    const freeMat = (mat: THREE.Material) => {
      // Dispose any textures the material holds (canvas glow sprites leak otherwise).
      for (const v of Object.values(mat) as unknown[]) {
        if (v && (v as THREE.Texture).isTexture) (v as THREE.Texture).dispose();
      }
      mat.dispose();
    };
    this.three.traverse((o) => {
      // Covers Mesh, Points, Sprite, Line — anything with geometry/material.
      const g = (o as THREE.Mesh).geometry as THREE.BufferGeometry | undefined;
      const mat = (o as THREE.Mesh).material as THREE.Material | THREE.Material[] | undefined;
      g?.dispose?.();
      if (Array.isArray(mat)) mat.forEach(freeMat);
      else if (mat) freeMat(mat);
    });
    this.three.clear();
  }
}
