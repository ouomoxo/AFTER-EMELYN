/**
 * SOVEREIGN//77 — Procedural IBL environment.
 * A cold studio: near-black surround with a few soft emissive panels so the
 * machined metal has something surgical to reflect. Generated once via PMREM
 * and shared by every scene. No HDRI download — keeps the bootstrap lean.
 */
import * as THREE from 'three';
import { PointsNodeMaterial, type WebGPURenderer } from 'three/webgpu';
import { vec3, uniform } from 'three/tsl';

/** PointsNodeMaterial with an animatable opacity uniform exposed as `.uOpacity`. */
export type GlowPoints = PointsNodeMaterial & { uOpacity: { value: number } };

export function buildEnvironment(renderer: WebGPURenderer): THREE.Texture | null {
  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0x040406);

  // Soft cold key panel (surgical white)
  const panel = (color: number, intensity: number, w: number, h: number, pos: THREE.Vector3Tuple) => {
    const geo = new THREE.PlaneGeometry(w, h);
    const mat = new THREE.MeshBasicMaterial({ color });
    mat.color.multiplyScalar(intensity);
    const m = new THREE.Mesh(geo, mat);
    m.position.set(...pos);
    m.lookAt(0, 0, 0);
    scene.add(m);
    return m;
  };

  panel(0xdfe6ea, 3.4, 14, 8, [6, 8, 6]);   // key
  panel(0x1a2226, 1.1, 20, 12, [-10, 2, -6]); // cool fill
  panel(0x123033, 1.0, 10, 3, [-4, -3, 8]);   // faint cyan data bounce
  panel(0x0a0c10, 1.0, 30, 30, [0, -12, 0]);  // floor

  let env: THREE.Texture | null = null;
  try {
    // At runtime `three` is aliased to the WebGPU build, so PMREMGenerator here
    // accepts the WebGPURenderer; the cast only satisfies the classic d.ts.
    const pmrem = new THREE.PMREMGenerator(renderer as unknown as THREE.WebGLRenderer);
    env = pmrem.fromScene(scene, 0.02).texture;
    pmrem.dispose();
  } catch (e) {
    // If PMREM is unavailable on this backend, scenes still render on their own
    // lights — just with less environment reflection.
    console.warn('[SOVEREIGN] PMREM environment unavailable, continuing without IBL', e);
  }
  scene.traverse((o) => {
    const m = o as THREE.Mesh;
    if (m.isMesh) {
      m.geometry.dispose();
      (m.material as THREE.Material).dispose();
    }
  });
  return env;
}

/**
 * A WebGPU-native glowing round point material. Standard PointsMaterial with a
 * canvas map does NOT render on the WebGPU backend, so points use a
 * PointsNodeMaterial whose alpha is a TSL circular falloff on the point-sprite UV.
 */
export function makePointsMaterial(hex: number, size: number, opacity = 0.9): GlowPoints {
  const m = new PointsNodeMaterial() as GlowPoints;
  m.size = size;
  m.sizeAttenuation = true;
  const c = new THREE.Color(hex);
  const uOpacity = uniform(opacity);
  m.colorNode = vec3(c.r, c.g, c.b);
  m.opacityNode = uOpacity;
  m.uOpacity = uOpacity;
  m.transparent = true;
  m.depthWrite = false;
  m.blending = THREE.AdditiveBlending;
  return m;
}

/** A soft radial "data" sprite texture, reused by particle systems. */
export function makeGlowSprite(size = 64, color = '#4fd4d0'): THREE.Texture {
  const c = document.createElement('canvas');
  c.width = c.height = size;
  const ctx = c.getContext('2d')!;
  const g = ctx.createRadialGradient(size / 2, size / 2, 0, size / 2, size / 2, size / 2);
  g.addColorStop(0, color);
  g.addColorStop(0.35, color + 'aa');
  g.addColorStop(1, 'transparent');
  ctx.fillStyle = g;
  ctx.fillRect(0, 0, size, size);
  const tex = new THREE.CanvasTexture(c);
  tex.colorSpace = THREE.SRGBColorSpace;
  return tex;
}
