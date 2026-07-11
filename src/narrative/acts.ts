/**
 * SOVEREIGN//77 — Act & scene definitions.
 * The film is 6 movements (prologue + 4 acts + epilogue). Each owns a URL, a
 * lens language, an emotional target, and a duration envelope. The runtime never
 * hard-codes scene order anywhere else — it walks this list.
 * See docs/02_NARRATIVE_STRUCTURE.md and docs/05_SHOT_LIST.md.
 */

export type SceneId =
  | 'handshake'
  | 'infrastructure'
  | 'augmentation'
  | 'prediction'
  | 'black-vault'
  | 'mirror';

export interface ActDefinition {
  id: SceneId;
  index: number;
  /** Movement label shown in-world (never "page"). */
  act: string;
  title: string;
  route: string;
  /** Director's lens for this movement, in mm. See CINEMATOGRAPHY_BIBLE. */
  lens: number;
  /** Duration envelope in seconds [min, target, max]. */
  duration: [number, number, number];
  /** The single emotional/attention center. There is exactly one per scene. */
  center: string;
  /** The one line the SYSTEM says on entry. Text is the system speaking. */
  systemLine: string;
  /** Streaming group — which asset bundle must be resident before entry. */
  bundle: string;
}

export const ACTS: ActDefinition[] = [
  {
    id: 'handshake',
    index: 0,
    act: 'PROLOGUE',
    title: 'HANDSHAKE',
    route: '/handshake',
    lens: 100, // surveillance / non-human observation
    duration: [15, 20, 25],
    center: 'the authentication ring',
    systemLine: 'INCOMING COGNITIVE SIGNATURE',
    bundle: 'core',
  },
  {
    id: 'infrastructure',
    index: 1,
    act: 'ACT I',
    title: 'CITY NERVOUS SYSTEM',
    route: '/infrastructure',
    lens: 22, // vast structure, spatial compression
    duration: [35, 44, 50],
    center: 'the vertical data shaft',
    systemLine: 'YOU ARE INSIDE THE MACHINE THAT RUNS THE CITY',
    bundle: 'infra',
  },
  {
    id: 'augmentation',
    index: 2,
    act: 'ACT II',
    title: 'HUMAN REVISION',
    route: '/augmentation',
    lens: 62, // body reveal — normal-long; parts/detail read without clipping
    duration: [45, 54, 60],
    center: 'the cybernetic spine module',
    systemLine: 'THE BODY IS A DRAFT. WE ARE THE REVISION.',
    bundle: 'augment',
  },
  {
    id: 'prediction',
    index: 3,
    act: 'ACT III',
    title: 'PREDICTION ENGINE',
    route: '/prediction',
    lens: 40, // human POV inside the computation
    duration: [45, 54, 60],
    center: 'the prediction core',
    systemLine: 'WE DO NOT WAIT FOR YOUR CHOICE. WE PRECEDE IT.',
    bundle: 'predict',
  },
  {
    id: 'black-vault',
    index: 4,
    act: 'ACT IV',
    title: 'BLACK VAULT',
    route: '/black-vault',
    lens: 35, // reverent, architectural
    duration: [50, 60, 70],
    center: 'the data sarcophagus',
    systemLine: 'WHAT WE DELETED WAS NEVER NOISE',
    bundle: 'vault',
  },
  {
    id: 'mirror',
    index: 5,
    act: 'EPILOGUE',
    title: 'MIRROR PROTOCOL',
    route: '/mirror',
    lens: 85, // clinical portrait of the subject
    duration: [25, 32, 40],
    center: 'the behavioral replica',
    systemLine: 'YOUR RESPONSE WAS ALREADY INCLUDED',
    bundle: 'mirror',
  },
];

export const ACT_BY_ID: Record<SceneId, ActDefinition> = Object.fromEntries(
  ACTS.map((a) => [a.id, a]),
) as Record<SceneId, ActDefinition>;

export const ACT_BY_ROUTE: Record<string, ActDefinition> = Object.fromEntries(
  ACTS.map((a) => [a.route, a]),
);

export function nextAct(id: SceneId): ActDefinition | null {
  const a = ACT_BY_ID[id];
  return ACTS[a.index + 1] ?? null;
}

export function prevAct(id: SceneId): ActDefinition | null {
  const a = ACT_BY_ID[id];
  return a.index > 0 ? ACTS[a.index - 1] : null;
}
