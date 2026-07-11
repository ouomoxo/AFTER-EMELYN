/**
 * SOVEREIGN//77 — Scene kit.
 * Shared building blocks so each movement keeps ONE center of attention and the
 * infrastructure repeats read as a system. Procedural fallbacks let a scene
 * stand up even before its GLB bundle finishes authoring.
 */
import * as THREE from 'three';
import { PALETTE } from '../../util/palette';
import { makeGlowSprite } from '../materials/Environment';

/** A cold three-point rig anchored on a target. */
export function coldRig(scene: THREE.Scene, target: THREE.Vector3Tuple, keyI = 120) {
  const key = new THREE.SpotLight(0xdfe8ea, keyI, 60, Math.PI / 5, 0.5, 1.0);
  key.position.set(target[0] + 4, target[1] + 6, target[2] + 6);
  key.target.position.set(...target);
  const fill = new THREE.PointLight(0x2a3a44, keyI * 0.16, 50, 2);
  fill.position.set(target[0] - 6, target[1] + 1, target[2] + 3);
  // Cyan rim is a restrained data accent — never a wash.
  const rim = new THREE.PointLight(PALETTE.cyan, keyI * 0.14, 30, 2);
  rim.position.set(target[0] - 1, target[1] + 2, target[2] - 4);
  const amb = new THREE.AmbientLight(0x141c20, 0.55);
  scene.add(key, key.target, fill, rim, amb);
  return { key, fill, rim, amb };
}

/** A streaming field of cyan data particles that drifts past the camera. */
export class DataStream {
  points: THREE.Points;
  private velocities: Float32Array;
  private count: number;
  private bounds: THREE.Vector3;

  constructor(count: number, bounds: THREE.Vector3, color = PALETTE.cyan, size = 0.03) {
    this.count = count;
    this.bounds = bounds;
    const g = new THREE.BufferGeometry();
    const pos = new Float32Array(count * 3);
    this.velocities = new Float32Array(count);
    for (let i = 0; i < count; i++) {
      pos[i * 3] = (Math.random() - 0.5) * bounds.x;
      pos[i * 3 + 1] = (Math.random() - 0.5) * bounds.y;
      pos[i * 3 + 2] = (Math.random() - 0.5) * bounds.z;
      this.velocities[i] = 0.5 + Math.random() * 2.5;
    }
    g.setAttribute('position', new THREE.BufferAttribute(pos, 3));
    const mat = new THREE.PointsMaterial({
      color,
      size,
      map: makeGlowSprite(48, '#' + new THREE.Color(color).getHexString()),
      transparent: true,
      opacity: 0.85,
      depthWrite: false,
      blending: THREE.AdditiveBlending,
    });
    this.points = new THREE.Points(g, mat);
  }

  update(dt: number, dir = new THREE.Vector3(0, 1, 0), speed = 1) {
    const pos = this.points.geometry.getAttribute('position') as THREE.BufferAttribute;
    const arr = pos.array as Float32Array;
    for (let i = 0; i < this.count; i++) {
      const v = this.velocities[i] * speed * dt;
      arr[i * 3] += dir.x * v;
      arr[i * 3 + 1] += dir.y * v;
      arr[i * 3 + 2] += dir.z * v;
      // wrap
      if (Math.abs(arr[i * 3 + 1]) > this.bounds.y / 2) arr[i * 3 + 1] = -Math.sign(dir.y) * this.bounds.y / 2;
      if (Math.abs(arr[i * 3]) > this.bounds.x / 2) arr[i * 3] = -Math.sign(dir.x) * this.bounds.x / 2;
      if (Math.abs(arr[i * 3 + 2]) > this.bounds.z / 2) arr[i * 3 + 2] = -Math.sign(dir.z) * this.bounds.z / 2;
    }
    pos.needsUpdate = true;
  }
}

/** Simple machined module used as a procedural stand-in for infra assets. */
export function machinedModule(w: number, h: number, d: number, metal = PALETTE.graphite): THREE.Group {
  const grp = new THREE.Group();
  const body = new THREE.Mesh(
    new THREE.BoxGeometry(w, h, d),
    new THREE.MeshStandardMaterial({ color: metal, metalness: 1, roughness: 0.5 }),
  );
  grp.add(body);
  // thin data slots
  const slotMat = new THREE.MeshStandardMaterial({
    color: PALETTE.cyan,
    emissive: PALETTE.cyan,
    emissiveIntensity: 1.4,
    roughness: 0.4,
  });
  const rows = Math.max(2, Math.floor(h / 0.25));
  for (let i = 0; i < rows; i++) {
    const slot = new THREE.Mesh(new THREE.BoxGeometry(w * 0.6, 0.02, 0.02), slotMat);
    slot.position.set(0, -h / 2 + 0.15 + i * (h / rows), d / 2);
    grp.add(slot);
  }
  return grp;
}

/**
 * A humanoid point cloud used by the Mirror epilogue — a standing silhouette
 * the subject's data pours into. Not anatomically detailed on purpose: it is a
 * *model of a person*, cold and approximate.
 */
export function humanoidCloud(count: number, color = PALETTE.cyan): THREE.Points {
  const g = new THREE.BufferGeometry();
  const pos = new Float32Array(count * 3);
  const seed = new Float32Array(count);
  const put = (i: number, x: number, y: number, z: number) => {
    pos[i * 3] = x;
    pos[i * 3 + 1] = y;
    pos[i * 3 + 2] = z;
    seed[i] = Math.random();
  };
  for (let i = 0; i < count; i++) {
    const r = Math.random();
    const a = Math.random() * Math.PI * 2;
    if (r < 0.16) {
      // head
      const rr = 0.12 * Math.cbrt(Math.random());
      put(i, Math.cos(a) * rr, 1.62 + Math.sin(Math.random() * Math.PI) * 0.12, Math.sin(a) * rr * 0.8);
    } else if (r < 0.62) {
      // torso
      const y = 0.85 + Math.random() * 0.62;
      const rr = 0.19 * (1 - (y - 0.85) / 1.2);
      put(i, Math.cos(a) * rr, y, Math.sin(a) * rr * 0.55);
    } else if (r < 0.82) {
      // arms
      const side = Math.random() < 0.5 ? -1 : 1;
      const t = Math.random();
      put(i, side * (0.22 + t * 0.34), 1.42 - t * 0.62, (Math.random() - 0.5) * 0.08);
    } else {
      // legs
      const side = Math.random() < 0.5 ? -1 : 1;
      const t = Math.random();
      put(i, side * 0.1, 0.85 - t * 0.85, (Math.random() - 0.5) * 0.08);
    }
  }
  g.setAttribute('position', new THREE.BufferAttribute(pos, 3));
  g.setAttribute('aSeed', new THREE.BufferAttribute(seed, 1));
  const mat = new THREE.PointsMaterial({
    color,
    size: 0.05, // must read as a luminous body at an 85mm portrait distance
    map: makeGlowSprite(48, '#' + new THREE.Color(color).getHexString()),
    transparent: true,
    opacity: 0.95,
    depthWrite: false,
    blending: THREE.AdditiveBlending,
    sizeAttenuation: true,
  });
  return new THREE.Points(g, mat);
}
