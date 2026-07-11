import { chromium } from 'playwright';
const sleep = ms => new Promise(r=>setTimeout(r,ms));
const b = await chromium.launch({ executablePath:'/opt/pw-browsers/chromium-1194/chrome-linux/chrome', headless:true, args:['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist'] });
async function shot(tier, dpr, name){
  const ctx = await b.newContext({ viewport:{width:900,height:1000}, deviceScaleFactor:dpr });
  const p = await ctx.newPage();
  await p.addInitScript(t=>{try{localStorage.setItem('sovereign.tier',t)}catch{}}, tier);
  await p.goto('http://localhost:5174/', { waitUntil:'domcontentloaded' }); await sleep(4500);
  await p.evaluate(()=>window.__sovereign.jump('augmentation')); await sleep(4000);
  await p.screenshot({ path:`docs/_ref/web/qual_${name}.png` });
  console.log(name, 'tier', await p.evaluate(()=>window.__sovereign.getState().tier));
  await ctx.close();
}
await shot('C', 2, 'mobileC');   // what mobile users see
await shot('A', 1.5, 'deskA');   // best tier
await b.close();
