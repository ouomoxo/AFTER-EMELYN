/** Mirror epilogue capture — no wheel events (assembles on a timer), avoids the SwiftShader scrub crash. */
import { chromium } from 'playwright';
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', headless: true, args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
const p = await b.newPage({ viewport: { width: 1280, height: 720 } });
p.on('pageerror', (e) => console.log('[pageerror]', e.message));
await p.addInitScript(() => { try { localStorage.setItem('sovereign.tier', 'B'); } catch {} });
await p.goto('http://localhost:4173', { waitUntil: 'domcontentloaded' });
await sleep(3200);
await p.evaluate(() => window.__sovereign.jump('mirror'));
await sleep(7000); // let the replica assemble (~6s wall-clock)
await p.screenshot({ path: 'docs/_ref/web/M1_mirror.png' });
console.log('scene:', await p.evaluate(() => window.__sovereign.getState().scene), 'interaction:', await p.evaluate(() => window.__sovereign.getState().interaction));
await p.mouse.move(560, 520); await sleep(600);
await p.screenshot({ path: 'docs/_ref/web/M2_choices.png' });
await b.close();
console.log('mirror captured');
