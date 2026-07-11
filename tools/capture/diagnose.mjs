/** Focused diagnostic — logs state transitions + per-scene render health to stdout (redirect to a file). */
import { chromium } from 'playwright';
const BASE = process.argv[2] || 'http://localhost:4173';
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const browser = await chromium.launch({
  executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome',
  headless: true,
  args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'],
});
const page = await browser.newPage({ viewport: { width: 1280, height: 720 } });
page.on('console', (m) => console.log('[console]', m.text()));
page.on('pageerror', (e) => console.log('[pageerror]', e.message, e.stack?.split('\n')[1] || ''));
await page.addInitScript(() => { try { localStorage.setItem('sovereign.tier', 'B'); } catch {} });
await page.goto(BASE, { waitUntil: 'domcontentloaded' });
await sleep(3500);

const state = () => page.evaluate(() => {
  const s = window.__sovereign?.getState?.();
  return s ? { scene: s.scene, inter: s.interaction, prog: +s.progress.toFixed(2), trans: s.transition } : null;
});

console.log('boot state:', JSON.stringify(await state()));

// Hold to authenticate; sample state every 400ms.
await page.mouse.move(640, 360);
await page.mouse.down();
for (let i = 0; i < 10; i++) { await sleep(400); console.log(`hold+${(i+1)*0.4}s`, JSON.stringify(await state())); }
await page.mouse.up();
for (let i = 0; i < 8; i++) { await sleep(500); console.log(`post+${(i+1)*0.5}s`, JSON.stringify(await state())); }

// Now probe each scene via jump with a bounded wait + error capture.
for (const id of ['infrastructure', 'augmentation', 'prediction', 'black-vault', 'mirror']) {
  try {
    const before = Date.now();
    await page.evaluate((i) => window.__sovereign.jump(i), id);
    await sleep(3000);
    const st = await state();
    // is the canvas non-black? sample center pixel brightness via screenshot buffer size heuristic
    const buf = await page.screenshot();
    console.log(`jump ${id}: ${Date.now()-before}ms  state=${JSON.stringify(st)}  pngBytes=${buf.length}`);
  } catch (e) {
    console.log(`jump ${id} THREW: ${e.message}`);
  }
}
await browser.close();
console.log('DIAGNOSE COMPLETE');
