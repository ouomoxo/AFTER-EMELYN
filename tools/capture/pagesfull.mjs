import { chromium } from 'playwright';
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', headless: true, args: ['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist'] });
const p = await b.newPage({ viewport: { width: 1280, height: 720 } });
const errs = [];
p.on('response', r => { if (r.status() >= 400) errs.push(r.status()+' '+r.url().replace('http://127.0.0.1:8090','')); });
p.on('pageerror', e => errs.push('JS: '+e.message));
await p.goto('http://127.0.0.1:8090/AFTER-EMELYN/', { waitUntil: 'domcontentloaded' });
await sleep(4000);
const s1 = await p.evaluate(() => window.__sovereign.getState());
console.log('boot:', s1.scene, 'tier', s1.tier, 'url', p.url());
await p.screenshot({ path: 'docs/_ref/web/pages_boot.png' });
// jump to a later scene → proves GLB + Draco load after the URL was rewritten
await p.evaluate(() => window.__sovereign.jump('augmentation'));
await sleep(3500);
console.log('after jump:', await p.evaluate(() => window.__sovereign.getState().scene), 'url', p.url());
await p.screenshot({ path: 'docs/_ref/web/pages_augmentation.png' });
console.log('4xx / JS errors:', errs.length ? errs.slice(0,10) : 'NONE');
await b.close();
