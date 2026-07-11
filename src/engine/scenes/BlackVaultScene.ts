/**
 * ACT IV — BLACK VAULT.
 * The most advanced place is the quietest. A black-stone sanctuary, deliberate
 * symmetry, a data sarcophagus at the axis. Opening it releases the memory it
 * claimed was noise — human choice, failure, feeling. The interface degrades
 * from corporate to internal debug. Lens 35mm: reverent, architectural.
 */
import * as THREE from 'three';
import { Scene, type SceneContext } from './Scene';
import type { SceneId } from '../../narrative/acts';
import { PALETTE } from '../../util/palette';
import { damp, lerp, remap, smoothstep } from '../../util/math';
import { makeGlowSprite } from '../materials/Environment';
import { setState } from '../../state/store';

export class BlackVaultScene extends Scene {
  id: SceneId = 'black-vault';
  private sarc?: THREE.Object3D;
  private lid?: THREE.Object3D;
  private lidBaseY = 0;
  private fragments!: THREE.Points;
  private fragMat?: THREE.PointsMaterial;
  private opened = false;
  private uiShifted = false;

  async build(ctx: SceneContext): Promise<void> {
    this.three.fog = new THREE.FogExp2(0x020203, 0.035);
    this.three.background = new THREE.Color(0x020203);

    // Reverent low light — a single shaft from above, symmetric fills.
    const shaft = new THREE.SpotLight(0xdfe8ea, 60, 40, Math.PI / 8, 0.7, 1.2);
    shaft.position.set(0, 12, 0.001);
    shaft.target.position.set(0, 0, 0);
    this.three.add(shaft, shaft.target);
    const amb = new THREE.AmbientLight(0x0a0e12, 0.6);
    const brass = new THREE.PointLight(0xb98a3a, 8, 18, 2);
    brass.position.set(0, 1.4, 3);
    this.three.add(amb, brass);

    // Black basalt hall — symmetric columns + floor.
    const stone = new THREE.MeshStandardMaterial({ color: 0x070708, metalness: 0.1, roughness: 0.75 });
    const floor = new THREE.Mesh(new THREE.CircleGeometry(20, 64), new THREE.MeshStandardMaterial({ color: 0x050506, metalness: 0.3, roughness: 0.5 }));
    floor.rotation.x = -Math.PI / 2;
    this.three.add(floor);
    for (let i = 0; i < 10; i++) {
      const a = (i / 10) * Math.PI * 2;
      const col = new THREE.Mesh(new THREE.BoxGeometry(0.6, 12, 0.6), stone);
      col.position.set(Math.cos(a) * 7, 6, Math.sin(a) * 7);
      this.three.add(col);
    }
    // ceremonial thin cyan floor line (the one restrained data element)
    const line = new THREE.Mesh(new THREE.RingGeometry(2.2, 2.24, 64), new THREE.MeshStandardMaterial({ color: PALETTE.cyan, emissive: PALETTE.cyan, emissiveIntensity: 1.5 }));
    line.rotation.x = -Math.PI / 2;
    line.position.y = 0.02;
    this.three.add(line);

    try {
      const a = await ctx.loader.load('assets/models/vault_sarcophagus.glb');
      this.sarc = a.scene;
      this.sarc.position.set(0, 0, 0);
      this.three.add(this.sarc);
      this.lid = a.parts['Lid'];
      if (this.lid) this.lidBaseY = this.lid.position.y;
    } catch {
      const box = new THREE.Mesh(new THREE.BoxGeometry(2.6, 0.7, 1.1), new THREE.MeshStandardMaterial({ color: 0x0a0a0c, metalness: 0.4, roughness: 0.4 }));
      box.position.y = 0.5;
      this.three.add(box);
      const lid = new THREE.Mesh(new THREE.BoxGeometry(2.62, 0.12, 1.12), new THREE.MeshStandardMaterial({ color: 0x0c0c0f, metalness: 0.5, roughness: 0.35 }));
      lid.position.y = 0.9;
      this.lid = lid;
      this.lidBaseY = lid.position.y;
      this.three.add(lid);
    }

    // Memory fragments held inside — faces/choices/feelings, as cyan-white motes.
    const N = Math.floor(1200 * ctx.profile.particles + 200);
    const g = new THREE.BufferGeometry();
    const pos = new Float32Array(N * 3);
    for (let i = 0; i < N; i++) {
      pos[i * 3] = (Math.random() - 0.5) * 1.8;
      pos[i * 3 + 1] = 0.5 + Math.random() * 0.3;
      pos[i * 3 + 2] = (Math.random() - 0.5) * 0.8;
    }
    g.setAttribute('position', new THREE.BufferAttribute(pos, 3));
    this.fragMat = new THREE.PointsMaterial({ color: 0xbfe9e6, size: 0.02, map: makeGlowSprite(32, '#bfe9e6'), transparent: true, opacity: 0, depthWrite: false, blending: THREE.AdditiveBlending });
    this.fragments = new THREE.Points(g, this.fragMat);
    this.three.add(this.fragments);
  }

  enter(ctx: SceneContext): void {
    ctx.camera.hardSet([0, 1.5, 8], [0, 0.9, 0], 35);
    ctx.camera.posLambda = 0.9; // heavy, slow, reverent
    ctx.camera.lookLambda = 1.4;
    ctx.camera.setParallaxLimit(0.22, 0.14);
    setState({ interaction: 'observing', systemLine: 'ARCHIVE // SEALED', glyphs: [] });
  }

  update(ctx: SceneContext, dt: number, time: number): void {
    const p = ctx.timeline.progress;

    // Slow approach, then rise to look into the opened core.
    const camZ = remap(p, 0, 0.7, 8, 3.4, smoothstep);
    const camY = remap(p, 0.5, 1, 1.5, 2.4, smoothstep);
    ctx.camera.setTarget([ctx.pointer.x * 0.6, camY, camZ], [0, lerp(0.9, 1.1, p), 0]);

    // Past halfway, the lid opens (slides up + back) and memory pours out.
    if (p > 0.5) {
      const open = smoothstep(remap(p, 0.5, 0.9, 0, 1));
      if (this.lid) {
        this.lid.position.y = this.lidBaseY + open * 0.9;
        this.lid.position.z = -open * 1.2;
      }
      if (this.fragMat) this.fragMat.opacity = damp(this.fragMat.opacity, open * 0.9, 2, dt);
      // fragments rise and disperse
      const arr = (this.fragments.geometry.getAttribute('position') as THREE.BufferAttribute).array as Float32Array;
      for (let i = 0; i < arr.length; i += 3) {
        arr[i + 1] += dt * 0.12 * open;
        arr[i] += Math.sin(time + i) * dt * 0.02 * open;
      }
      this.fragments.geometry.getAttribute('position').needsUpdate = true;

      if (!this.opened && open > 0.2) {
        this.opened = true;
        setState({ systemLine: 'RECOVERED: CHOICE // MEMORY // FAILURE // FEELING' });
        ctx.audio.sub(30, 2.2);
        ctx.audio.duck(0.4, 0.6);
      }
    }

    // The interface degrades to debug near the reveal.
    if (p > 0.66 && !this.uiShifted) {
      this.uiShifted = true;
      document.documentElement.setAttribute('data-sovereign', 'debug');
      setState({ glyphs: ['0x7F..A2 DECRYPT OK', 'INTEGRITY 61% RISING', 'CLASSIFIER LABEL: "NOISE" — FALSE'] });
    }

    if (ctx.timeline.atGate) this.requestAdvance = true;
  }

  exit(): void {
    document.documentElement.setAttribute('data-sovereign', 'cold');
    setState({ glyphs: [] });
  }
}
