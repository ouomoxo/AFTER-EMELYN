/**
 * ACT II — HUMAN REVISION.
 * The cybernetic spine module. The subject may look, not seize control: drag
 * orbits the camera only within a director-set ±14°. Scrubbing separates the
 * five layers like a surgical exploded diagram. The data betrays the lie —
 * VOLUNTARY CONTROL 41% / PREDICTIVE OVERRIDE 59%. Lens 75mm: body & detail.
 */
import * as THREE from 'three';
import { Scene, type SceneContext } from './Scene';
import type { SceneId } from '../../narrative/acts';
import { PALETTE } from '../../util/palette';
import { clamp, damp, lerp, smoothstep, remap } from '../../util/math';
import { coldRig } from './sceneKit';
import { setState } from '../../state/store';

const LAYER_OFFSETS: Record<string, THREE.Vector3Tuple> = {
  Dermal_Shell_L: [0.85, 0, 0],
  Dermal_Shell_R: [-0.85, 0, 0],
  Muscle_Layer: [0, 0, -0.6],
  Neural_Conductor: [0, 0, 0.42],
  Memory_Coprocessor: [0, 0.55, 0.2],
  // Spinal_Interface stays — it is the truth at the core.
};

const LAYER_LABELS = [
  'DERMAL SHELL',
  'ARTIFICIAL MUSCLE LAYER',
  'NEURAL CONDUCTOR',
  'SPINAL INTERFACE',
  'MEMORY CO-PROCESSOR',
];

export class AugmentationScene extends Scene {
  id: SceneId = 'augmentation';
  private module?: THREE.Object3D;
  private parts: Record<string, THREE.Object3D> = {};
  private basePos: Record<string, THREE.Vector3> = {};
  private neuralMat?: THREE.MeshStandardMaterial;
  private signals: THREE.PointLight[] = [];
  private yaw = 0;
  private pitch = 0;
  private explode = 0;
  private center = new THREE.Vector3(0, 0.85, 0);
  private radius = 4.6; // far enough that the ~1.8m module fits at ~62mm
  private anomalyShown = false;

  async build(ctx: SceneContext): Promise<void> {
    this.three.fog = new THREE.FogExp2(0x05070a, 0.05);
    this.three.background = new THREE.Color(0x04050a);
    coldRig(this.three, [0, 0.9, 0], 34);

    // A cold operating-theatre floor reflection plane.
    const floor = new THREE.Mesh(
      new THREE.CircleGeometry(6, 48),
      new THREE.MeshStandardMaterial({ color: 0x070a0d, metalness: 0.9, roughness: 0.35 }),
    );
    floor.rotation.x = -Math.PI / 2;
    floor.position.y = -0.05;
    this.three.add(floor);

    try {
      const a = await ctx.loader.load('assets/models/cybernetic_module.glb');
      this.module = a.scene;
      this.module.position.set(0, 0, 0);
      this.three.add(this.module);
      for (const name of Object.keys(LAYER_OFFSETS).concat(['Spinal_Interface'])) {
        const o = a.parts[name];
        if (o) {
          this.parts[name] = o;
          this.basePos[name] = o.position.clone();
        }
      }
      // Grab the neural material so we can drive a living signal pulse.
      const neural = a.parts['Neural_Conductor'] as THREE.Mesh;
      if (neural?.isMesh) this.neuralMat = neural.material as THREE.MeshStandardMaterial;

      // Two cyan signals that travel up the spine — the nervous system alive.
      for (let i = 0; i < 2; i++) {
        const sig = new THREE.PointLight(0x4fd4d0, 2.2, 1.4, 2);
        this.three.add(sig);
        this.signals.push(sig);
      }

      // A cool rim light so the ceramic shell separates from the void.
      const rim = new THREE.SpotLight(0xbfe9ea, 26, 12, Math.PI / 5, 0.7, 1.2);
      rim.position.set(-2.5, 2.4, -3);
      rim.target.position.set(0, 0.9, 0);
      this.three.add(rim, rim.target);
    } catch {
      // Fallback: a stand-in stack so the scene still stands up.
      const stand = new THREE.Mesh(
        new THREE.CapsuleGeometry(0.2, 1.4, 6, 16),
        new THREE.MeshStandardMaterial({ color: PALETTE.surgical, metalness: 0.2, roughness: 0.3 }),
      );
      stand.position.y = 0.85;
      this.three.add(stand);
    }
  }

  enter(ctx: SceneContext): void {
    // Mobile cut: the module is a tall vertical spine — it OWNS a portrait frame,
    // so come closer (a more intimate, detail-forward read) than the wide cut.
    this.radius = ctx.portrait ? 4.0 : 4.6;
    const lens = ctx.portrait ? 52 : 62;
    ctx.camera.hardSet([0, 0.95, this.radius], [0, 0.85, 0], lens);
    ctx.camera.posLambda = 2.2;
    ctx.camera.lookLambda = 3.0;
    ctx.camera.setParallaxLimit(0.06, 0.05); // very restrained — this is a held shot
    setState({ interaction: 'engaged', systemLine: 'SUBJECT FRAME LOADED — REVISION PREVIEW' });
  }

  update(ctx: SceneContext, dt: number, time: number): void {
    const p = ctx.timeline.progress;

    // Constrained orbit: pointer sets a TARGET yaw/pitch within ±14° / ±7°.
    // A very slow drift toward the module (3-beat: hold → creep → hold) keeps the
    // held shot alive without turning it into a game camera.
    const targetYaw = ctx.pointer.x * 0.24;
    const targetPitch = ctx.pointer.y * 0.12;
    this.yaw = damp(this.yaw, targetYaw, 3, dt);
    this.pitch = damp(this.pitch, targetPitch, 3, dt);
    const creep = this.radius - smoothstep(clamp(ctx.timeline.localTime / 10)) * 0.5;
    const cx = Math.sin(this.yaw) * creep;
    const cz = Math.cos(this.yaw) * creep;
    const cy = 0.95 + this.pitch * 1.4;
    ctx.camera.setTarget([cx, cy, cz], [this.center.x, this.center.y, this.center.z]);

    // Neural signals travel up the spine; the conductor breathes with them.
    this.signals.forEach((sig, i) => {
      const t = (time * 0.5 + i * 0.5) % 1;
      sig.position.set(0, 0.2 + t * 1.4, 0.06);
      sig.intensity = Math.sin(t * Math.PI) * 3.0;
    });
    if (this.neuralMat) {
      this.neuralMat.emissiveIntensity = 1.0 + Math.sin(time * 3.5) * 0.5 + this.explode * 0.8;
    }

    // Scrub separates the layers in sequence (shell → muscle → neural → memory).
    this.explode = damp(this.explode, smoothstep(p), 2.4, dt);
    for (const [name, off] of Object.entries(LAYER_OFFSETS)) {
      const o = this.parts[name];
      const base = this.basePos[name];
      if (!o || !base) continue;
      // stagger: each layer starts a bit later
      const order = ['Dermal_Shell_L', 'Dermal_Shell_R', 'Muscle_Layer', 'Neural_Conductor', 'Memory_Coprocessor'].indexOf(name);
      const local = clamp(remap(this.explode, order * 0.1, order * 0.1 + 0.6, 0, 1));
      o.position.set(
        lerp(base.x, base.x + off[0], local),
        lerp(base.y, base.y + off[1], local),
        lerp(base.z, base.z + off[2], local),
      );
    }

    // The current layer label + the anomaly readout.
    const layerIdx = clamp(Math.floor(p * 5), 0, 4);
    setState({ systemLine: LAYER_LABELS[layerIdx] });

    if (p > 0.82 && !this.anomalyShown) {
      this.anomalyShown = true;
      setState({
        glyphs: ['VOLUNTARY CONTROL: 41%', 'PREDICTIVE OVERRIDE: 59%', 'CLASSIFICATION: CONTROL SUBSTRATE'],
        systemLine: 'THIS IS NOT ENHANCEMENT',
      });
      ctx.audio.sub(40, 1.4);
      ctx.audio.blip(420);
    }

    if (ctx.timeline.atGate) this.requestAdvance = true;
  }

  exit(): void {
    setState({ glyphs: [] });
  }
}
