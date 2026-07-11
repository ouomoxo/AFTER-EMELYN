import { chromium } from 'playwright';
const sleep = ms => new Promise(r=>setTimeout(r,ms));
const b = await chromium.launch({ executablePath:'/opt/pw-browsers/chromium-1194/chrome-linux/chrome', headless:true, args:['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist'] });
const p = await b.newPage({ viewport:{width:1280,height:720} });
await p.addInitScript(()=>{try{localStorage.setItem('sovereign.tier','B')}catch{}});
await p.goto('http://localhost:5174/?debug', { waitUntil:'domcontentloaded' }); await sleep(9000);
// audio synthesis proof
const peak = await p.evaluate(async()=> await window.__sovereign.audioProof());
console.log('AUDIO peak amplitude:', peak.toFixed(4), peak>0.01? 'AUDIBLE ✓':'SILENT ✗');
// perf HUD populated?
const perf = await p.evaluate(()=>window.__sovereign.getState().perf);
console.log('PERF fps='+perf.fps, 'draw='+perf.drawCalls, 'tris='+perf.triangles);
await p.screenshot({ path:'docs/_ref/web/debug_hud.png' });
await b.close();
