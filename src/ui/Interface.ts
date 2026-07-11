/**
 * SOVEREIGN//77 — DOM Interface.
 * Subscribes to the store and renders the system's voice: act label, spoken
 * line, data glyphs, the lagging tracking cursor, the handshake hold ring, the
 * mirror choices, and minimal controls. Everything here is in-world.
 */
import './interface.css';
import { store, getState, type SovereignState } from '../state/store';
import { ACT_BY_ID } from '../narrative/acts';
import type { AudioDirector } from '../audio/AudioDirector';

export class Interface {
  private root: HTMLElement;
  private el: Record<string, HTMLElement> = {};
  private holdCirc = 326.7256; // 2πr for r=52
  private lastLine = '';

  constructor(mount: HTMLElement, private audio: AudioDirector) {
    this.root = mount;
    this.build();
    store.subscribe((s) => this.render(s));
  }

  private h(tag: string, cls?: string, html?: string): HTMLElement {
    const e = document.createElement(tag);
    if (cls) e.className = cls;
    if (html !== undefined) e.innerHTML = html;
    return e;
  }

  private build() {
    this.root.classList.add('live');
    this.root.appendChild(this.h('div', 'frame'));
    ['tl', 'tr', 'bl', 'br'].forEach((c) => this.root.appendChild(this.h('div', `tick ${c}`)));

    this.el.track = this.h('div', 'cursor-track');
    this.el.track.setAttribute('data-tag', 'TRACKING');
    this.el.dot = this.h('div', 'cursor-dot');
    this.root.append(this.el.track, this.el.dot);

    this.el.act = this.h('div', 'act-label');
    this.el.line = this.h('div', 'system-line');
    this.el.glyphs = this.h('div', 'glyphs');
    this.el.progress = this.h('div', 'progress');
    for (let i = 0; i < 6; i++) this.el.progress.appendChild(this.h('i'));
    this.root.append(this.el.act, this.el.line, this.el.glyphs, this.el.progress);

    // Hold ring (handshake)
    this.el.hold = this.h('div', 'hold-ring');
    this.el.hold.innerHTML = `
      <svg width="120" height="120" viewBox="0 0 120 120">
        <circle class="bg" cx="60" cy="60" r="52" fill="none" stroke-width="2"/>
        <circle class="fg" cx="60" cy="60" r="52" fill="none" stroke-width="2"
          stroke-dasharray="${this.holdCirc}" stroke-dashoffset="${this.holdCirc}"/>
      </svg>
      <div class="label">HOLD TO AUTHENTICATE</div>`;
    this.root.appendChild(this.el.hold);
    this.el.holdFg = this.el.hold.querySelector('.fg') as HTMLElement;
    this.el.holdLabel = this.el.hold.querySelector('.label') as HTMLElement;

    // Mirror choices
    this.el.choices = this.h('div', 'choices');
    const accept = this.h('button', 'choice accept', 'ACCEPT CONTINUITY');
    const terminate = this.h('button', 'choice terminate', 'TERMINATE MODEL');
    accept.addEventListener('click', () => this.choose('accept'));
    terminate.addEventListener('click', () => this.choose('terminate'));
    this.el.choices.append(accept, terminate);
    this.root.appendChild(this.el.choices);

    // Controls
    const controls = this.h('div', 'controls');
    this.el.mute = this.h('button', undefined, 'SOUND: ON');
    this.el.mute.addEventListener('click', () => {
      const m = !getState().muted;
      store.setState({ muted: m });
      this.audio.setMuted(m);
      this.el.mute.textContent = `SOUND: ${m ? 'OFF' : 'ON'}`;
    });
    this.el.renderClass = this.h('div', 'render-class', 'RENDER CLASS: —');
    controls.append(this.el.renderClass, this.el.mute);
    this.root.appendChild(controls);
  }

  private choose(which: 'accept' | 'terminate') {
    this.audio.click(which === 'accept' ? 660 : 300);
    window.dispatchEvent(new CustomEvent('sovereign:choice', { detail: which }));
    this.el.choices.classList.remove('show');
  }

  private render(s: SovereignState) {
    const def = ACT_BY_ID[s.scene];
    this.el.act.innerHTML = `${def.act} &nbsp;·&nbsp; <b>${def.title}</b>`;
    this.el.renderClass.textContent = `RENDER CLASS: ${s.tier}`;

    // System line — retypes when it changes.
    if (s.systemLine !== this.lastLine) {
      this.lastLine = s.systemLine;
      this.el.line.innerHTML = `${s.systemLine}<span class="cursorpipe">▌</span>`;
      this.el.line.classList.add('show');
    }
    if (!s.systemLine) this.el.line.classList.remove('show');

    // Glyphs
    this.el.glyphs.innerHTML = s.glyphs
      .map((g) => `<div class="${/OVERRIDE|WARNING|CONFLICT|FALSE/.test(g) ? 'warn' : ''}">${g}</div>`)
      .join('');

    // Progress ticks
    const ticks = this.el.progress.children;
    const onCount = Math.round(s.progress * 6);
    for (let i = 0; i < ticks.length; i++) ticks[i].classList.toggle('on', i < onCount);

    // Hold ring — visible during handshake engagement/authentication.
    const showHold = s.scene === 'handshake' && (s.interaction === 'engaged' || s.interaction === 'authenticating');
    this.el.hold.classList.toggle('show', showHold);
    if (showHold) {
      const off = this.holdCirc * (1 - (s.interaction === 'authenticating' ? s.progress : 0));
      (this.el.holdFg as unknown as SVGElement).setAttribute('stroke-dashoffset', String(off));
      this.el.holdLabel.textContent = s.interaction === 'authenticating' ? 'AUTHENTICATING' : 'HOLD TO AUTHENTICATE';
    }

    // Mirror choices — appear once the replica is complete (interaction latched).
    const showChoices = s.scene === 'mirror' && s.interaction === 'authenticating' && !s.choice;
    this.el.choices.classList.toggle('show', showChoices);
    if (showChoices) this.el.track.setAttribute('data-tag', 'DECIDING');
  }
}
