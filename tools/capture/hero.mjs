/** Hero-scene capture: handshake authentication + door open, augmentation explode, infra depth. */
import { chromium } from 'playwright';
import { mkdirSync } from 'node:fs';
const BASE = process.argv[2] || 'http://localhost:4173';
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
await page.addInitScript(() => { try { localStorage.setItem('sovereign.tier', 'B'); } catch {} });
await page.goto(BASE, { waitUntil: 'domcontentloaded' });
await sleep(3200);
const scene = () => page.evaluate(() => window.__sovereign?.getState?.().scene ?? '?');
const shot = async (n) => { await page.screenshot({ path: `${OUT}/${n}.png` }); console.log(`  ${n} [${await scene()}]`); };

// HANDSHAKE — wake, hold to authenticate, catch the door opening + dolly-through.
for (let i = 0; i < 14; i++) { await page.mouse.move(520 + i * 14, 330 + Math.sin(i / 3) * 36); await sleep(28); }
await page.mouse.move(640, 360); await page.mouse.down(); await sleep(2100);
await shot('H1_auth_complete');
await sleep(700); await shot('H2_door_opening');
await sleep(900); await shot('H3_door_through');
await page.mouse.up();
await sleep(3200); await shot('H4_after_transition'); // should be infrastructure

// INFRASTRUCTURE depth (travel light on the machinery).
await page.evaluate(() => window.__sovereign.jump('infrastructure')); await sleep(2600);
for (let i = 0; i < 12; i++) { await page.mouse.wheel(0, 260); await sleep(55); }
await sleep(900); await shot('I1_infra_deep');

// AUGMENTATION — assembled, then explode with neural pulse.
await page.evaluate(() => window.__sovereign.jump('augmentation')); await sleep(2800);
await shot('A1_assembled');
for (let i = 0; i < 16; i++) { await page.mouse.wheel(0, 240); await sleep(55); }
await sleep(1000); await shot('A2_explode');

await browser.close();
console.log('✓ hero frames captured');
