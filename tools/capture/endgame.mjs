/** Capture the final two movements directly (avoids the sprite-heavy prediction run). */
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

await page.evaluate(() => window.__sovereign.jump('black-vault')); await sleep(2800);
await shot('V1_vault');
for (let i = 0; i < 16; i++) { await page.mouse.wheel(0, 240); await sleep(55); }
await sleep(1400); await shot('V2_vault_open');

await page.evaluate(() => window.__sovereign.jump('mirror')); await sleep(3000);
await shot('M1_mirror');
await sleep(4000); await shot('M2_replica');
// hover a choice
await page.mouse.move(560, 520); await sleep(400); await shot('M3_choices');

await browser.close();
console.log('✓ endgame frames captured');
