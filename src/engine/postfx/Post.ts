/**
 * SOVEREIGN//77 — Post FX (WebGPU / TSL).
 * A cinematic "shot on a lens" stack on three/webgpu PostProcessing:
 *   scene → edge chromatic aberration → depth-of-field bokeh → bloom →
 *   AgX-tonemapped split-tone grade → vignette → sensor grain → fade/corruption.
 * DOF + CA are tier-gated (A/B only). Runs on WebGPU where available and the
 * WebGL2 fallback everywhere else. Focus distance tracks the subject each frame.
 */
import * as THREE from 'three/webgpu';
import {
  pass,
  bloom,
  dof,
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
  private uGrain = uniform(0.018);
  private uFocus = uniform(6);      // focus distance (camera→subject), updated per frame
  private uAperture = uniform(0.006); // a whisper: subject dead sharp, only deep bg falls off
  private uMaxblur = uniform(0.4);
  private uCA = uniform(0.0013);    // chromatic aberration at the frame edge
  private bloomPass?: ReturnType<typeof bloom>;
  private bloomStrength = 0.5;
  private lens: boolean;            // DOF + CA on this tier?

  constructor(
    renderer: THREE.WebGPURenderer,
    scene: THREE.Scene,
    camera: THREE.Camera,
    _size: THREE.Vector2,
    profile: TierProfile,
  ) {
    this.bloomStrength = profile.bloom ? profile.bloomStrength : 0;
    this.lens = profile.tier === 'A' || profile.tier === 'B';
    this.postProcessing = new THREE.PostProcessing(renderer);
    this.setScenePass(scene, camera);
  }

  /** (Re)build the TSL node graph for the active scene. */
  setScenePass(scene: THREE.Scene, camera: THREE.Camera) {
    const scenePass = pass(scene, camera);
    const sceneColor = scenePass.getTextureNode();

    const uvN = uv();
    const dir = uvN.sub(0.5);
    const edge = dot(dir, dir); // 0 centre → ~0.5 corner: scales lens artifacts outward

    // --- Lens chromatic aberration: split R/B outward at the frame edge ---
    // Sampling the pass texture at offset UV is the same primitive DOF uses.
    let lensColor = sceneColor;
    if (this.lens) {
      // .uv(node) re-samples the pass texture at an offset (same primitive DOF
      // uses); it exists at runtime but not in the TSL type surface.
      const tex = sceneColor as unknown as { uv: (n: unknown) => { r: unknown; b: unknown } };
      const off = dir.mul(this.uCA.mul(edge).mul(8.0));
      const r = tex.uv(uvN.add(off)).r;
      const g = sceneColor.g;
      const b = tex.uv(uvN.sub(off)).b;
      lensColor = vec4(r, g, b, 1.0) as unknown as typeof sceneColor;
    }

    // --- Depth of field (bokeh): focus tracks the subject; everything else falls
    // off. This is the single strongest "shot on a camera" cue. Tier A/B only. ---
    let focused: typeof sceneColor = lensColor;
    if (this.lens) {
      const viewZ = scenePass.getViewZNode();
      focused = dof(lensColor, viewZ, this.uFocus, this.uAperture, this.uMaxblur) as unknown as typeof sceneColor;
    }

    let col = focused.rgb;

    // --- Bloom: only genuine emissives (high threshold), on the focused image ---
    this.bloomPass = bloom(focused, this.bloomStrength, 0.6, 0.92);
    col = col.add(this.bloomPass.rgb);

    // --- Split-tone grade (linear, pre AgX output-transform): cool shadows,
    // faintly warm highlights. AgX handles the toe/shoulder, so keep lifts small. ---
    const luma = dot(col, vec3(0.299, 0.587, 0.114));
    col = col.add(vec3(0.005, 0.011, 0.013).mul(smoothstep(0.0, 0.4, luma).oneMinus()));
    col = col.add(vec3(0.012, 0.010, 0.006).mul(smoothstep(0.6, 1.0, luma)));

    // --- Vignette (a touch deeper now the lens sells the frame) ---
    const vig = mix(float(0.64), float(1.0), smoothstep(1.15, 0.35, length(dir).mul(1.05)));
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
    // If the lens tier changed (runtime demotion), rebuild without DOF/CA.
    const lens = profile.tier === 'A' || profile.tier === 'B';
    if (lens !== this.lens) this.lens = lens; // next setScenePass (scene change) drops the lens
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
  /** Focus distance (camera → subject), driven per frame by the Engine. */
  set focus(d: number) {
    this.uFocus.value = d;
  }

  resize(_w: number, _h: number) {
    // PostProcessing tracks the renderer size automatically.
  }

  async render(_dt: number, time: number) {
    this.uTime.value = time;
    await this.postProcessing.renderAsync();
  }
}
