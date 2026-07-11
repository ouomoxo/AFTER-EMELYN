/**
 * ACT I — CITY NERVOUS SYSTEM.
 * The camera falls through the interior organs of the city: a vertical data
 * shaft, server spines, cooling towers, fiber. Scroll is the film playhead, not
 * a scrollbar. When the subject stops, drones/steam/light keep moving — the
 * world stays alive. Lens 22mm: vast structure, spatial compression.
 */
import * as THREE from 'three';
import { Scene, type SceneContext } from './Scene';
import type { SceneId } from '../../narrative/acts';
import { PALETTE } from '../../util/palette';
import { lerp, remap, smoothstep } from '../../util/math';
import { coldRig, DataStream, machinedModule } from './sceneKit';
import { setState } from '../../state/store';

export class InfrastructureScene extends Scene {
  id: SceneId = 'infrastructure';
  private shaft?: THREE.Mesh;
  private shaftCore?: THREE.Mesh;
  private stream!: DataStream;
  private drones: THREE.Object3D[] = [];
  private racks: THREE.Object3D[] = [];
  private lookedBack = false;

  async build(ctx: SceneContext): Promise<void> {
    this.three.fog = new THREE.FogExp2(0x04060a, 0.011);
    this.three.background = new THREE.Color(0x04060a);
    coldRig(this.three, [0, -14, 0], 42);

    // Central vertical data shaft — the spine of the city, kilometres deep.
    const shaftH = 220;
    this.shaft = new THREE.Mesh(
      new THREE.CylinderGeometry(2.4, 2.4, shaftH, 48, 1, true),
      new THREE.MeshStandardMaterial({
        color: PALETTE.graphite,
        metalness: 1,
        roughness: 0.45,
        side: THREE.BackSide,
      }),
    );
    this.shaft.position.y = -shaftH / 2 + 6;
    this.three.add(this.shaft);

    this.shaftCore = new THREE.Mesh(
      new THREE.CylinderGeometry(0.28, 0.28, shaftH, 24),
      new THREE.MeshStandardMaterial({
        color: PALETTE.cyan,
        emissive: PALETTE.cyan,
        emissiveIntensity: 1.05,
        roughness: 0.3,
      }),
    );
    this.shaftCore.position.y = this.shaft.position.y;
    this.three.add(this.shaftCore);

    // Ring structures descending the shaft (the "vertebrae" of the city).
    const ringMat = new THREE.MeshStandardMaterial({ color: PALETTE.graphiteLight, metalness: 1, roughness: 0.5 });
    for (let i = 0; i < 40; i++) {
      const ring = new THREE.Mesh(new THREE.TorusGeometry(2.6, 0.12, 8, 40), ringMat);
      ring.rotation.x = Math.PI / 2;
      ring.position.y = 4 - i * 5;
      this.three.add(ring);
    }

    // Server spines + cooling modules on the walls — try real assets, else procedural.
    await this.populateWalls(ctx);

    // Data particles streaming UP past the falling camera.
    this.stream = new DataStream(
      Math.floor(1400 * ctx.profile.particles + 120),
      new THREE.Vector3(6, 120, 6),
    );
    this.stream.points.position.y = -50;
    this.three.add(this.stream.points);

    // Maintenance drones drifting in the shaft.
    await this.spawnDrones(ctx);
  }

  private async populateWalls(ctx: SceneContext) {
    // Load the infrastructure kit; any missing piece degrades to a procedural box.
    const kit = await Promise.all(
      ['server_rack', 'cooling_unit', 'fiber_box'].map((n) =>
        ctx.loader.load(`assets/models/${n}.glb`).then((a) => a.scene).catch(() => null),
      ),
    );
    const [rack, cooler, fiber] = kit;
    const protos = [rack, cooler, rack, fiber]; // racks dominate the spine
    for (let i = 0; i < 34; i++) {
      const ang = (i / 34) * Math.PI * 2 * 3 + (i % 2) * 0.4; // spiral down
      const y = 3 - i * 3.4;
      const radius = 5.0 + (i % 3) * 0.7;
      const proto = protos[i % protos.length];
      const mod = proto ? proto.clone() : machinedModule(1.6, 3.0, 0.9);
      mod.position.set(Math.cos(ang) * radius, y, Math.sin(ang) * radius);
      mod.lookAt(0, y, 0);
      mod.scale.setScalar(proto === rack ? 1.3 : proto === cooler ? 1.1 : 1.4);
      this.three.add(mod);
      this.racks.push(mod);
    }
  }

  private async spawnDrones(ctx: SceneContext) {
    let proto: THREE.Object3D | null = null;
    try {
      const a = await ctx.loader.load('assets/models/maintenance_drone.glb');
      proto = a.scene;
    } catch {
      proto = null;
    }
    for (let i = 0; i < 6; i++) {
      const d = proto
        ? proto.clone()
        : new THREE.Mesh(
            new THREE.OctahedronGeometry(0.18),
            new THREE.MeshStandardMaterial({ color: PALETTE.graphiteLight, metalness: 1, roughness: 0.4 }),
          );
      d.position.set((Math.random() - 0.5) * 6, -i * 8 - 4, (Math.random() - 0.5) * 6);
      d.userData.baseY = d.position.y;
      d.userData.phase = Math.random() * Math.PI * 2;
      this.three.add(d);
      this.drones.push(d);
    }
  }

  enter(ctx: SceneContext): void {
    ctx.camera.hardSet([0, 4, 7], [0, 0, 0], 22);
    ctx.camera.posLambda = 1.4;
    ctx.camera.lookLambda = 1.8;
    ctx.camera.setParallaxLimit(0.5, 0.3);
    ctx.timeline.setShotBoundaries([0, 0.25, 0.6, 1.0]);
    setState({ interaction: 'observing' });
  }

  update(ctx: SceneContext, dt: number, time: number): void {
    const p = ctx.timeline.progress;

    // Scroll drives a descent down the shaft (the playhead IS the fall).
    const camY = remap(p, 0, 1, 4, -150, smoothstep);
    const camZ = remap(p, 0, 1, 7, 3.2);
    ctx.camera.setTarget([0, camY, camZ], [0, camY - 4, 0]);

    // Shot 4 (>0.6): infrastructure reveal — widen and slow.
    if (p > 0.6) ctx.camera.setLens(lerp(22, 28, smoothstep(remap(p, 0.6, 1, 0, 1))));

    // The world stays alive regardless of scroll.
    if (this.shaftCore) {
      const m = this.shaftCore.material as THREE.MeshStandardMaterial;
      m.emissiveIntensity = 0.95 + Math.sin(time * 3) * 0.25;
    }
    this.stream.update(dt, new THREE.Vector3(0, 1, 0), 6);
    for (const d of this.drones) {
      d.position.y = d.userData.baseY + Math.sin(time * 0.6 + d.userData.phase) * 0.6;
      d.rotation.y += dt * 0.4;
    }

    // Near the end the system notices the subject and turns to the camera.
    if (p > 0.9 && !this.lookedBack) {
      this.lookedBack = true;
      setState({ systemLine: 'YOU ARE BEING OBSERVED IN RETURN' });
      ctx.audio.blip(600);
    }

    if (ctx.timeline.atGate) this.requestAdvance = true;
  }
}
