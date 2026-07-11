/**
 * SOVEREIGN//77 — Engine.
 * The single render loop, kept entirely outside any UI framework. Owns the
 * renderer, the camera director, the timeline, post FX, the performance
 * governor, and the active scene. Transitions between movements are hidden
 * inside a black/fog beat so asset swaps are never visible.
 */
import * as THREE from 'three';
import { WebGPURenderer } from 'three/webgpu';
import { CameraDirector } from './CameraDirector';
import { CinematicTimeline } from './CinematicTimeline';
import { PerformanceGovernor } from './PerformanceGovernor';
import { AssetLoader } from '../loaders/AssetLoader';
import { Post } from '../postfx/Post';
import { buildEnvironment } from '../materials/Environment';
import { Scene, type SceneContext } from '../scenes/Scene';
import { AudioDirector } from '../../audio/AudioDirector';
import { ACTS, type SceneId, ACT_BY_ID } from '../../narrative/acts';
import { setState, getState } from '../../state/store';
import { clamp, damp } from '../../util/math';

export type SceneFactory = () => Scene;

export class Engine {
  renderer: WebGPURenderer;
  camera: CameraDirector;
  timeline = new CinematicTimeline();
  governor: PerformanceGovernor;
  loader = new AssetLoader();
  audio = new AudioDirector();
  post!: Post;
  env: THREE.Texture | null = null;

  private factories = new Map<SceneId, SceneFactory>();
  private active?: Scene;
  private next?: Scene;
  private clock = new THREE.Clock();
  private size = new THREE.Vector2();
  private rawPointer = new THREE.Vector2();
  private pointer = new THREE.Vector2();
  private pressed = false;
  private transitioning = false;
  private time = 0;
  private onSceneChange?: (id: SceneId) => void;

  constructor(canvas: HTMLElement) {
    const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    const hasWebGPU = 'gpu' in navigator; // intent flag; runtime uses WebGL2 path
    this.governor = new PerformanceGovernor(reduced, hasWebGPU);

    // WebGPU when the device supports it, automatic WebGL2 fallback otherwise —
    // one renderer satisfies "WebGPU 우선, WebGL2 폴백". Init is async (see start()).
    this.renderer = new WebGPURenderer({
      antialias: this.governor.profile.tier !== 'C',
      powerPreference: 'high-performance',
    });
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, this.governor.profile.pixelRatioCap));
    this.renderer.toneMapping = THREE.ACESFilmicToneMapping;
    this.renderer.toneMappingExposure = 0.82; // restrained; the void stays deep
    this.renderer.outputColorSpace = THREE.SRGBColorSpace;
    this.renderer.shadowMap.enabled = this.governor.profile.shadows;
    this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    canvas.appendChild(this.renderer.domElement);

    this.updateSize();
    this.camera = new CameraDirector(this.size.x / this.size.y);

    setState({
      tier: this.governor.profile.tier,
      reducedMotion: reduced,
    });

    window.addEventListener('resize', () => this.updateSize(), { passive: true });
  }

  register(id: SceneId, factory: SceneFactory) {
    this.factories.set(id, factory);
  }

  onScene(cb: (id: SceneId) => void) {
    this.onSceneChange = cb;
  }

  private updateSize() {
    const w = window.innerWidth;
    const h = window.innerHeight;
    this.size.set(w, h);
    this.renderer.setSize(w, h);
    if (this.camera) {
      this.camera.cam.aspect = w / h;
      this.camera.cam.updateProjectionMatrix();
    }
    this.post?.resize(w, h);
  }

  private ctx(): SceneContext {
    return {
      camera: this.camera,
      timeline: this.timeline,
      loader: this.loader,
      audio: this.audio,
      profile: this.governor.profile,
      pointer: this.pointer,
      reducedMotion: getState().reducedMotion,
      secondVisit: getState().secondVisit,
      fx: {
        corruption: (v: number) => {
          if (this.post) this.post.corruption = v;
        },
      },
    };
  }

  /** Boot the first movement and start the loop. */
  async start(first: SceneId = 'handshake') {
    // WebGPURenderer must initialize its device before any render / PMREM use.
    await this.renderer.init();
    this.env = buildEnvironment(this.renderer);
    // Record which backend actually resolved (webgpu vs webgl fallback).
    const backend = (this.renderer.backend as { isWebGPUBackend?: boolean })?.isWebGPUBackend ? 'webgpu' : 'webgl';
    setState({ backend });
    await this.go(first, true);
    this.post = new Post(this.renderer, this.active!.three, this.camera.cam, this.size, this.governor.profile);
    this.loop();
  }

  /** Load + activate a scene. Prefetches the following movement's bundle. */
  async go(id: SceneId, immediate = false) {
    const factory = this.factories.get(id);
    if (!factory) return;
    const scene = factory();
    const ctx = this.ctx();
    await scene.build(ctx);
    scene.three.environment = this.env;
    scene.ready = true;

    if (immediate || !this.active) {
      this.active?.dispose();
      this.active = scene;
      this.applyScene(id);
      scene.enter(ctx);
    } else {
      this.next = scene;
    }

    // Warm the next movement's hero asset so its transition never stalls on a
    // fetch. Maps each movement to the GLB it actually needs (no 404s).
    const def = ACT_BY_ID[id];
    const following = ACTS[def.index + 1];
    const HERO: Partial<Record<SceneId, string[]>> = {
      infrastructure: ['assets/models/server_rack.glb', 'assets/models/maintenance_drone.glb'],
      augmentation: ['assets/models/cybernetic_module.glb'],
      prediction: ['assets/models/prediction_core.glb'],
      'black-vault': ['assets/models/vault_sarcophagus.glb'],
    };
    if (following && HERO[following.id]) this.loader.prefetch(HERO[following.id]!);
  }

  private applyScene(id: SceneId) {
    const def = ACT_BY_ID[id];
    this.timeline.reset(id === 'handshake' || id === 'mirror');
    this.camera.setLens(def.lens);
    this.audio.setScene(id);
    setState({
      scene: id,
      sceneIndex: def.index,
      systemLine: def.systemLine,
      progress: 0,
      shot: 0,
    });
    this.post?.setScenePass(this.active!.three, this.camera.cam);
    this.onSceneChange?.(id);
  }

  /** Cinematic transition to the next movement (called by scenes at the gate). */
  async advance() {
    if (this.transitioning) return;
    const cur = getState().scene;
    const def = ACT_BY_ID[cur];
    const following = ACTS[def.index + 1];
    if (!following) return;
    this.transitioning = true;
    try {
      this.audio.duck(0.15, 0.5);
      this.audio.sub(30, 1.6); // telegraph the move

      // Fade to black over ~700ms, hiding the asset swap.
      await this.fadeTo(1, 0.7);
      await this.go(following.id, false);
      if (this.next) {
        this.active?.dispose();
        this.active = this.next;
        this.next = undefined;
      }
      this.applyScene(following.id);
      this.active!.enter(this.ctx());
      await this.fadeTo(0, 0.9);
    } catch (err) {
      console.error('[SOVEREIGN] advance failed', err);
      if (this.post) this.post.fade = 0; // never leave the frame black
    } finally {
      this.transitioning = false; // the loop must never stay frozen
    }
  }

  /** Jump straight to a movement (menu / keyboard / debug). */
  async jump(id: SceneId) {
    if (this.transitioning) return;
    this.transitioning = true;
    await this.fadeTo(1, 0.5);
    await this.go(id, true);
    await this.fadeTo(0, 0.7);
    this.transitioning = false;
  }

  private fadeTo(target: number, dur: number): Promise<void> {
    return new Promise((resolve) => {
      const start = performance.now();
      const from = this.post ? this.post.fade : 0;
      const tick = () => {
        const t = clamp((performance.now() - start) / (dur * 1000));
        if (this.post) this.post.fade = from + (target - from) * t;
        if (t < 1) requestAnimationFrame(tick);
        else resolve();
      };
      tick();
    });
  }

  setPointer(x: number, y: number) {
    this.rawPointer.set(x, y);
    this.active?.onPointer?.(this.ctx(), x, y);
  }

  setPressed(down: boolean) {
    this.pressed = down;
    this.active?.onPress?.(this.ctx(), down);
  }

  private loop = async () => {
    const dt = Math.min(this.clock.getDelta(), 0.05);
    this.time += dt;
    const frameStart = performance.now();

    // Smooth the pointer (user input → damped target, never direct).
    this.pointer.x = damp(this.pointer.x, this.rawPointer.x, 6, dt);
    this.pointer.y = damp(this.pointer.y, this.rawPointer.y, 6, dt);
    this.camera.parallax.set(this.pointer.x, this.pointer.y);

    const ctx = this.ctx();
    this.timeline.update(dt);
    if (this.active?.ready) {
      this.active.update(ctx, dt, this.time);
      if (this.active.requestAdvance) {
        this.active.requestAdvance = false;
        void this.advance();
      }
    }
    this.camera.update(dt, this.size.x / this.size.y);

    setState({ progress: this.timeline.progress, shot: this.timeline.shot });

    // WebGPU rendering is async; await it so frames never overlap, then schedule
    // the next one.
    if (this.post) await this.post.render(dt, this.time);
    else await this.renderer.renderAsync(this.active!.three, this.camera.cam);

    const frameMs = performance.now() - frameStart;
    this.governor.sample(frameMs);
    if (this.governor.profile.tier !== getState().tier) {
      setState({ tier: this.governor.profile.tier });
      this.post?.applyProfile(this.governor.profile);
    }

    void this.pressed;
    requestAnimationFrame(this.loop);
  };
}
