// Fotogrammi di un video animato in HTML (1080x1920): ferma tutte le animazioni e le porta, fotogramma per fotogramma, al tempo giusto.
// Uso: node rendi_video.js file.html cartella_fotogrammi durata_secondi [fps] [elenco,di,fotogrammi]
const { chromium } = require('playwright'); const fs = require('fs'), path = require('path');
const ADATTA = `() => {
  const out = [];
  document.querySelectorAll('[data-min]').forEach(e => {
    const min = parseFloat(e.dataset.min), inn = e.firstElementChild; let fs = parseFloat(getComputedStyle(e).fontSize);
    const ok = () => inn.offsetHeight <= e.clientHeight + 1 && inn.scrollWidth <= inn.clientWidth + 1;
    while (!ok() && fs > min) { fs -= 2; e.style.fontSize = fs + 'px'; }
    if (!ok()) out.push('AVVISO ' + (e.id || e.className) + ': testo troppo lungo (' + e.textContent.slice(0, 40) + ')');
  });
  // zona libera di TikTok: i blocchi con data-fondo devono finire sopra quella quota
  const sotto = e => e.offsetTop + e.offsetHeight - parseFloat(e.dataset.fondo);
  const sp = document.querySelector('#spiega[data-fondo]');
  if (sp && sotto(sp) > 0) {                       // la spiegazione non ci sta: si accorcia il riquadro della foto
    const ch0 = parseFloat(getComputedStyle(document.body).getPropertyValue('--ch')), ch = Math.max(420, ch0 - Math.ceil(sotto(sp)));
    document.body.style.setProperty('--ch', ch + 'px');
    out.push('nota: riquadro foto da ' + ch0 + ' a ' + ch + ' px per far stare la spiegazione');
  }
  document.querySelectorAll('[data-fondo]').forEach(e => {
    if (e.dataset.minf) { let fs = parseFloat(getComputedStyle(e).fontSize); while (sotto(e) > 0 && fs > parseFloat(e.dataset.minf)) { fs -= 1; e.style.fontSize = fs + 'px'; } }
    if (sotto(e) > 0) out.push('AVVISO ' + e.id + ': finisce ' + Math.round(sotto(e)) + ' px sotto la zona libera');
  });
  return out;
}`;
(async () => {
  const [html, out, dur, fps = '30', solo] = process.argv.slice(2);
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
  await p.goto('file://' + path.resolve(html)); await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(500);
  await p.evaluate(() => document.getAnimations().forEach(a => a.pause()));
  const avvisi = await p.evaluate(eval(ADATTA));
  avvisi.forEach(a => console.log(a));
  const N = Math.round(parseFloat(dur) * fps);
  const quali = solo ? solo.split(',').map(Number) : [...Array(N).keys()];
  for (const i of quali) {
    await p.evaluate(t => document.getAnimations().forEach(a => { a.currentTime = t; }), i * 1000 / fps);
    await p.screenshot({ path: path.join(out, `f${String(i).padStart(5, '0')}.jpg`), type: 'jpeg', quality: 96 });
  }
  await b.close();
})();
