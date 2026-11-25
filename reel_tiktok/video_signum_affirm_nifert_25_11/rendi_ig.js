// Carosello Instagram: html/<prodotto>_ig.html -> instagram/<prodotto>_sN.jpg (1080x1350). Uso: node rendi_ig.js signum affirm nifert
const { chromium } = require('playwright'); const path = require('path'), fs = require('fs');
(async () => { const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1080, height: 1350 } });
  const out = path.join(__dirname, 'instagram'); fs.mkdirSync(out, { recursive: true });
  for (const k of process.argv.slice(2)) { await p.goto('file://' + path.join(__dirname, 'html', k + '_ig.html')); await p.waitForTimeout(800);
    const over = await p.evaluate(() => [...document.querySelectorAll('.s')].map((s, i) => { const c = s.querySelector('.c'); const f = s.querySelector('.foot').getBoundingClientRect().top; return c.lastElementChild.getBoundingClientRect().bottom > f - 14 ? i + 1 : 0; }).filter(Boolean));
    if (over.length) console.log(k, 'TESTO OLTRE IL PIEDE', over);
    const els = p.locator('.s'); const n = await els.count();
    for (let i = 0; i < n; i++) await els.nth(i).screenshot({ path: path.join(out, `${k}_s${i + 1}.jpg`), type: 'jpeg', quality: 90 }); }
  await b.close(); })();
