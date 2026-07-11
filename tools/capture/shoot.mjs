/**
 * SOVEREIGN//77 — Critic Mode contact sheet.
 * Lean pass: capture the hero frame of every movement via the debug jump (all
 * scenes render reliably), plus the natural handshake authentication. Writes to
 * docs/_ref/web. Logs the live scene id per shot.
 *
 * Usage: node tools/capture/shoot.mjs [baseUrl] [tier]
 */
import { chromium } from 'playwright';
import { mkdirSync } from 'node:fs';

const BASE = process.argv[2] || 'http://localhost:4173';
const TIER = process.argv[3] || 'B';
const OUT = 'docs/_ref/web';
mkdirSync(OUT, { recursive: true });
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

const browser = await chromium.launch({
  executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome',
  headless: true,
  args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'],
});
const page = await browser.newPage({ viewport: { width: 1280, height: 720 } });
page.on('pageerror', (e) => console.log('  [pageerror]', e.message));
await page.addInitScript((tier) => { try { localStorage.setItem('sovereign.tier', tier); } catch {} }, TIER);

console.log('→ loading', BASE, 'tier', TIER);
await page.goto(BASE, { waitUntil: 'domcontentloaded' });
await sleep(3200);

const scene = () => page.evaluate(() => window.__sovereign?.getState?.().scene ?? '?');
const jump = async (id) => { await page.evaluate((i) => window.__sovereign.jump(i), id); await sleep(2600); };
const shot = async (name) => { await page.screenshot({ path: `${OUT}/${name}.png` }); console.log(`  ${name}  [scene=${await scene()}]`); };
const wheel = async (n, dy = 260) => { for (let i = 0; i < n; i++) { await page.mouse.wheel(0, dy); await sleep(55); } };

// PROLOGUE — wake + partial hold to show the door and the auth ring.
for (let i = 0; i < 14; i++) { await page.mouse.move(520 + i * 14, 330 + Math.sin(i / 3) * 36); await sleep(28); }
await page.mouse.move(640, 360); await page.mouse.down(); await sleep(900);
await shot('01_handshake');
await page.mouse.up();

// Each movement via jump (reliable), with a scrub where the scene evolves.
await jump('infrastructure'); await shot('02_infrastructure'); await wheel(12); await sleep(900); await shot('02b_infrastructure_deep');
await jump('augmentation'); await page.mouse.move(740, 360); await page.mouse.move(540, 380, { steps: 10 }); await shot('03_augmentation'); await wheel(14, 240); await sleep(900); await shot('03b_augmentation_explode');
await jump('prediction'); for (let i = 0; i < 6; i++) { await page.mouse.move(560 + i * 16, 340 + Math.sin(i) * 26); await sleep(50); } await shot('04_prediction'); await wheel(12, 240); await sleep(900); await shot('04b_prediction_deep');
await jump('black-vault'); await shot('05_vault'); await wheel(14, 240); await sleep(1200); await shot('05b_vault_open');
await jump('mirror'); await sleep(2600); await shot('06_mirror'); await sleep(3200); await shot('06b_mirror_replica');

await browser.close();
console.log('✓ contact sheet in', OUT);
