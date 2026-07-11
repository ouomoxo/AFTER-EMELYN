/**
 * SOVEREIGN//77 — Post FX (WebGPU / TSL).
 * Built on three/webgpu PostProcessing with a TSL node graph: scene pass →
 * bloom → cinematic grade (edge chromatic aberration, cool-shadow split tone,
 * vignette, sensor grain, transition fade, logical-glitch corruption). Runs on
 * the WebGPU backend where available and the WebGL2 fallback everywhere else.
 */
import * as THREE from 'three/webgpu';
import {
  pass,
  bloom,
  uniform,
  uv,
  vec2,
  vec3,
  vec4,
  float,
  mix,
  dot,
  length,
  smoothstep,
  fract,
  sin,
} from 'three/tsl';
import type { TierProfile } from '../core/PerformanceGovernor';

export class Post {
  postProcessing: THREE.PostProcessing;
  private uTime = uniform(0);
  private uFade = uniform(0);
  private uCorruption = uniform(0);
  private uGrain = uniform(0.02);
  private bloomPass?: ReturnType<typeof bloom>;
  private bloomStrength = 0.5;

  constructor(
    renderer: THREE.WebGPURenderer,
    scene: THREE.Scene,
    camera: THREE.Camera,
    _size: THREE.Vector2,
    profile: TierProfile,
  ) {
    this.bloomStrength = profile.bloom ? profile.bloomStrength : 0;
    this.postProcessing = new THREE.PostProcessing(renderer);
    this.setScenePass(scene, camera);
  }

  /** (Re)build the TSL node graph for the active scene. */
  setScenePass(scene: THREE.Scene, camera: THREE.Camera) {
    const scenePass = pass(scene, camera);
    const sceneColor = scenePass.getTextureNode();

    const uvN = uv();
    const dir = uvN.sub(0.5);
    let col = sceneColor.rgb;

    // --- Bloom: only genuine emissives (high threshold) ---
    this.bloomPass = bloom(scenePass.getTextureNode(), this.bloomStrength, 0.6, 0.92);
    col = col.add(this.bloomPass.rgb);

    // --- Split-tone grade: cool shadows, faintly warm highlights ---
    // Values are small: this operates in linear space (pre output-transform), so
    // additive lifts are amplified by the sRGB curve — a little goes a long way.
    const luma = dot(col, vec3(0.299, 0.587, 0.114));
    col = col.add(vec3(0.006, 0.013, 0.015).mul(smoothstep(0.0, 0.4, luma).oneMinus()));
    col = col.add(vec3(0.014, 0.011, 0.007).mul(smoothstep(0.6, 1.0, luma)));

    // --- Vignette ---
    const vig = mix(float(0.7), float(1.0), smoothstep(1.15, 0.4, length(dir).mul(1.05)));
    col = col.mul(vig);

    // --- Fine sensor grain (a logical glitch briefly intensifies it) ---
    const noise = fract(sin(dot(uvN, vec2(12.9898, 78.233)).add(this.uTime)).mul(43758.5453));
    const grainAmt = this.uGrain.add(this.uCorruption.mul(0.08));
    col = col.add(noise.sub(0.5).mul(grainAmt));

    // --- Corruption flush: a restrained red bias on a glitch event (privilege) ---
    col = col.add(vec3(0.06, 0.0, 0.0).mul(this.uCorruption).mul(noise));

    // --- Transition fade to black ---
    col = col.mul(this.uFade.oneMinus());

    this.postProcessing.outputNode = vec4(col, 1.0);
    this.postProcessing.needsUpdate = true;
  }

  applyProfile(profile: TierProfile) {
    this.bloomStrength = profile.bloom ? profile.bloomStrength : 0;
    if (this.bloomPass) (this.bloomPass as unknown as { strength: { value: number } }).strength.value = this.bloomStrength;
  }

  set fade(v: number) {
    this.uFade.value = v;
  }
  get fade() {
    return this.uFade.value;
  }
  set corruption(v: number) {
    this.uCorruption.value = v;
  }

  resize(_w: number, _h: number) {
    // PostProcessing tracks the renderer size automatically.
  }

  async render(_dt: number, time: number) {
    this.uTime.value = time;
    await this.postProcessing.renderAsync();
  }
}
