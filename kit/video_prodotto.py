#!/usr/bin/env python3
"""Video TikTok di un prodotto nello stile approvato (Enervin, 28/11/2026).
Uso: python3 kit/video_prodotto.py kit/prodotti_video/<id>.json
Pagine: 1 copertina laterale con il problema in grande, 2 dosi, 3 a cosa serve, 4 lo sapevi.
Scrive settimane/2026-11-30/img/<id>_1..4.jpg, reel_tiktok/<id>_tiktok.mp4, kit/prodotti_video/<id>_didascalia.txt"""
import sys, json, subprocess
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import s4kit as K
from playwright.sync_api import sync_playwright
from PIL import Image
u = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
OUT = K.REPO / "settimane" / "2026-11-30" / "img"; OUT.mkdir(parents=True, exist_ok=True)
c = u["copertina"]
css = K.CSS_POST + """
.txt{position:absolute;left:80px;top:150px;width:590px;display:flex;flex-direction:column;gap:18px}
.l{white-space:nowrap;font-weight:800;line-height:1;letter-spacing:-3px}
.sub{font-size:44px;font-weight:600;line-height:1.25;margin-top:26px}.sub span{color:var(--acc)}
.bot{position:absolute;right:60px;top:150px;height:900px;width:330px;display:flex;justify-content:center;align-items:center}
.bot img{max-height:100%;max-width:100%}
.box2{position:absolute;left:80px;right:80px;bottom:130px;border-radius:40px;padding:30px 44px;font-size:36px;font-weight:700;line-height:1.28}
.sw{position:absolute;left:80px;bottom:66px;font-size:30px;font-weight:700;color:var(--acc)}
"""
righe = "" if "titolo" in c else "".join(f'<div class="l" data-max="{m}" style="color:var(--{"dark" if i == 0 else "acc"})">{t}</div>' for i, (t, m) in enumerate(c["righe"]))
bw = c.get("larghezza_foto", 330)
cover = (f'<div class="s" style="{K._vars(u["colore"])}"><div class="tag"><span class="dot"></span>{c["tag"]}</div>'
         f'<img class="logo" src="{K.LOGO.as_uri()}"><div class="num">1/4</div>'
         f'<div class="txt" style="width:{920-bw-20}px">{righe}<div class="sub">{c["sotto"]}</div></div>'
         f'<div class="bot" style="width:{bw}px"><img class="sh" src="{K._foto(u["foto"])}"></div>'
         f'<div class="box2 scuro">{c["box"]}</div><div class="sw">scorri →</div></div>')
js = ""
FIT = "async()=>{await document.fonts.ready;document.querySelectorAll('.l').forEach(e=>{e.style.display='inline-block';e.style.alignSelf='flex-start';let W=e.parentElement.clientWidth,f=+e.dataset.max;e.style.fontSize=f+'px';while(e.getBoundingClientRect().width>W&&f>40){f--;e.style.fontSize=f+'px'}});return 1}"
html_cover = f"<!DOCTYPE html><html><head><meta charset='utf-8'><style>{css}</style></head><body>{cover}{js}</body></html>"
STD = "titolo" in c   # copertina standard come gli altri post (Valerio 28/11 11:17)
resto = {"tipo": "carosello", "colore": u["colore"], "argomento": u["argomento"],
         "slide": [{"tipo": "copertina", "tag": c.get("tag"), "titolo": c.get("titolo", "x"), "sotto": c.get("sotto", "x"),
                    "box": c.get("box", "x"), "foto": u["foto"]}] + u["slide"]}
html_resto = K.html_carosello(resto)
K.TMP.mkdir(exist_ok=True)
files = [OUT / f'{u["id"]}_{i}.jpg' for i in range(1, 5)]
with sync_playwright() as pw:
    b = pw.chromium.launch(); p = b.new_page(viewport={"width": 1080, "height": 1350})
    if not STD:
        f = K.TMP / "cov.html"; f.write_text(html_cover, encoding="utf-8"); p.goto(f.as_uri()); p.wait_for_timeout(700); p.evaluate(FIT)
        print("copertina, dimensioni righe:", p.evaluate("()=>[...document.querySelectorAll('.l')].map(e=>e.style.fontSize)"))
        p.locator(".s").screenshot(path=str(K.TMP / "s.png")); Image.open(K.TMP / "s.png").convert("RGB").save(files[0], quality=92)
    f = K.TMP / "resto.html"; f.write_text(html_resto, encoding="utf-8"); p.goto(f.as_uri()); p.wait_for_timeout(600)
    fits = p.evaluate(K.JS_FIT); print("adattamento pagine:", fits)
    if STD:  # copertina: solo il titolo si adatta (max 100px), il sottotitolo resta a 40px come negli altri post
        print("titolo copertina px:", p.evaluate("""() => { const b=document.querySelector('.cvtxt'), z=b.querySelector('.zz'), h=z.querySelector('h1');
          z.style.zoom=1; let f=100; h.style.fontSize=f+'px';
          while ((h.scrollWidth>b.clientWidth+1 || b.scrollHeight>b.clientHeight+1) && f>56) { f--; h.style.fontSize=f+'px'; }
          return f; }"""))
    for i in (range(0, 4) if STD else range(1, 4)):
        p.locator(".s").nth(i).screenshot(path=str(K.TMP / "s.png")); Image.open(K.TMP / "s.png").convert("RGB").save(files[i], quality=92)
    b.close()
e, a = K.controlla_testi({**resto, "prodotti": u["prodotti"], "didascalia": u["didascalia"], "tipo": "carosello", "slide": u["slide"]}, json.loads((K.KIT / "prodotti.json").read_text(encoding="utf-8")))
print("controlli:", [x for x in e if "storia" not in x and "campo" not in x], a)
(K.KIT / "prodotti_video" / f'{u["id"]}_didascalia.txt').write_text(K.didascalia_finale(u["didascalia"]), encoding="utf-8")
subprocess.run(["bash", str(K.KIT / "mkvid.sh"), str(K.REPO / "reel_tiktok" / f'{u["id"]}_tiktok.mp4')] + [str(x) for x in files], check=True)
print("video:", K.REPO / "reel_tiktok" / f'{u["id"]}_tiktok.mp4')
