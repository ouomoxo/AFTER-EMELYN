import { chromium } from 'playwright';
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', headless: true, args: ['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist'] });
const p = await b.newPage({ viewport: { width: 1280, height: 720 } });
p.on('pageerror', e => console.log('[pageerror]', e.message));
await p.addInitScript(() => { try { localStorage.setItem('sovereign.tier','A'); } catch{} });
await p.goto('http://localhost:4173', { waitUntil: 'domcontentloaded' });
await sleep(3200);
await p.evaluate(() => window.__sovereign.jump('infrastructure'));
await sleep(2600);
// Scrub via the timeline directly (no wheel events → no SwiftShader crash).
await p.evaluate(() => window.__sovereign.engine.timeline.setTarget(0.35)); await sleep(2500);
await p.screenshot({ path: 'docs/_ref/web/I_mid.png' });
await p.evaluate(() => window.__sovereign.engine.timeline.setTarget(0.7)); await sleep(2500);
await p.screenshot({ path: 'docs/_ref/web/I_deep.png' });
console.log('infra tier:', await p.evaluate(() => window.__sovereign.getState().tier));
await b.close();
console.log('infra captured');
