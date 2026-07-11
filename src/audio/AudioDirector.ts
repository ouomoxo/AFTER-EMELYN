/**
 * SOVEREIGN//77 — AudioDirector.
 * Every sound is synthesized in the Web Audio graph — no audio files. Six
 * layers per the sound design: room tone, machine physics, data feedback,
 * musical drone, interface, and deliberate silence. Sub-bass is fired
 * 100–300ms BEFORE a visual hit to telegraph it. The closer to the system's
 * core, the more machine overtakes music; the final twist strips music and
 * leaves only the subject's own input sounds.
 */
import type { SceneId } from '../narrative/acts';

export class AudioDirector {
  private ctx?: AudioContext;
  private master?: GainNode;
  private roomGain?: GainNode;
  private machineGain?: GainNode;
  private musicGain?: GainNode;
  private started = false;
  muted = false;

  private roomNodes: AudioNode[] = [];
  private machineNodes: AudioNode[] = [];
  private musicNodes: AudioNode[] = [];

  /** Must be called from a user gesture (autoplay policy). */
  init() {
    if (this.started) return;
    const Ctx = window.AudioContext || (window as unknown as { webkitAudioContext: typeof AudioContext }).webkitAudioContext;
    this.ctx = new Ctx();
    this.master = this.ctx.createGain();
    this.master.gain.value = this.muted ? 0 : 0.9;
    this.master.connect(this.ctx.destination);

    this.roomGain = this.ctx.createGain();
    this.machineGain = this.ctx.createGain();
    this.musicGain = this.ctx.createGain();
    [this.roomGain, this.machineGain, this.musicGain].forEach((g) => {
      g.gain.value = 0;
      g.connect(this.master!);
    });

    this.buildRoomTone();
    this.buildMusicDrone();
    this.started = true;
  }

  get ready() {
    return this.started;
  }

  private t() {
    return this.ctx!.currentTime;
  }

  private noiseBuffer(): AudioBuffer {
    const ctx = this.ctx!;
    const len = ctx.sampleRate * 2;
    const buf = ctx.createBuffer(1, len, ctx.sampleRate);
    const d = buf.getChannelData(0);
    for (let i = 0; i < len; i++) d[i] = Math.random() * 2 - 1;
    return buf;
  }

  // Layer 1 — low-frequency room tone (the space breathing).
  private buildRoomTone() {
    const ctx = this.ctx!;
    const oscA = ctx.createOscillator();
    oscA.type = 'sine';
    oscA.frequency.value = 41;
    const oscB = ctx.createOscillator();
    oscB.type = 'sine';
    oscB.frequency.value = 41.6; // slow beat
    const noise = ctx.createBufferSource();
    noise.buffer = this.noiseBuffer();
    noise.loop = true;
    const lp = ctx.createBiquadFilter();
    lp.type = 'lowpass';
    lp.frequency.value = 220;
    const nGain = ctx.createGain();
    nGain.gain.value = 0.06;
    oscA.connect(this.roomGain!);
    oscB.connect(this.roomGain!);
    noise.connect(lp).connect(nGain).connect(this.roomGain!);
    oscA.start();
    oscB.start();
    noise.start();
    this.roomNodes.push(oscA, oscB, noise);
  }

  // Layer 4 — musical drone (a cold minor cluster).
  private buildMusicDrone() {
    const ctx = this.ctx!;
    const freqs = [55, 82.4, 110, 164.8]; // A1, E2, A2, E3
    freqs.forEach((f, i) => {
      const o = ctx.createOscillator();
      o.type = i === 0 ? 'triangle' : 'sine';
      o.frequency.value = f;
      const g = ctx.createGain();
      g.gain.value = 0.12 / (i + 1);
      const lfo = ctx.createOscillator();
      lfo.frequency.value = 0.05 + i * 0.017;
      const lfoG = ctx.createGain();
      lfoG.gain.value = 0.04;
      lfo.connect(lfoG).connect(g.gain);
      o.connect(g).connect(this.musicGain!);
      o.start();
      lfo.start();
      this.musicNodes.push(o, lfo);
    });
  }

  // Layer 2 — machine hum (per-scene mechanical bed).
  private buildMachine(freq: number, detune: number) {
    this.machineNodes.forEach((n) => (n as OscillatorNode).stop?.());
    this.machineNodes = [];
    const ctx = this.ctx!;
    for (let i = 0; i < 3; i++) {
      const o = ctx.createOscillator();
      o.type = 'sawtooth';
      o.frequency.value = freq * (1 + i * 0.5);
      o.detune.value = (i - 1) * detune;
      const bp = ctx.createBiquadFilter();
      bp.type = 'bandpass';
      bp.frequency.value = 320 + i * 260;
      bp.Q.value = 6;
      const g = ctx.createGain();
      g.gain.value = 0.03 / (i + 1);
      o.connect(bp).connect(g).connect(this.machineGain!);
      o.start();
      this.machineNodes.push(o);
    }
  }

  private ramp(g: GainNode | undefined, to: number, time = 1.2) {
    if (!g) return;
    g.gain.cancelScheduledValues(this.t());
    g.gain.setTargetAtTime(to, this.t(), time / 3);
  }

  /** Balance the six layers for a given movement. */
  setScene(id: SceneId) {
    if (!this.started) return;
    const beds: Record<SceneId, [number, number, number, number]> = {
      // [room, machine, music, machineFreq]
      handshake: [0.5, 0.2, 0.5, 60],
      infrastructure: [0.7, 0.6, 0.45, 48],
      augmentation: [0.6, 0.7, 0.4, 72],
      prediction: [0.55, 0.9, 0.3, 90],
      'black-vault': [0.8, 0.35, 0.5, 40],
      mirror: [0.4, 0.15, 0.0, 55], // final twist: music gone
    };
    const [room, machine, music, freq] = beds[id];
    this.buildMachine(freq, 12);
    this.ramp(this.roomGain, room, 2.0);
    this.ramp(this.machineGain, machine, 2.4);
    this.ramp(this.musicGain, music, 3.0);
  }

  /** Duck everything briefly before a big transition. */
  duck(depth = 0.25, time = 0.4) {
    if (!this.master) return;
    this.master.gain.setTargetAtTime(this.muted ? 0 : depth, this.t(), time / 3);
    this.master.gain.setTargetAtTime(this.muted ? 0 : 0.9, this.t() + time + 0.5, 0.4);
  }

  /** Sub-bass telegraph — fire ~200ms before a visual hit. */
  sub(freq = 34, dur = 1.4) {
    if (!this.ctx) return;
    const o = this.ctx.createOscillator();
    o.type = 'sine';
    o.frequency.setValueAtTime(freq * 1.6, this.t());
    o.frequency.exponentialRampToValueAtTime(freq, this.t() + 0.5);
    const g = this.ctx.createGain();
    g.gain.setValueAtTime(0.0001, this.t());
    g.gain.exponentialRampToValueAtTime(this.muted ? 0.0001 : 0.7, this.t() + 0.04);
    g.gain.exponentialRampToValueAtTime(0.0001, this.t() + dur);
    o.connect(g).connect(this.master!);
    o.start();
    o.stop(this.t() + dur + 0.1);
  }

  /** Interface tick — used sparingly (not every button beeps). */
  click(freq = 880) {
    if (!this.ctx) return;
    const o = this.ctx.createOscillator();
    o.type = 'square';
    o.frequency.value = freq;
    const g = this.ctx.createGain();
    g.gain.setValueAtTime(0.0001, this.t());
    g.gain.exponentialRampToValueAtTime(this.muted ? 0.0001 : 0.16, this.t() + 0.005);
    g.gain.exponentialRampToValueAtTime(0.0001, this.t() + 0.09);
    o.connect(g).connect(this.master!);
    o.start();
    o.stop(this.t() + 0.12);
  }

  /** Data feedback blip (system acknowledging the subject). */
  blip(freq = 1400) {
    if (!this.ctx) return;
    const o = this.ctx.createOscillator();
    o.type = 'sine';
    o.frequency.setValueAtTime(freq, this.t());
    o.frequency.exponentialRampToValueAtTime(freq * 1.5, this.t() + 0.08);
    const g = this.ctx.createGain();
    g.gain.setValueAtTime(0.0001, this.t());
    g.gain.exponentialRampToValueAtTime(this.muted ? 0.0001 : 0.08, this.t() + 0.01);
    g.gain.exponentialRampToValueAtTime(0.0001, this.t() + 0.12);
    o.connect(g).connect(this.master!);
    o.start();
    o.stop(this.t() + 0.14);
  }

  /** Rising authentication tone during press-and-hold. `p` is 0..1. */
  authTone(p: number) {
    // Reuse a persistent oscillator via a simple pooled node.
    if (!this.ctx) return;
    if (!this._auth) {
      this._auth = this.ctx.createOscillator();
      this._authGain = this.ctx.createGain();
      this._authGain.gain.value = 0;
      this._auth.type = 'sine';
      this._auth.connect(this._authGain).connect(this.master!);
      this._auth.start();
    }
    this._auth.frequency.setTargetAtTime(180 + p * 620, this.t(), 0.05);
    this._authGain!.gain.setTargetAtTime(this.muted ? 0 : p * 0.12, this.t(), 0.05);
  }
  private _auth?: OscillatorNode;
  private _authGain?: GainNode;

  endAuthTone() {
    this._authGain?.gain.setTargetAtTime(0, this.t(), 0.1);
  }

  setMuted(m: boolean) {
    this.muted = m;
    if (this.master) this.master.gain.setTargetAtTime(m ? 0 : 0.9, this.t(), 0.1);
  }
}
