// Rende html/<prodotto>.html in <prodotto>/s1..sN.png (1080x1920). Uso: node rendi.js signum affirm nifert
const { chromium } = require('playwright'); const path = require('path'), fs = require('fs');
(async () => { const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  for (const k of process.argv.slice(2)) { fs.mkdirSync(path.join(__dirname, k), { recursive: true });
    await p.goto('file://' + path.join(__dirname, 'html', k + '.html')); await p.waitForTimeout(800);
    const over = await p.evaluate(() => [...document.querySelectorAll('.s')].map((s, i) => { const c = s.querySelector('.c'); const last = c.lastElementChild; const f = s.querySelector('.foot').getBoundingClientRect().top; return last.getBoundingClientRect().bottom > f - 20 ? i + 1 : 0; }).filter(Boolean));
    if (over.length) console.log(k, 'TESTO OLTRE IL PIEDE nelle slide', over);
    const els = p.locator('.s'); const n = await els.count();
    for (let i = 0; i < n; i++) await els.nth(i).screenshot({ path: path.join(__dirname, k, `s${i + 1}.png`) }); }
  await b.close(); })();
