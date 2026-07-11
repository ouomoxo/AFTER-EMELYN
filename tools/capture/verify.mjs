/** Verify second-visit staging and reduced-motion (Tier D). Minimal load + one shot each. */
import { chromium } from 'playwright';
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const exe = '/opt/pw-browsers/chromium-1194/chrome-linux/chrome';
const args = ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'];
const get = (p) => p.evaluate(() => { const s = window.__sovereign?.getState?.(); return s ? { scene: s.scene, tier: s.tier, line: s.systemLine, second: s.secondVisit, reduced: s.reducedMotion } : null; });

// 1) SECOND VISIT — pre-seed the "seen" flag the epilogue plants.
{
  const b = await chromium.launch({ executablePath: exe, headless: true, args });
  const p = await b.newPage({ viewport: { width: 1280, height: 720 } });
  await p.addInitScript(() => { try { localStorage.setItem('sovereign.tier', 'B'); localStorage.setItem('sovereign.seen', '1'); } catch {} });
  await p.goto('http://localhost:4173', { waitUntil: 'domcontentloaded' });
  await sleep(3500);
  console.log('SECOND VISIT:', JSON.stringify(await get(p)));
  await p.screenshot({ path: 'docs/_ref/web/S1_second_visit.png' });
  await b.close();
}

// 2) REDUCED MOTION — should resolve to Tier D.
{
  const b = await chromium.launch({ executablePath: exe, headless: true, args });
  const ctx = await b.newContext({ viewport: { width: 1280, height: 720 }, reducedMotion: 'reduce' });
  const p = await ctx.newPage();
  await p.goto('http://localhost:4173', { waitUntil: 'domcontentloaded' });
  await sleep(3500);
  console.log('REDUCED MOTION:', JSON.stringify(await get(p)));
  await b.close();
}
console.log('verify done');
