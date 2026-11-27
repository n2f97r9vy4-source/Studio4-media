#!/usr/bin/env python3
"""Caroselli TikTok nello stile dei video già pubblicati (QZyme, Razormin, Cidely, Turbo Root):
slide del kit 1080x1350 (kit/s4kit.py: logo in alto a destra, senza cornice) al centro di un fondo 1080x1920
fatto dalla stessa slide sfocata. Uscite: <prodotto>/s1..sN.png (9:16) e, se "video": true, <prodotto>_tiktok.mp4.
Uso: NODE_PATH=$(npm root -g) python3 genera_kit.py            (tutti i prodotti)
     NODE_PATH=$(npm root -g) python3 genera_kit.py juvinal    (solo i prodotti indicati, gli altri non si toccano)

Copertina su misura "copertina_formula" (27/11/2026, richiesta di Valerio sulla copertina di MKP: "deve essere più
attraente e far capire che si parla di MKP"): sigla del concime in grande, titolo N-P-K in tre riquadri come sul sacco,
frase su cosa risolve, modi d'uso, sacco grande su un cerchio colorato. Sfondo, logo, etichetta in alto, riquadro scuro
e "scorri" restano quelli del kit; kit/s4kit.py non viene toccato. Campi della slide:
  tag, nome (la sigla), formula [[numero, etichetta, "evidenza"?], ...], titolo, modi [[emoji, testo], ...], foto, box.
"""
import json, subprocess, sys
from pathlib import Path
from PIL import Image, ImageFilter, ImageEnhance
QUI = Path(__file__).resolve().parent; REPO = QUI.parent.parent
sys.path.insert(0, str(REPO / "kit")); import s4kit as k

def nove_sedicesimi(src, dst):
    s = Image.open(src).convert("RGB")
    bg = s.resize((1536, 1920)).crop((228, 0, 1308, 1920)).filter(ImageFilter.GaussianBlur(40))
    bg = ImageEnhance.Brightness(bg).enhance(1.04)
    bg.paste(s, (0, 285)); bg.save(dst)

# ---------------------------------------------------------------- copertina su misura "formula"
ARANCIO = "#DF502E"   # arancio Studio 4: solo per il riquadro in evidenza (es. lo zero dell'azoto)
CSS_FORMULA = """
.fxdisc{position:absolute;left:572px;top:282px;width:720px;height:720px;border-radius:50%;
 background:linear-gradient(150deg,color-mix(in srgb,var(--acc) 72%,#fff) 0%,var(--acc) 66%,color-mix(in srgb,var(--acc) 80%,var(--dark)) 100%)}
.fxfoto{position:absolute;left:512px;top:318px;width:505px}
.fxnome{position:absolute;left:72px;top:128px;font-size:236px;font-weight:700;letter-spacing:-9px;line-height:1;color:var(--dark);white-space:nowrap}
.fxchips{position:absolute;left:80px;top:404px;display:flex;gap:14px}
.fxchip{width:130px}
.fxchip b{display:flex;align-items:center;justify-content:center;height:94px;border-radius:24px;background:var(--dark);color:#fff;font-size:60px;font-weight:700}
.fxchip.ev b{background:ARANCIO}
.fxchip span{display:block;text-align:center;margin-top:8px;font-size:20px;font-weight:700;letter-spacing:2px;text-transform:uppercase;color:var(--acc)}
.fxtit{position:absolute;left:80px;top:590px;width:430px;font-size:53px;line-height:1.07;font-weight:700;letter-spacing:-1.5px}
.fxmodi{position:absolute;left:80px;top:818px;display:flex;flex-direction:column;align-items:flex-start;gap:12px}
.fxmodo{background:#fff;border-radius:999px;box-shadow:0 10px 26px rgba(0,0,0,.10);font-size:27px;font-weight:700;display:flex;align-items:center;gap:12px;padding:12px 24px 12px 18px}
.fxmodo i{font-style:normal;font-size:32px;line-height:1}
.fxbox{position:absolute;left:80px;right:80px;bottom:140px}
.fxswipe{position:absolute;left:80px;bottom:70px}
""".replace("ARANCIO", ARANCIO)

def copertina_formula(c, s, T):
    chips = "".join(f'<div class="fxchip{" ev" if len(v) > 2 and v[2] == "evidenza" else ""}"><b>{v[0]}</b><span>{v[1]}</span></div>'
                    for v in s["formula"])
    modi = "".join(f'<div class="fxmodo"><i>{e}</i>{t}</div>' for e, t in s.get("modi", []))
    # il riquadro nascosto serve solo a tenere allineati i numeri di slide negli avvisi di rendi_kit.js
    return (f'<div class="s" style="{k._vars(c["colore"])}"><div class="tag"><span class="dot"></span>{s["tag"]}</div>'
            f'<img class="logo" src="{k.LOGO.as_uri()}"><div class="num">1/{T}</div>'
            f'<div class="fitbox" data-min="1" data-max="1" style="display:none"><div class="zz"></div></div>'
            f'<div class="fxdisc"></div><img class="fxfoto sh" src="{k._foto(s["foto"])}">'
            f'<div class="fxnome">{s["nome"]}</div><div class="fxchips">{chips}</div>'
            f'<h1 class="fxtit">{s["titolo"]}</h1><div class="fxmodi">{modi}</div>'
            f'<div class="fxbox cvbox scuro">{s["box"]}</div><div class="fxswipe swipe">scorri →</div></div>')

def html_carosello(c):
    """Come k.html_carosello; se la prima slide è "copertina_formula" la disegna qui e lascia al kit tutte le altre."""
    s0 = c["slide"][0]
    if s0["tipo"] != "copertina_formula":
        return k.html_carosello(c)
    finta = {"tipo": "copertina", "titolo": "", "sotto": "", "box": ""}
    SEP = '<div class="s" style="'
    pezzi = k.html_carosello(dict(c, slide=[finta] + c["slide"][1:])).split(SEP)
    assert len(pezzi) == len(c["slide"]) + 1, "struttura dell'HTML del kit cambiata"
    return (pezzi[0].replace("</style>", CSS_FORMULA + "</style>") + copertina_formula(c, s0, len(c["slide"]))
            + "".join(SEP + p for p in pezzi[2:]))

# ---------------------------------------------------------------- resa
DISC_FITO = k.DISC
IG = QUI / "instagram_kit"; IG.mkdir(exist_ok=True)
jsf = QUI / ".js_fit.txt"; jsf.write_text(k.JS_FIT)
SOLO = set(sys.argv[1:])
for c in json.loads((QUI / "caroselli_kit.json").read_text(encoding="utf-8")):
    if SOLO and c["id"] not in SOLO: continue
    k.DISC = DISC_FITO if c.get("fito", True) else "Prima dell'uso leggere sempre l'etichetta del prodotto."
    out = QUI / ("kit_" + c["id"]); out.mkdir(exist_ok=True)
    for f in out.glob("*.png"): f.unlink()
    html = QUI / f".{c['id']}.html"; html.write_text(html_carosello(c), encoding="utf-8")
    r = subprocess.run(["node", str(QUI / "rendi_kit.js"), str(html), str(jsf), str(out)], capture_output=True, text=True)
    print(c["id"], r.stdout.strip(), r.stderr.strip()[-300:]); html.unlink()
    for i in range(len(c["slide"])):
        kp = out / f"k{i+1}.png"; nove_sedicesimi(kp, out / f"s{i+1}.png")
        Image.open(kp).convert("RGB").save(IG / f"{c['id']}_s{i+1}.jpg", quality=92); kp.unlink()
    if c.get("video"):
        subprocess.run([str(QUI / "video.sh"), str(out), str(QUI / f"{c['id']}_tiktok.mp4")], check=True)
jsf.unlink()
