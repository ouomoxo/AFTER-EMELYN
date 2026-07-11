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
import { clamp, damp, smoothstep, lerp } from '../../util/math';
import { PALETTE } from '../../util/palette';
import { makePointsMaterial } from '../materials/Environment';

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
  private fill!: THREE.SpotLight;
  private rim!: THREE.PointLight;
  private dust?: THREE.Points;
  private estZ = 13.5; // establishing dolly distance (set per aspect in enter)
  private estLens = 40;

  private holdStart = 0; // wall-clock ms when the press began
  private hold = 0; // 0..HOLD_TIME seconds, measured against wall clock
  private authed = false;
  private authTime = 0;
  private reveal = 0; // 0..1 how "awake" the door is
  private engage = 0; // 0..1 ratcheting push toward the core (never pulls back)
  private held = false;
  private freezeOpen = false; // debug: hold the door open for capture (?freezeopen)

  async build(ctx: SceneContext): Promise<void> {
    // Read the debug flag before the router rewrites the URL to /handshake.
    if (typeof location !== 'undefined' && new URLSearchParams(location.search).has('freezeopen')) {
      this.freezeOpen = true;
    }
    // Light fog at rest so the monumental door reads crisp; it thickens on auth
    // to swallow the camera as it is pulled through into the tunnel.
    this.three.fog = new THREE.FogExp2(PALETTE.obsidianDeep, 0.05);
    this.three.background = new THREE.Color(PALETTE.obsidianDeep);

    try {
      // The pressure door carries its detail in real geometry (bolts, armor
      // bands, the machined eye), so it reads on every tier from the lean
      // neutral-PBR GLB — no AO-baked variant. (The door's AO bake blew its base
      // color to white under glTF; the geometry needs no help, so skip it.)
      const asset = await ctx.loader.load('assets/models/auth_door.glb');
      this.door = asset.scene;
      // Author face is +Y after glTF y-up; stand it up to face the camera (+Z).
      this.door.rotation.x = Math.PI / 2;
      this.door.scale.setScalar(1);
      this.door.position.set(0, 0, 0);
      this.three.add(this.door);

      // The prologue must read near-black at rest, then reveal under the ramping
      // key. The procedural studio environment blows the ceramic/polished metal
      // to white via IBL, so dim it right down — the scene lights + the emissive
      // eye do the sculpting, not the ambient env.
      this.door.traverse((o) => {
        const mesh = o as THREE.Mesh;
        if (!mesh.isMesh) return;
        const mats = Array.isArray(mesh.material) ? mesh.material : [mesh.material];
        for (const mm of mats as THREE.MeshStandardMaterial[]) {
          if (mm && 'envMapIntensity' in mm) mm.envMapIntensity = 0.16;
        }
      });

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

    // Lighting — near black at first, then a cold key rakes the whole bulkhead
    // as the subject wakes it. Wide cone + long range to cover the 10m wall.
    this.key = new THREE.SpotLight(0xdfe8ea, 0.0, 70, Math.PI / 3.1, 0.5, 1.0);
    this.key.position.set(3.5, 6, 11);
    this.key.target.position.set(0, 0, 0);
    this.three.add(this.key, this.key.target);

    // A cold fill from the opposite low side so the wall + floor never crush.
    this.fill = new THREE.SpotLight(0x27363d, 0.0, 70, Math.PI / 2.9, 0.6, 1.0);
    this.fill.position.set(-5.5, -1.5, 10);
    this.fill.target.position.set(0, -0.5, 0);
    this.three.add(this.fill, this.fill.target);

    // Cyan rim — the eye's own glow spills onto the seam.
    this.rim = new THREE.PointLight(PALETTE.cyan, 0.0, 9, 2);
    this.rim.position.set(0, 0, 1.4);
    this.three.add(this.rim);

    this.three.add(new THREE.AmbientLight(0x1a2429, 0.4));

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
    this.dust = new THREE.Points(g, makePointsMaterial(0x2a3438, 0.02, 0.5));
    this.three.add(this.dust);
  }

  enter(ctx: SceneContext): void {
    // Establishing: the monumental blast door in a dark hall, the grated floor
    // leading in. Wide + low so its scale reads; it starts near-black and the
    // key comes up as the subject engages. Portrait pulls back to fit the frame.
    this.estZ = ctx.portrait ? 15.5 : 13.5;
    this.estLens = ctx.portrait ? 34 : 42;
    ctx.camera.hardSet([0, -0.3, this.estZ], [0, -0.1, 0], this.estLens);
    ctx.camera.posLambda = 0.4;
    ctx.camera.lookLambda = 1.2;
    ctx.camera.setParallaxLimit(0.14, 0.08);
    setState({ interaction: 'observing', systemLine: 'INCOMING COGNITIVE SIGNATURE' });
    // Debug aid: ?freezeopen (captured in build) authenticates immediately and
    // holds the door open (never advances) so the leaf-parting can be captured.
    if (this.freezeOpen) this.authenticate(ctx);
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
    this.key.intensity = damp(this.key.intensity, 150 * this.reveal + (this.authed ? 80 : 0), 2, dt);
    this.fill.intensity = damp(this.fill.intensity, 45 * this.reveal, 2, dt);
    this.rim.intensity = damp(this.rim.intensity, 10 * this.reveal, 2, dt);

    // Before auth: a deliberate push from the establishing wide toward the core.
    // `engage` ratchets forward (holding = full push) so releasing never yanks
    // the camera back out.
    if (!this.authed) {
      const engTarget = this.held ? 1 : this.reveal > 0.12 ? 0.5 : 0;
      this.engage = Math.max(this.engage, engTarget);
      const push = smoothstep(this.engage);
      ctx.camera.posLambda = 0.6;
      ctx.camera.setTarget([0, lerp(-0.3, 0, push), lerp(this.estZ, 6.5, push)], [0, 0, 0.4]);
      ctx.camera.setLens(lerp(this.estLens, 58, push));
    }

    // Core pulse — a heartbeat that quickens as it wakes.
    if (this.coreMat) {
      const beat = 0.5 + 0.5 * Math.sin(time * (1.5 + this.reveal * 4));
      this.coreMat.emissiveIntensity = 0.4 + beat * (0.6 + this.reveal * 2) + (this.authed ? 3 : 0);
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
      const open = smoothstep(clamp((t - 0.35) / 1.6)); // leaves part after the silent beat
      // Part horizontally along the seam (local X survives the stand-up rotation).
      // Wide enough to fully clear the ~2m leaves and expose the tunnel mouth.
      if (this.leafL) this.leafL.position.x = this.leafLBase.x - open * 2.7;
      if (this.leafR) this.leafR.position.x = this.leafRBase.x + open * 2.7;
      // Dolly from the core through the widening gap, past the parting leaves,
      // into the lit tunnel. In freeze mode the dolly is held for capture.
      const camT = this.freezeOpen ? Math.min(t, 0.8) : t;
      const push = smoothstep(clamp((camT - 0.5) / 2.2));
      ctx.camera.posLambda = 1.0;
      ctx.camera.setTarget([0, 0, lerp(6.5, -5.0, push)], [0, 0, -9]);
      this.three.fog && ((this.three.fog as THREE.FogExp2).density = 0.05 + push * 0.28);
      if (t > 2.6 && !this.freezeOpen) this.requestAdvance = true;
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
