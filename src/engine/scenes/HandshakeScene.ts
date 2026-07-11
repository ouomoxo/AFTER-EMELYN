/**
 * PROLOGUE — HANDSHAKE.
 * The black screen IS the door. The subject presses and holds the core for 2s;
 * authentication completes with a beat of silence, the leaves part, and the
 * camera is pulled through into fog — which masks the swap to Act I.
 * Lens 100mm: the system observes the subject from a cold distance.
 */
import * as THREE from 'three';
import { Scene, type SceneContext } from './Scene';
import type { SceneId } from '../../narrative/acts';
import { setState } from '../../state/store';
import { clamp, damp, smoothstep } from '../../util/math';
import { PALETTE } from '../../util/palette';

const HOLD_TIME = 2.0;

export class HandshakeScene extends Scene {
  id: SceneId = 'handshake';
  private door?: THREE.Object3D;
  private leafL?: THREE.Object3D;
  private leafR?: THREE.Object3D;
  private leafLBase = new THREE.Vector3();
  private leafRBase = new THREE.Vector3();
  private core?: THREE.Object3D;
  private coreMat?: THREE.MeshStandardMaterial;
  private key!: THREE.SpotLight;
  private rim!: THREE.PointLight;
  private dust?: THREE.Points;

  private holdStart = 0; // wall-clock ms when the press began
  private hold = 0; // 0..HOLD_TIME seconds, measured against wall clock
  private authed = false;
  private authTime = 0;
  private reveal = 0; // 0..1 how "awake" the door is
  private held = false;

  async build(ctx: SceneContext): Promise<void> {
    this.three.fog = new THREE.FogExp2(PALETTE.obsidianDeep, 0.12);
    this.three.background = new THREE.Color(PALETTE.obsidianDeep);

    try {
      const asset = await ctx.loader.load('assets/models/auth_door.glb');
      this.door = asset.scene;
      // Author face is +Y after glTF y-up; stand it up to face the camera (+Z).
      this.door.rotation.x = Math.PI / 2;
      this.door.scale.setScalar(1);
      this.door.position.set(0, 0, 0);
      this.three.add(this.door);

      this.leafL = asset.parts['Leaf_L'];
      this.leafR = asset.parts['Leaf_R'];
      if (this.leafL) this.leafLBase.copy(this.leafL.position);
      if (this.leafR) this.leafRBase.copy(this.leafR.position);
      this.core = asset.parts['Core'];
      const coreMesh = this.core as THREE.Mesh;
      if (coreMesh?.isMesh) this.coreMat = coreMesh.material as THREE.MeshStandardMaterial;
    } catch (e) {
      // The door must never be a blocker — fall back to a lit ring so the
      // prologue still resolves and the film continues.
      console.warn('[SOVEREIGN] auth_door load failed, using fallback', e);
      const ring = new THREE.Mesh(
        new THREE.TorusGeometry(1, 0.08, 16, 64),
        new THREE.MeshStandardMaterial({ color: PALETTE.cyan, emissive: PALETTE.cyan, emissiveIntensity: 2, metalness: 0.6, roughness: 0.3 }),
      );
      const core = new THREE.Mesh(
        new THREE.CircleGeometry(0.5, 48),
        new THREE.MeshStandardMaterial({ color: PALETTE.cyan, emissive: PALETTE.cyan, emissiveIntensity: 1.5 }),
      );
      this.core = core;
      this.coreMat = core.material as THREE.MeshStandardMaterial;
      this.door = new THREE.Group();
      this.door.add(ring, core);
      this.three.add(this.door);
    }

    // Lighting — near black at first, keyed on the core.
    this.key = new THREE.SpotLight(0xdfe8ea, 0.0, 22, Math.PI / 5, 0.6, 1.2);
    this.key.position.set(1.5, 2.5, 6);
    this.key.target.position.set(0, 0, 0);
    this.three.add(this.key, this.key.target);

    this.rim = new THREE.PointLight(PALETTE.cyan, 0.0, 12, 2);
    this.rim.position.set(0, 0, 2.2);
    this.three.add(this.rim);

    this.three.add(new THREE.AmbientLight(0x223035, 0.25));

    // Drifting dust so the void is never truly dead.
    const N = Math.floor(600 * ctx.profile.particles + 60);
    const g = new THREE.BufferGeometry();
    const pos = new Float32Array(N * 3);
    for (let i = 0; i < N; i++) {
      pos[i * 3] = (Math.random() - 0.5) * 10;
      pos[i * 3 + 1] = (Math.random() - 0.5) * 8;
      pos[i * 3 + 2] = Math.random() * 6 - 1;
    }
    g.setAttribute('position', new THREE.BufferAttribute(pos, 3));
    this.dust = new THREE.Points(
      g,
      new THREE.PointsMaterial({ color: 0x2a3438, size: 0.012, transparent: true, opacity: 0.5, depthWrite: false }),
    );
    this.three.add(this.dust);
  }

  enter(ctx: SceneContext): void {
    // Camera starts pushed toward the core, 100mm, very slow creep.
    ctx.camera.hardSet([0, 0.1, 5.2], [0, 0, 0], 100);
    ctx.camera.posLambda = 0.5;
    ctx.camera.setParallaxLimit(0.18, 0.1);
    setState({ interaction: 'observing', systemLine: 'INCOMING COGNITIVE SIGNATURE' });
  }

  onPress(ctx: SceneContext, down: boolean): void {
    this.held = down;
    if (down && !this.authed) {
      this.holdStart = performance.now();
      setState({ interaction: 'authenticating' });
      ctx.audio.blip(900);
    }
    if (!down) ctx.audio.endAuthTone();
  }

  onPointer(_ctx: SceneContext, _x: number, _y: number): void {
    if (!this.authed) {
      this.reveal = clamp(this.reveal + 0.02); // moving the cursor "wakes" the system
      if (this.reveal > 0.15) setState({ interaction: 'engaged' });
    }
  }

  update(ctx: SceneContext, dt: number, time: number): void {
    // Reveal the door as the subject engages.
    const targetReveal = this.authed ? 1 : Math.max(this.reveal, this.held ? 0.6 : 0.08);
    this.reveal = damp(this.reveal, targetReveal, 1.5, dt);
    this.key.intensity = damp(this.key.intensity, 40 * this.reveal + (this.authed ? 60 : 0), 2, dt);
    this.rim.intensity = damp(this.rim.intensity, 6 * this.reveal, 2, dt);

    // Core pulse — a heartbeat that quickens as it wakes.
    if (this.coreMat) {
      const beat = 0.5 + 0.5 * Math.sin(time * (1.5 + this.reveal * 4));
      this.coreMat.emissiveIntensity = 0.4 + beat * (0.6 + this.reveal * 2) + (this.authed ? 6 : 0);
    }

    // Press-and-hold authentication — measured against the WALL CLOCK so it is
    // always ~2 real seconds regardless of frame rate (dt is capped for physics
    // stability and would otherwise stretch the hold on slow devices).
    if (this.held && !this.authed) {
      this.hold = (performance.now() - this.holdStart) / 1000;
      const p = clamp(this.hold / HOLD_TIME);
      ctx.audio.authTone(p);
      ctx.timeline.drive(p); // fills the hold ring 0→100% over the 2s hold
      if (p >= 1) this.authenticate(ctx);
    } else if (!this.authed) {
      this.hold = damp(this.hold, 0, 3, dt);
      ctx.timeline.drive(clamp(this.hold / HOLD_TIME));
      ctx.audio.authTone(clamp(this.hold / HOLD_TIME));
    }

    // Post-authentication: silence beat, flare, part the leaves, dolly through.
    // Wall-clock timed so the reveal plays over real seconds at any frame rate.
    if (this.authed) {
      this.authTime = (performance.now() - this.authStart) / 1000;
      const t = this.authTime;
      const open = smoothstep(clamp((t - 0.35) / 1.5)); // leaves part after the silent beat
      // Part horizontally along the seam (local X survives the stand-up rotation).
      if (this.leafL) this.leafL.position.x = this.leafLBase.x - open * 2.4;
      if (this.leafR) this.leafR.position.x = this.leafRBase.x + open * 2.4;
      // Dolly the camera forward through the widening gap.
      const push = smoothstep(clamp((t - 0.6) / 2.2));
      ctx.camera.posLambda = 1.1;
      ctx.camera.setTarget([0, 0, 5.2 - push * 6.4], [0, 0, -4]);
      this.three.fog && ((this.three.fog as THREE.FogExp2).density = 0.12 + push * 0.5);
      if (t > 2.4) this.requestAdvance = true;
    }

    // Idle drift on the dust.
    if (this.dust) this.dust.rotation.y = time * 0.01;
  }

  private authStart = 0;
  private authenticate(ctx: SceneContext) {
    if (this.authed) return;
    this.authed = true;
    this.authStart = performance.now();
    this.authTime = 0;
    setState({ interaction: 'resolved' });
    ctx.audio.endAuthTone();
    ctx.audio.duck(0.05, 0.35); // the short silence
    setTimeout(() => ctx.audio.sub(28, 2.0), 300); // low-frequency shock as space opens
  }
}
