// Rende un HTML del kit (slide .s 1080x1350) applicando lo stesso adattamento del testo di kit/s4kit.py. Uso: node rendi_kit.js file.html js_fit.txt cartella_out
const { chromium } = require('playwright'); const fs = require('fs'), path = require('path');
(async () => {
  const [html, jsf, out] = process.argv.slice(2);
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1080, height: 1350 } });
  await p.goto('file://' + path.resolve(html)); await p.waitForTimeout(500);
  const fits = await p.evaluate(eval(fs.readFileSync(jsf, 'utf8')));
  fits.forEach(([ok, k], i) => { if (!ok || k < 0.86) console.log(`slide ${i + 1}: ${ok ? 'testo fitto' : 'TROPPO TESTO'} (scala ${k})`); });
  const els = p.locator('.s'); const n = await els.count();
  for (let i = 0; i < n; i++) await els.nth(i).screenshot({ path: path.join(out, `k${i + 1}.png`) });
  await b.close();
})();
