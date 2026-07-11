/**
 * SOVEREIGN//77 — two-slice verification capture (HANDSHAKE + HUMAN REVISION).
 * Shoots the actual runtime look of the rebuilt slices: handshake establishing →
 * engaged → pressed → authenticated/open (tunnel), and the module assembled →
 * exploded. Landscape tier A + one portrait tier C mobile check.
 *
 * Usage: node tools/capture/slices.mjs [baseUrl]
 */
import { chromium } from 'playwright';
import { mkdirSync } from 'node:fs';

const BASE = process.argv[2] || 'http://localhost:4173/AFTER-EMELYN/';
const OUT = 'docs/_ref/web';
mkdirSync(OUT, { recursive: true });
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

const browser = await chromium.launch({
  executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome',
  headless: true,
  args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'],
});

async function ctx(vp, tier, dpr = 1.5) {
  const c = await browser.newContext({ viewport: vp, deviceScaleFactor: dpr });
  const p = await c.newPage();
  p.on('pageerror', (e) => console.log('  [pageerror]', e.message));
  await p.addInitScript((t) => { try { localStorage.setItem('sovereign.tier', t); } catch {} }, tier);
  return { c, p };
}
const state = (p) => p.evaluate(() => window.__sovereign?.getState?.() ?? {});

// ---- Landscape, tier A ----
{
  const { c, p } = await ctx({ width: 1280, height: 720 }, 'A');
  await p.goto(BASE, { waitUntil: 'domcontentloaded' });
  await sleep(3500);
  await p.screenshot({ path: `${OUT}/hs_1_establish.png` });
  console.log('hs establish', (await state(p)).scene, (await state(p)).backend);
  // engage: move the cursor to wake + push in
  for (let i = 0; i < 16; i++) { await p.mouse.move(520 + i * 16, 340 + Math.sin(i / 3) * 40); await sleep(45); }
  await sleep(1500);
  await p.screenshot({ path: `${OUT}/hs_2_engage.png` });
  // press + hold to push fully in on the core
  await p.mouse.move(640, 360); await p.mouse.down(); await sleep(1300);
  await p.screenshot({ path: `${OUT}/hs_3_press.png` });
  await p.mouse.up();
  await c.close();
}
// open/tunnel via ?freezeopen (authenticates + holds the parted door)
{
  const { c, p } = await ctx({ width: 1280, height: 720 }, 'A');
  await p.goto(`${BASE}?freezeopen`, { waitUntil: 'domcontentloaded' });
  await sleep(4500);
  await p.screenshot({ path: `${OUT}/hs_4_open.png` });
  console.log('hs open', (await state(p)).scene);
  await c.close();
}
// module assembled + exploded
{
  const { c, p } = await ctx({ width: 1280, height: 720 }, 'A');
  await p.goto(BASE, { waitUntil: 'domcontentloaded' });
  await sleep(3200);
  await p.evaluate(() => window.__sovereign.jump('augmentation'));
  await sleep(3200);
  await p.screenshot({ path: `${OUT}/mod_1_assembled.png` });
  console.log('mod', (await state(p)).scene, 'progress', (await state(p)).progress?.toFixed?.(2));
  // Scrub the layers apart, but STOP before the gate so it doesn't advance.
  for (let i = 0; i < 40; i++) {
    const pr = (await state(p)).progress ?? 0;
    if (pr >= 0.72) break;
    await p.mouse.wheel(0, 130); await sleep(70);
  }
  await sleep(1300);
  await p.screenshot({ path: `${OUT}/mod_2_explode.png` });
  console.log('mod explode', (await state(p)).scene, 'progress', (await state(p)).progress?.toFixed?.(2));
  await c.close();
}
// ---- Portrait mobile, tier C ----
{
  const { c, p } = await ctx({ width: 900, height: 1000 }, 'C', 2);
  await p.goto(BASE, { waitUntil: 'domcontentloaded' });
  await sleep(3500);
  await p.screenshot({ path: `${OUT}/m_hs_establish.png` });
  await p.evaluate(() => window.__sovereign.jump('augmentation'));
  await sleep(3200);
  await p.screenshot({ path: `${OUT}/m_mod.png` });
  console.log('mobile', (await state(p)).scene, (await state(p)).tier);
  await c.close();
}

await browser.close();
console.log('✓ slice captures in', OUT);
