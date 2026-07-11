/**
 * EPILOGUE — MIRROR PROTOCOL.
 * A human silhouette assembles from the subject's own recorded behavior. The
 * replica completes. Two choices — ACCEPT CONTINUITY / TERMINATE MODEL — but
 * neither is answered: "YOUR RESPONSE WAS ALREADY INCLUDED." Music is gone;
 * only the subject's input sounds remain. Lens 85mm: a clinical portrait.
 */
import * as THREE from 'three';
import { Scene, type SceneContext } from './Scene';
import type { SceneId } from '../../narrative/acts';
import { PALETTE } from '../../util/palette';
import { clamp, lerp, smoothstep } from '../../util/math';
import { humanoidCloud } from './sceneKit';
import { getState, setState } from '../../state/store';

export class MirrorScene extends Scene {
  id: SceneId = 'mirror';
  private cloud!: THREE.Points;
  private base!: Float32Array;
  private scatter!: Float32Array;
  private assemble = 0;
  private resolved = false;
  private resolveT = 0;
  private enterTime = 0;

  async build(_ctx: SceneContext): Promise<void> {
    this.three.fog = new THREE.FogExp2(0x030405, 0.05);
    this.three.background = new THREE.Color(0x030405);

    const key = new THREE.SpotLight(0xdfe8ea, 30, 20, Math.PI / 6, 0.6, 1.2);
    key.position.set(2, 3, 4);
    key.target.position.set(0, 1, 0);
    this.three.add(key, key.target, new THREE.AmbientLight(0x0a1014, 0.5));

    this.cloud = humanoidCloud(4000, PALETTE.cyan);
    this.three.add(this.cloud);
    const pos = this.cloud.geometry.getAttribute('position') as THREE.BufferAttribute;
    this.base = (pos.array as Float32Array).slice();
    // scattered start positions
    this.scatter = new Float32Array(this.base.length);
    for (let i = 0; i < this.base.length; i += 3) {
      const a = Math.random() * Math.PI * 2;
      const r = 3 + Math.random() * 4;
      this.scatter[i] = Math.cos(a) * r;
      this.scatter[i + 1] = Math.random() * 3;
      this.scatter[i + 2] = Math.sin(a) * r;
    }

    // Listen for the DOM choice + restart triggers.
    window.addEventListener('sovereign:choice', this.onChoice as EventListener);
  }

  private onChoice = (e: Event) => {
    if (this.resolved) return;
    const choice = (e as CustomEvent).detail as 'accept' | 'terminate';
    this.resolved = true;
    this.resolveT = 0;
    setState({ choice, interaction: 'resolved', systemLine: 'YOUR RESPONSE WAS ALREADY INCLUDED' });
  };

  enter(ctx: SceneContext): void {
    // Mobile cut: a human figure is a portrait subject — pull back and drop the
    // look-at so the full silhouette stands head-to-toe in the vertical frame.
    if (ctx.portrait) ctx.camera.hardSet([0, 1.0, 5.6], [0, 0.85, 0], 60);
    else ctx.camera.hardSet([0, 1.2, 4.4], [0, 1.0, 0], 85);
    ctx.camera.posLambda = 0.8;
    ctx.camera.setParallaxLimit(0.12, 0.08);
    ctx.timeline.drive(0);
    setState({
      interaction: 'engaged',
      systemLine: 'BEHAVIORAL MODEL COMPLETE',
      glyphs: ['DECISION LATENCY MAPPED', 'ATTENTION PROFILE MAPPED', 'COGNITIVE REPLICA: 0.0%'],
    });
    // Persist that the subject has now been seen.
    try {
      localStorage.setItem('sovereign.seen', '1');
      localStorage.setItem('sovereign.replica', String(getState().behavior.replica));
    } catch {
      /* storage may be blocked; the film still resolves */
    }
  }

  update(_ctx: SceneContext, dt: number, time: number): void {
    // The replica assembles from the recorded behavior over ~6 real seconds.
    // Driven directly off the wall clock (not a dt-damp) so the figure forms on
    // schedule at any frame rate.
    if (!this.enterTime) this.enterTime = performance.now();
    const elapsed = (performance.now() - this.enterTime) / 1000;
    this.assemble = this.resolved ? 1 : smoothstep(clamp(elapsed / 6));

    const pos = this.cloud.geometry.getAttribute('position') as THREE.BufferAttribute;
    const arr = pos.array as Float32Array;
    for (let i = 0; i < arr.length; i += 3) {
      const breath = Math.sin(time * 1.5 + i) * 0.005;
      arr[i] = lerp(this.scatter[i], this.base[i] + breath, this.assemble);
      arr[i + 1] = lerp(this.scatter[i + 1], this.base[i + 1], this.assemble);
      arr[i + 2] = lerp(this.scatter[i + 2], this.base[i + 2] + breath, this.assemble);
    }
    pos.needsUpdate = true;
    this.cloud.rotation.y = Math.sin(time * 0.1) * 0.15;

    // Replica percentage counts up toward the profiled value.
    const replica = clamp(0.6 + getState().behavior.replica * 0.4) * this.assemble;
    const pct = (replica * 100).toFixed(1);
    if (!this.resolved) {
      setState({ glyphs: ['DECISION LATENCY MAPPED', 'ATTENTION PROFILE MAPPED', `COGNITIVE REPLICA: ${pct}%`] });
      // Reveal the two choices once the model is essentially complete.
      if (this.assemble > 0.9 && getState().interaction !== 'authenticating') {
        setState({ interaction: 'authenticating' }); // "authenticating" == awaiting the (moot) choice
      }
    }

    // After the subject "chooses", hold the line, then loop back — changed.
    if (this.resolved) {
      this.resolveT += dt;
      if (this.resolveT > 3.4) {
        window.dispatchEvent(new CustomEvent('sovereign:restart'));
        this.resolved = false; // guard against repeat
      }
    }
  }

  exit(): void {
    window.removeEventListener('sovereign:choice', this.onChoice as EventListener);
  }
}
