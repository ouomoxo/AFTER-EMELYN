/**
 * SOVEREIGN//77 — AssetLoader.
 * Streams GLB scene bundles (Draco-compressed) per movement. Assets load in the
 * PRIOR scene so a transition never stalls on a fetch. Materials come in as
 * neutral PBR; the scene's material system + the grade give them the final look.
 */
import * as THREE from 'three';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
import { DRACOLoader } from 'three/examples/jsm/loaders/DRACOLoader.js';

export interface LoadedAsset {
  scene: THREE.Group;
  parts: Record<string, THREE.Object3D>;
}

export class AssetLoader {
  private gltf: GLTFLoader;
  private cache = new Map<string, Promise<LoadedAsset>>();

  constructor() {
    const draco = new DRACOLoader();
    // Decoder is vendored into /public/draco — never fetched from a CDN, so the
    // film boots on restricted networks and offline.
    draco.setDecoderPath('draco/');
    draco.setDecoderConfig({ type: 'wasm' });
    this.gltf = new GLTFLoader();
    this.gltf.setDRACOLoader(draco);
  }

  load(url: string): Promise<LoadedAsset> {
    if (this.cache.has(url)) return this.cache.get(url)!;
    const p = new Promise<LoadedAsset>((resolve, reject) => {
      this.gltf.load(
        url,
        (g) => {
          const parts: Record<string, THREE.Object3D> = {};
          g.scene.traverse((o) => {
            if (o.name) parts[o.name] = o;
            const mesh = o as THREE.Mesh;
            if (mesh.isMesh) {
              mesh.castShadow = true;
              mesh.receiveShadow = true;
              const mat = mesh.material as THREE.MeshStandardMaterial;
              if (mat && 'envMapIntensity' in mat) mat.envMapIntensity = 1.0;
            }
          });
          resolve({ scene: g.scene, parts });
        },
        undefined,
        (err) => reject(err),
      );
    });
    this.cache.set(url, p);
    return p;
  }

  /** Warm a set of URLs without blocking. */
  prefetch(urls: string[]) {
    urls.forEach((u) => void this.load(u).catch(() => {}));
  }
}
