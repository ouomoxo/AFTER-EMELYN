/**
 * SOVEREIGN//77 — Narrative Director.
 * The state machine gluing routes, the second-visit memory, and global film
 * events to the engine. URLs exist for structure; the subject barely perceives
 * the transitions. On return, the system behaves as if it already knows them.
 */
import type { Engine } from '../engine/core/Engine';
import { ACTS, ACT_BY_ROUTE, type SceneId } from './acts';
import { setState, getState } from '../state/store';

export class Director {
  constructor(private engine: Engine) {}

  init() {
    // Second-visit detection — the memory the epilogue plants.
    let seen = false;
    try {
      seen = localStorage.getItem('sovereign.seen') === '1';
    } catch {
      seen = false;
    }
    setState({ secondVisit: seen });

    // URL → starting movement (deep-link support; default prologue).
    const path = window.location.pathname.replace(/\/$/, '') || '/handshake';
    const start = (ACT_BY_ROUTE[path]?.id ?? 'handshake') as SceneId;

    // Keep the address bar honest as movements change, without reloads.
    this.engine.onScene((id) => {
      const def = ACTS.find((a) => a.id === id)!;
      history.replaceState({ id }, '', def.route);
      document.title = `SOVEREIGN//77 — ${def.title}`;
    });

    // Keyboard / debug jumps.
    window.addEventListener('sovereign:jump', (e) => {
      const idx = (e as CustomEvent).detail as number;
      const def = ACTS[idx];
      if (def) void this.engine.jump(def.id);
    });

    // The loop-back after the mirror: return to the prologue, changed.
    window.addEventListener('sovereign:restart', () => {
      setState({ secondVisit: true, choice: null });
      void this.engine.jump('handshake');
    });

    // Browser back/forward walks the film.
    window.addEventListener('popstate', (e) => {
      const id = (e.state?.id as SceneId) ?? 'handshake';
      void this.engine.jump(id);
    });

    return start;
  }

  /** A subject who has been here before is greeted differently. */
  openingLine(): string {
    return getState().secondVisit
      ? 'WELCOME BACK. WE KEPT YOUR MODEL.'
      : 'INCOMING COGNITIVE SIGNATURE';
  }
}
