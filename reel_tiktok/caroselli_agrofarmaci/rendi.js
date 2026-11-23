// Rende ogni file HTML (una slide per file) in PNG 1080x1920. Uso: node rendi.js <cartella_html>
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
(async () => {
  const dir = process.argv[2];
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  for (const f of fs.readdirSync(dir).filter(x => x.endsWith('.html')).sort()) {
    await p.goto('file://' + path.resolve(dir, f)); await p.waitForTimeout(300);
    const over = await p.evaluate(() => { const c = document.querySelector('.safe'); return c.scrollHeight > c.clientHeight + 1; });
    if (over) console.log('TROPPO TESTO:', f);
    await p.screenshot({ path: path.resolve(dir, f.replace('.html', '.png')) });
  }
  await b.close();
})();
