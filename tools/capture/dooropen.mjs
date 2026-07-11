import { chromium } from 'playwright';
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', headless: true, args: ['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist'] });
const p = await b.newPage({ viewport: { width: 1280, height: 720 } });
p.on('pageerror', e => console.log('[pageerror]', e.message));
await p.addInitScript(() => { try { localStorage.setItem('sovereign.tier','A'); } catch{} });
await p.goto('http://localhost:4173/?freezeopen', { waitUntil: 'domcontentloaded' });
await sleep(5500); // let the open sequence play + settle at held-open
await p.screenshot({ path: 'docs/_ref/web/H_door_open.png' });
console.log('scene:', await p.evaluate(() => window.__sovereign.getState().scene), 'inter:', await p.evaluate(() => window.__sovereign.getState().interaction));
await b.close(); console.log('door-open captured');
