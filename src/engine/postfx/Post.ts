/**
 * SOVEREIGN//77 — Post FX.
 * RenderPass → restrained UnrealBloom → a single cinematic grade pass
 * (cool-shadow lift, vignette, fine grain, edge chromatic aberration). The
 * renderer supplies ACES tone-mapping; this pass supplies the final grade,
 * kept separate from material data per the color-management plan.
 */
import * as THREE from 'three';
import { EffectComposer } from 'three/examples/jsm/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/examples/jsm/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/examples/jsm/postprocessing/UnrealBloomPass.js';
import { ShaderPass } from 'three/examples/jsm/postprocessing/ShaderPass.js';
import { OutputPass } from 'three/examples/jsm/postprocessing/OutputPass.js';
import type { TierProfile } from '../core/PerformanceGovernor';

const GradeShader = {
  uniforms: {
    tDiffuse: { value: null as THREE.Texture | null },
    uTime: { value: 0 },
    uVignette: { value: 1.05 },
    uGrain: { value: 0.03 },
    uAberration: { value: 0.006 },
    uCoolShadow: { value: new THREE.Color(0x0a1416) },
    uWarmHi: { value: new THREE.Color(0x0d0b08) },
    uFade: { value: 0.0 }, // 0 = normal, 1 = black (scene transitions)
    uCorruption: { value: 0.0 }, // logical glitch amount (prediction/vault)
  },
  vertexShader: /* glsl */ `
    varying vec2 vUv;
    void main() { vUv = uv; gl_Position = projectionMatrix * modelViewMatrix * vec4(position,1.0); }
  `,
  fragmentShader: /* glsl */ `
    precision highp float;
    varying vec2 vUv;
    uniform sampler2D tDiffuse;
    uniform float uTime, uVignette, uGrain, uAberration, uFade, uCorruption;
    uniform vec3 uCoolShadow, uWarmHi;

    float hash(vec2 p){ p = fract(p*vec2(123.34,456.21)); p += dot(p, p+45.32); return fract(p.x*p.y); }

    void main(){
      vec2 uv = vUv;
      // Logical corruption: horizontal band displacement (an EVENT, not decoration)
      float band = 0.0;
      if (uCorruption > 0.001) {
        float row = floor(uv.y * 140.0);
        float n = hash(vec2(row, floor(uTime*12.0)));
        band = (step(0.985 - uCorruption*0.08, n)) * (n-0.5) * uCorruption * 0.06;
      }
      uv.x += band;

      // Chromatic aberration — a whisper, only at the extreme edge (no rainbows).
      vec2 dir = uv - 0.5;
      float edge = smoothstep(0.2, 0.72, length(dir));
      float ab = (uAberration + uCorruption * 0.0016) * edge;
      float r = texture2D(tDiffuse, uv - dir*ab).r;
      float g = texture2D(tDiffuse, uv).g;
      float b = texture2D(tDiffuse, uv + dir*ab).b;
      vec3 col = vec3(r,g,b);

      // Split-tone grade: cool shadows, faintly warm highlights
      float luma = dot(col, vec3(0.299,0.587,0.114));
      col += uCoolShadow * (1.0 - smoothstep(0.0, 0.5, luma));
      col += uWarmHi * smoothstep(0.55, 1.0, luma);

      // Vignette
      float vig = smoothstep(1.15, uVignette*0.35, length(dir)*uVignette);
      col *= mix(0.62, 1.0, vig);

      // Fine sensor grain
      float grain = (hash(uv*vec2(1920.0,1080.0) + uTime) - 0.5) * uGrain;
      col += grain;

      // Transition fade to black
      col *= (1.0 - uFade);

      gl_FragColor = vec4(col, 1.0);
    }
  `,
};

export class Post {
  composer: EffectComposer;
  bloom: UnrealBloomPass;
  grade: ShaderPass;

  constructor(
    renderer: THREE.WebGLRenderer,
    scene: THREE.Scene,
    camera: THREE.Camera,
    size: THREE.Vector2,
    profile: TierProfile,
  ) {
    this.composer = new EffectComposer(renderer);
    this.composer.setSize(size.x, size.y);
    this.composer.addPass(new RenderPass(scene, camera));

    // High threshold: only genuinely emissive pixels (cyan data, white
    // authority) bloom — lit ceramic/metal must NOT smear into white.
    this.bloom = new UnrealBloomPass(size.clone(), profile.bloomStrength, 0.6, 0.92);
    this.bloom.enabled = profile.bloom;
    this.composer.addPass(this.bloom);

    this.grade = new ShaderPass(GradeShader);
    this.composer.addPass(this.grade);

    this.composer.addPass(new OutputPass());
  }

  setScenePass(scene: THREE.Scene, camera: THREE.Camera) {
    // Rebuild the RenderPass target when the active scene swaps.
    const pass = this.composer.passes[0] as RenderPass;
    pass.scene = scene;
    pass.camera = camera;
  }

  applyProfile(profile: TierProfile) {
    this.bloom.enabled = profile.bloom;
    this.bloom.strength = profile.bloomStrength;
  }

  set fade(v: number) {
    this.grade.uniforms.uFade.value = v;
  }
  set corruption(v: number) {
    this.grade.uniforms.uCorruption.value = v;
  }

  resize(w: number, h: number) {
    this.composer.setSize(w, h);
    this.bloom.setSize(w, h);
  }

  render(dt: number, time: number) {
    this.grade.uniforms.uTime.value = time;
    void dt;
    this.composer.render();
  }
}
