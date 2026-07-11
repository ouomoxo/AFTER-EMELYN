/**
 * SOVEREIGN//77 — Bootstrap.
 * Wires the engine, the six movements, input, audio, the diegetic interface,
 * and the narrative director. In-world, this is the cold-start of an access
 * terminal: the boot glyph dissolves the instant the system takes over.
 */
import { Engine } from './engine/core/Engine';
import { Director } from './narrative/Director';
import { Interface } from './ui/Interface';
import { InputInterpreter } from './input/InputInterpreter';
import { HandshakeScene } from './engine/scenes/HandshakeScene';
import { InfrastructureScene } from './engine/scenes/InfrastructureScene';
import { AugmentationScene } from './engine/scenes/AugmentationScene';
import { PredictionScene } from './engine/scenes/PredictionScene';
import { BlackVaultScene } from './engine/scenes/BlackVaultScene';
import { MirrorScene } from './engine/scenes/MirrorScene';
import { renderAudioProof } from './audio/AudioDirector';
import { setState, getState } from './state/store';

async function boot() {
  const stage = document.getElementById('stage')!;
  const uiMount = document.getElementById('interface')!;

  const engine = new Engine(stage);
  engine.register('handshake', () => new HandshakeScene());
  engine.register('infrastructure', () => new InfrastructureScene());
  engine.register('augmentation', () => new AugmentationScene());
  engine.register('prediction', () => new PredictionScene());
  engine.register('black-vault', () => new BlackVaultScene());
  engine.register('mirror', () => new MirrorScene());

  const ui = new Interface(uiMount, engine.audio);
  void ui;
  const input = new InputInterpreter(engine, document.body);
  input.attach();

  const director = new Director(engine);
  const start = director.init();

  // Audio must start from a user gesture (autoplay policy).
  const armAudio = () => {
    if (!engine.audio.ready) {
      engine.audio.init();
      engine.audio.setScene(getState().scene);
      setState({ audioReady: true });
    }
  };
  window.addEventListener('pointerdown', armAudio, { once: true });
  window.addEventListener('keydown', armAudio, { once: true });

  // Body "pressing" class drives the custom cursor state.
  window.addEventListener('pointerdown', () => document.body.classList.add('pressing'));
  window.addEventListener('pointerup', () => document.body.classList.remove('pressing'));

  if (new URLSearchParams(location.search).has('debug')) setState({ debug: true });

  // Introspection hook for the capture harness / debugging (not user-facing).
  (window as unknown as { __sovereign: unknown }).__sovereign = {
    getState,
    jump: (id: string) => engine.jump(id as never),
    audioProof: renderAudioProof,
    engine,
  };

  await engine.start(start);

  // Dissolve the boot glyph — the system is now in control.
  const bootEl = document.getElementById('boot');
  if (bootEl) {
    bootEl.style.opacity = '0';
    setTimeout(() => bootEl.remove(), 1000);
  }
  setState({ booted: true });

  // Returning subjects are addressed as known.
  if (getState().secondVisit) {
    setState({ systemLine: 'WELCOME BACK. WE KEPT YOUR MODEL.' });
  }
}

boot().catch((err) => {
  console.error('[SOVEREIGN] boot failed', err);
  const boot = document.getElementById('boot');
  if (boot) boot.innerHTML = '<span class="sig" style="color:#e0322a">ACCESS FAULT — REFRESH TERMINAL</span>';
});
