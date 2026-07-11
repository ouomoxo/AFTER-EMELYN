/**
 * SOVEREIGN//77 — Canonical palette & color grammar.
 * This is the single source of truth. Do not introduce colors outside this file.
 * See docs/04_ART_DIRECTION.md for the ratio budget and semantic rules.
 *
 * Ratio budget (screen-area target):
 *   Obsidian Black   55%   the void the system lives in
 *   Cold Graphite    20%   structure, machined surfaces
 *   Surgical White   12%   system authority / light
 *   Desaturated Cyan  7%   data flow (never decorative)
 *   Warning Amber     4%   caution, review, hesitation
 *   Emergency Red     2%   danger / privilege escalation ONLY
 */

export const PALETTE = {
  obsidian: 0x050506,
  obsidianDeep: 0x020203,
  graphite: 0x14161a,
  graphiteLight: 0x282c32,
  surgical: 0xe8ecec,
  surgicalDim: 0x9aa2a4,
  cyan: 0x4fd4d0,
  cyanDeep: 0x1c6b6a,
  amber: 0xe0a038,
  emergency: 0xe0322a,
} as const;

/** Hex strings for CSS / DOM UI. Mirrors PALETTE exactly. */
export const CSS = {
  obsidian: '#050506',
  obsidianDeep: '#020203',
  graphite: '#14161a',
  graphiteLight: '#282c32',
  surgical: '#e8ecec',
  surgicalDim: '#9aa2a4',
  cyan: '#4fd4d0',
  cyanDeep: '#1c6b6a',
  amber: '#e0a038',
  emergency: '#e0322a',
} as const;

/**
 * Semantic grammar. UI code should reference intent, not raw color, so the
 * "cyan = data / white = authority / amber = warning / red = privilege" rule
 * stays enforceable in one place.
 */
export const SEMANTIC = {
  data: CSS.cyan,
  authority: CSS.surgical,
  warning: CSS.amber,
  danger: CSS.emergency,
  dormant: CSS.surgicalDim,
} as const;

export type ColorKey = keyof typeof PALETTE;
