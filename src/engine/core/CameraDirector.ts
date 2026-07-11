/**
 * SOVEREIGN//77 — CameraDirector.
 * Owns the one perspective camera. Scenes hand it targets (position, look-at,
 * lens); the director approaches them with mass. Mouse/drag only perturb the
 * TARGET within director-set limits — never the camera directly. Framing is
 * composed for 2.39:1 but stays legible at 16:9 and vertical (no forced bars).
 */
import * as THREE from 'three';
import { damp } from '../../util/math';

/** Convert a 35mm-equivalent focal length to vertical FOV for a given aspect. */
function lensToFov(focalMM: number, aspect: number): number {
  const sensor = 24; // full-frame height
  const vfov = 2 * Math.atan(sensor / (2 * focalMM)) * (180 / Math.PI);
  // Widen slightly on narrow (portrait) viewports so the subject survives.
  return aspect < 1 ? vfov / Math.max(0.72, aspect) : vfov;
}

export class CameraDirector {
  cam: THREE.PerspectiveCamera;
  private pos = new THREE.Vector3(0, 1.5, 6);
  private look = new THREE.Vector3(0, 1, 0);
  private targetPos = new THREE.Vector3(0, 1.5, 6);
  private targetLook = new THREE.Vector3(0, 1, 0);
  private lens = 40;
  private targetLens = 40;

  /** Parallax the user can add to the target (director-limited per scene). */
  parallax = new THREE.Vector2(0, 0);
  private parallaxAmount = new THREE.Vector2(0.25, 0.14);

  /** Positional damping constant; scenes lower it for heavy, slow moves. */
  posLambda = 1.6;
  lookLambda = 2.2;
  lensLambda = 2.0;

  private breatheT = 0;
  breatheAmt = 0.012;

  constructor(aspect: number) {
    this.cam = new THREE.PerspectiveCamera(lensToFov(this.lens, aspect), aspect, 0.05, 4000);
    this.cam.position.copy(this.pos);
  }

  setLens(focalMM: number) {
    this.targetLens = focalMM;
  }

  /** Distance from the eye to what it is looking at — the DOF focus plane. */
  get focusDistance(): number {
    return this.pos.distanceTo(this.look);
  }

  /** Immediately place the camera (used on scene entry to avoid a long glide). */
  hardSet(pos: THREE.Vector3Tuple, look: THREE.Vector3Tuple, focalMM: number) {
    this.pos.set(...pos);
    this.targetPos.set(...pos);
    this.look.set(...look);
    this.targetLook.set(...look);
    this.lens = focalMM;
    this.targetLens = focalMM;
  }

  setTarget(pos: THREE.Vector3Tuple, look: THREE.Vector3Tuple) {
    this.targetPos.set(...pos);
    this.targetLook.set(...look);
  }

  setParallaxLimit(x: number, y: number) {
    this.parallaxAmount.set(x, y);
  }

  update(dt: number, aspect: number) {
    // Apply user parallax as a small offset on the target (mass absorbs it).
    const px = this.parallax.x * this.parallaxAmount.x;
    const py = this.parallax.y * this.parallaxAmount.y;

    this.pos.x = damp(this.pos.x, this.targetPos.x + px, this.posLambda, dt);
    this.pos.y = damp(this.pos.y, this.targetPos.y + py, this.posLambda, dt);
    this.pos.z = damp(this.pos.z, this.targetPos.z, this.posLambda, dt);

    this.look.x = damp(this.look.x, this.targetLook.x + px * 0.4, this.lookLambda, dt);
    this.look.y = damp(this.look.y, this.targetLook.y + py * 0.4, this.lookLambda, dt);
    this.look.z = damp(this.look.z, this.targetLook.z, this.lookLambda, dt);

    this.lens = damp(this.lens, this.targetLens, this.lensLambda, dt);

    // Breathing: the system is alive even when "still". Disabled by reduced motion.
    this.breatheT += dt;
    const bx = Math.sin(this.breatheT * 0.6) * this.breatheAmt;
    const by = Math.cos(this.breatheT * 0.47) * this.breatheAmt * 0.7;

    this.cam.position.set(this.pos.x + bx, this.pos.y + by, this.pos.z);
    this.cam.lookAt(this.look);
    this.cam.fov = lensToFov(this.lens, aspect);
    this.cam.aspect = aspect;
    this.cam.updateProjectionMatrix();
  }
}
