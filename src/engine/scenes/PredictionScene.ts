/**
 * ACT III — PREDICTION ENGINE.
 * A vast circular compute hall; a faceted core hangs at its center, gyroscopic
 * rings counter-rotating. Thousands of behavior simulations run around it. The
 * system pre-activates the target BEFORE the subject reaches it. Glitches are
 * logical EVENTS only (a restored record, a misclassification), never decor.
 * Lens 40mm: human POV inside the machine.
 */
import * as THREE from 'three';
import { Scene, type SceneContext } from './Scene';
import type { SceneId } from '../../narrative/acts';
import { PALETTE } from '../../util/palette';
import { clamp, damp, remap, smoothstep } from '../../util/math';
import { coldRig, DataStream } from './sceneKit';
import { makeGlowSprite } from '../materials/Environment';
import { setState } from '../../state/store';

export class PredictionScene extends Scene {
  id: SceneId = 'prediction';
  private core?: THREE.Object3D;
  private gyros: THREE.Object3D[] = [];
  private coreShellMat?: THREE.MeshStandardMaterial;
  private sims: THREE.Sprite[] = [];
  private stream!: DataStream;
  private predictSprite!: THREE.Sprite;
  private events = new Set<number>();

  async build(ctx: SceneContext): Promise<void> {
    this.three.fog = new THREE.FogExp2(0x03040a, 0.02);
    this.three.background = new THREE.Color(0x03040a);
    coldRig(this.three, [0, 1, 0], 40);

    // Circular hall floor + ceiling rings.
    const ringMat = new THREE.MeshStandardMaterial({ color: PALETTE.graphite, metalness: 1, roughness: 0.5 });
    for (let i = 0; i < 5; i++) {
      const ring = new THREE.Mesh(new THREE.TorusGeometry(9 + i * 2.5, 0.08, 8, 96), ringMat);
      ring.rotation.x = Math.PI / 2;
      ring.position.y = -2 + i * 0.02;
      this.three.add(ring);
    }

    try {
      const a = await ctx.loader.load('assets/models/prediction_core.glb');
      this.core = a.scene;
      this.core.position.set(0, 1.4, 0);
      this.core.scale.setScalar(1.4);
      this.three.add(this.core);
      ['Gyro_0', 'Gyro_1', 'Gyro_2'].forEach((n) => a.parts[n] && this.gyros.push(a.parts[n]));
      const shell = a.parts['CoreShell'] as THREE.Mesh;
      if (shell?.isMesh) this.coreShellMat = shell.material as THREE.MeshStandardMaterial;
    } catch {
      const core = new THREE.Mesh(
        new THREE.IcosahedronGeometry(1.2, 0),
        new THREE.MeshStandardMaterial({ color: PALETTE.cyan, emissive: PALETTE.cyan, emissiveIntensity: 1.5, roughness: 0.2, metalness: 0.4 }),
      );
      core.position.set(0, 1.4, 0);
      this.core = core;
      this.three.add(core);
    }

    // Thousands of behavior simulations — glowing sprites orbiting the core.
    const simTex = makeGlowSprite(32, '#4fd4d0');
    const N = Math.floor(620 * ctx.profile.particles + 90);
    for (let i = 0; i < N; i++) {
      const s = new THREE.Sprite(new THREE.SpriteMaterial({ map: simTex, color: PALETTE.cyan, transparent: true, opacity: 0.5, blending: THREE.AdditiveBlending, depthWrite: false }));
      const a = Math.random() * Math.PI * 2;
      const r = 3 + Math.random() * 7;
      const y = 1.4 + (Math.random() - 0.5) * 5;
      s.position.set(Math.cos(a) * r, y, Math.sin(a) * r);
      s.scale.setScalar(0.06 + Math.random() * 0.08);
      s.userData = { a, r, y, speed: 0.1 + Math.random() * 0.3 };
      this.three.add(s);
      this.sims.push(s);
    }

    // The system's predicted-cursor ghost (leads the real pointer).
    this.predictSprite = new THREE.Sprite(new THREE.SpriteMaterial({ map: makeGlowSprite(48, '#e8ecec'), color: PALETTE.surgical, transparent: true, opacity: 0.0, blending: THREE.AdditiveBlending, depthWrite: false }));
    this.predictSprite.scale.setScalar(0.5);
    this.three.add(this.predictSprite);

    this.stream = new DataStream(Math.floor(500 * ctx.profile.particles + 60), new THREE.Vector3(24, 10, 24));
    this.three.add(this.stream.points);
  }

  enter(ctx: SceneContext): void {
    ctx.camera.hardSet([0, 1.6, 12], [0, 1.4, 0], 40);
    ctx.camera.posLambda = 1.3;
    ctx.camera.setParallaxLimit(0.4, 0.22);
    setState({ interaction: 'engaged', systemLine: 'PREDICTION ENGINE ONLINE', glyphs: ['EXPECTED CURSOR VECTOR', 'PREDICTED DWELL TIME', 'NEXT ACTION PROBABILITY 0.00'] });
  }

  update(ctx: SceneContext, dt: number, time: number): void {
    const p = ctx.timeline.progress;

    // Push in toward the core across the movement. In the portrait cut the wide
    // hall needs more distance so the orrery fits the narrow frame.
    const z = ctx.portrait ? 1.35 : 1.0;
    const camZ = remap(p, 0, 1, 12 * z, 4.5 * z, smoothstep);
    ctx.camera.setTarget([ctx.pointer.x * 1.2, 1.5 + ctx.pointer.y * 0.6, camZ], [0, 1.4, 0]);

    // Gyroscopes counter-rotate; the core breathes.
    this.gyros.forEach((g, i) => {
      const s = (i + 1) * (i % 2 === 0 ? 1 : -1) * 0.3;
      g.rotation.y += dt * s;
      g.rotation.x += dt * s * 0.4;
    });
    if (this.core && !this.gyros.length) this.core.rotation.y += dt * 0.3;
    if (this.coreShellMat) this.coreShellMat.emissiveIntensity = 0.4 + Math.sin(time * 2) * 0.2;

    // Simulations orbit.
    for (const s of this.sims) {
      s.userData.a += dt * s.userData.speed;
      s.position.set(Math.cos(s.userData.a) * s.userData.r, s.userData.y + Math.sin(time + s.userData.r) * 0.1, Math.sin(s.userData.a) * s.userData.r);
    }
    this.stream.update(dt, new THREE.Vector3(0.3, 0, 0.2), 2);

    // Predicted-cursor ghost LEADS the real pointer (system precedes choice).
    const px = ctx.pointer.x * 3 + ctx.pointer.x * 0.8;
    const py = 1.5 + ctx.pointer.y * 1.4;
    this.predictSprite.position.set(px, py, 4.6);
    const m = this.predictSprite.material as THREE.SpriteMaterial;
    m.opacity = damp(m.opacity, clamp(p * 0.7), 2, dt);
    setState({ glyphs: ['EXPECTED CURSOR VECTOR', 'PREDICTED DWELL TIME', `NEXT ACTION PROBABILITY ${(clamp(0.4 + p * 0.58)).toFixed(2)}`] });

    // Logical glitch events (not random) at fixed narrative beats.
    this.fireEvent(ctx, p, 0.35, 0.35, 'HIDDEN RECORD RESTORED');
    this.fireEvent(ctx, p, 0.62, 0.5, 'SUBJECT MISCLASSIFIED — RECOMPUTING');
    this.fireEvent(ctx, p, 0.85, 0.7, 'TIMELINE CONFLICT DETECTED');

    // decay corruption
    if (this._corruptT > 0) {
      this._corruptT -= dt;
      ctx.fx.corruption(clamp(this._corruptT * this._corruptAmt));
    } else ctx.fx.corruption(0);

    if (ctx.timeline.atGate) this.requestAdvance = true;
  }

  private _corruptT = 0;
  private _corruptAmt = 0;
  private fireEvent(ctx: SceneContext, p: number, at: number, amt: number, line: string) {
    const key = Math.round(at * 100);
    if (p >= at && !this.events.has(key)) {
      this.events.add(key);
      this._corruptT = 0.5;
      this._corruptAmt = amt;
      setState({ systemLine: line });
      ctx.audio.sub(52, 0.5);
      ctx.audio.blip(300);
    }
  }

  exit(ctx: SceneContext): void {
    ctx.fx.corruption(0);
    setState({ glyphs: [] });
  }
}
