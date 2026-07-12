/**
 * SOVEREIGN//77 — IBL environment.
 * Real image-based lighting from a Blender-authored studio HDRI (dark surgical
 * room, shaped softboxes, cyan practicals, overhead rig) so polished titanium /
 * ceramic reflect a believable world. Falls back to a lean procedural studio if
 * the HDRI can't load. Generated once via PMREM and shared by every scene.
 */
import * as THREE from 'three';
import { RGBELoader } from 'three/examples/jsm/loaders/RGBELoader.js';
import { PointsNodeMaterial, type WebGPURenderer } from 'three/webgpu';
import { vec3, uniform } from 'three/tsl';

/** PointsNodeMaterial with an animatable opacity uniform exposed as `.uOpacity`. */
export type GlowPoints = PointsNodeMaterial & { uOpacity: { value: number } };

/** Load the authored studio HDRI → PMREM. Async; the Engine awaits it at boot. */
export async function buildEnvironment(renderer: WebGPURenderer): Promise<THREE.Texture | null> {
  const base = import.meta.env.BASE_URL;
  try {
    const hdr = await new RGBELoader().loadAsync(`${base}assets/env/studio.hdr`);
    hdr.mapping = THREE.EquirectangularReflectionMapping;
    const pmrem = new THREE.PMREMGenerator(renderer as unknown as THREE.WebGLRenderer);
    const env = pmrem.fromEquirectangular(hdr).texture;
    pmrem.dispose();
    hdr.dispose();
    return env;
  } catch (e) {
    console.warn('[SOVEREIGN] studio HDRI unavailable, using procedural studio', e);
    return buildProceduralEnvironment(renderer);
  }
}

/** Fallback: a few emissive panels through PMREM (no HDRI fetch). */
function buildProceduralEnvironment(renderer: WebGPURenderer): THREE.Texture | null {
  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0x040406);
  const panel = (color: number, intensity: number, w: number, h: number, pos: THREE.Vector3Tuple) => {
    const mat = new THREE.MeshBasicMaterial({ color });
    mat.color.multiplyScalar(intensity);
    const m = new THREE.Mesh(new THREE.PlaneGeometry(w, h), mat);
    m.position.set(...pos);
    m.lookAt(0, 0, 0);
    scene.add(m);
  };
  panel(0xdfe6ea, 3.4, 14, 8, [6, 8, 6]);
  panel(0x1a2226, 1.1, 20, 12, [-10, 2, -6]);
  panel(0x123033, 1.0, 10, 3, [-4, -3, 8]);
  panel(0x0a0c10, 1.0, 30, 30, [0, -12, 0]);
  let env: THREE.Texture | null = null;
  try {
    const pmrem = new THREE.PMREMGenerator(renderer as unknown as THREE.WebGLRenderer);
    env = pmrem.fromScene(scene, 0.02).texture;
    pmrem.dispose();
  } catch (e) {
    console.warn('[SOVEREIGN] PMREM unavailable, continuing without IBL', e);
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
