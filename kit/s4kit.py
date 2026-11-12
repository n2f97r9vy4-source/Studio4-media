#!/usr/bin/env python3
"""STUDIO 4 MEDIA — kit grafico e controlli.
Da una specifica (spec.json) produce caroselli 1080x1350 e storie 1080x1920 nello stile approvato da Valerio.
Non modificare lo stile qui senza una richiesta esplicita di Valerio: lo stile è deciso.
"""
import json, re, datetime
from pathlib import Path

KIT = Path(__file__).resolve().parent
REPO = KIT.parent
FOTO = KIT / "assets" / "foto"
LOGO = KIT / "assets" / "logo_s4.png"
TMP = KIT / ".tmp"
DISC = ("Usare i prodotti fitosanitari con precauzione. Prima dell'uso leggere sempre l'etichetta "
        "e le informazioni sul prodotto. Vendita ai possessori di patentino.")

# nome: (accento, scuro, sfondo chiaro 1, sfondo chiaro 2, evidenza per le storie)
PALETTE = {
    "studio4":    ("#1B9A4B", "#0E3B22", "#F2F8F3", "#D6EBDC", "#C8F2D6"),
    "verde":      ("#2B8A3E", "#123D1C", "#F1F8F1", "#D3EAD5", "#B9E8C2"),
    "oliva":      ("#6E8B1E", "#2D3A0B", "#F6F8EC", "#E2E9C8", "#DDEB9E"),
    "smeraldo":   ("#1F8A5B", "#0C3B26", "#EFF8F3", "#CFEBDD", "#B5EBD0"),
    "petrolio":   ("#1F7A7A", "#0F3B3B", "#EEF8F8", "#CFE9E8", "#9FE0D8"),
    "blu":        ("#2E7DB5", "#0E2F47", "#EFF5FB", "#D0E3F2", "#B3D7F2"),
    "azzurro":    ("#0277BD", "#01304F", "#EEF7FC", "#CDE7F6", "#B3E5FC"),
    "indaco":     ("#3949AB", "#141B4D", "#F1F2FB", "#D5D9F2", "#FFD54F"),
    "viola":      ("#6B3FA0", "#2A1445", "#F6F1FB", "#E0D2F2", "#D9C2F5"),
    "magenta":    ("#C2185B", "#4A0A24", "#FCF0F5", "#F3D2E0", "#F9B8D2"),
    "rosso":      ("#C0392B", "#4A1410", "#FDF1EF", "#F4D5D0", "#FFB4A8"),
    "arancio":    ("#E64A19", "#4A160A", "#FEF2EC", "#F9D9CB", "#FFD3C2"),
    "terracotta": ("#B4561E", "#3E1C0A", "#FBF3EC", "#F0DCCB", "#FFC79A"),
    "marrone":    ("#9A5A24", "#3B2412", "#FBF4EA", "#EBD5B9", "#F2C994"),
    "giallo":     ("#D99A00", "#5A3E00", "#FFF9E8", "#FBEBB8", "#FFE08A"),
    "grigio":     ("#5B5F6B", "#23262E", "#F4F5F7", "#DDE0E6", "#D7DCE6"),
}

def _pal(nome):
    if nome not in PALETTE:
        raise ValueError(f"colore sconosciuto: {nome}. Disponibili: {', '.join(PALETTE)}")
    return PALETTE[nome]

def _foto(nome):
    p = FOTO / f"{nome}.png"
    if not p.exists():
        raise FileNotFoundError(f"foto '{nome}' non presente in kit/assets/foto (disponibili: {', '.join(sorted(x.stem for x in FOTO.glob('*.png')))})")
    return p.as_uri()

FONT = "".join(
    f"@font-face{{font-family:P;src:url({(KIT/'fonts'/f).as_uri()});font-weight:{w}}}"
    for f, w in [("Poppins-Regular.ttf", 400), ("Poppins-Medium.ttf", 500), ("Poppins-Bold.ttf", 600),
                 ("Poppins-Bold.ttf", 700), ("Poppins-Bold.ttf", 800)])

CSS_POST = FONT + """
*{box-sizing:border-box;margin:0;padding:0}
body{background:#888}
.s{width:1080px;height:1350px;position:relative;overflow:hidden;font-family:P,'Noto Color Emoji',sans-serif;color:var(--dark);
 background:linear-gradient(160deg,var(--bg1) 0%,var(--bg2) 100%);margin-bottom:20px}
.tag{position:absolute;top:70px;left:80px;font-size:25px;font-weight:700;letter-spacing:3px;color:var(--acc);text-transform:uppercase;max-width:660px;white-space:nowrap;overflow:hidden}
.num{position:absolute;top:70px;right:80px;font-size:26px;font-weight:700;color:var(--acc)}
.logo{position:absolute;left:762px;top:60px;width:180px}
.dot{display:inline-block;width:14px;height:14px;border-radius:50%;background:var(--acc);margin-right:14px}
em{font-style:normal;color:var(--acc)}
.card{background:#fff;border-radius:30px;padding:22px 32px;box-shadow:0 14px 40px rgba(0,0,0,.09)}
.col{position:absolute;left:80px;right:80px;top:140px;bottom:50px;display:flex;flex-direction:column;gap:22px}
.fit{flex:1;min-height:0;overflow:hidden}
.zz{display:flex;flex-direction:column;gap:22px;height:100%}
h2{font-size:64px;line-height:1.05;font-weight:700;letter-spacing:-1.5px}
.disc{font-size:21px;line-height:1.4;font-weight:500;color:var(--dark);opacity:.75;border-top:2px solid rgba(0,0,0,.15);padding-top:18px}
.sh{filter:drop-shadow(0 22px 26px rgba(0,0,0,.28))}
.scuro{background:var(--dark);color:#fff}
.cv{position:absolute;left:80px;right:80px;top:140px;bottom:70px;display:flex;flex-direction:column;gap:30px}
.cvtop{flex:1;min-height:0;display:flex;gap:30px}
.cvtxt{flex:1;min-width:0;overflow:hidden}
.cvtxt .zz{gap:44px;height:auto}
.cvmedia{flex:none;width:420px;display:flex;align-items:center;justify-content:center}
.cvmedia img{max-height:100%;max-width:100%}
h1{font-size:92px;line-height:1.03;font-weight:700;letter-spacing:-3px}
.cvsub{font-size:40px;font-weight:600;line-height:1.28}
.cvsub span,.hl{color:var(--acc)}
.cvbox{border-radius:40px;padding:32px 44px;font-size:36px;font-weight:700;line-height:1.28}
.swipe{font-size:30px;font-weight:700;color:var(--acc)}
"""

CSS_STORIA = FONT + """
*{margin:0;box-sizing:border-box}
body{width:1080px;height:1920px;position:relative;overflow:hidden;font-family:P,'Noto Color Emoji',sans-serif;color:#fff}
.logo{position:absolute;top:60px;right:60px;background:#fff;border-radius:18px;padding:12px 16px;line-height:0}.logo img{width:230px}
.w{position:absolute;left:70px;right:70px;top:230px;bottom:150px;display:flex;flex-direction:column;gap:44px}
h1{font-size:100px;line-height:1.03;font-weight:800;letter-spacing:-2px}
h1 em{font-style:normal;color:var(--hl)}
.media{flex:1;min-height:0;display:flex;align-items:center;justify-content:center;gap:50px}
.media img{max-height:100%;max-width:46%;object-fit:contain;filter:drop-shadow(0 26px 30px rgba(0,0,0,.35))}
.media img.solo{max-width:80%}
.emo{line-height:1;font-size:240px}
.box{background:rgba(255,255,255,.96);color:var(--dk);border-radius:34px;padding:34px 42px}
.lab{font-size:26px;font-weight:700;color:var(--ac);letter-spacing:2px;text-transform:uppercase}
.big{font-size:50px;font-weight:800;line-height:1.14;margin-top:8px}
.sm{font-size:34px;font-weight:600;margin-top:14px;line-height:1.3}
.st{height:250px;border:4px dashed rgba(255,255,255,.75);border-radius:34px;display:flex;align-items:center;justify-content:center;font-size:30px;font-weight:700;letter-spacing:2px;opacity:.9;text-transform:uppercase}
.foot{text-align:center;font-size:36px;font-weight:700}
"""

# ---------------------------------------------------------------- slide dei caroselli
def _punti(items, fs=28):
    return "".join(
        f'<div class="card" style="padding:16px 24px;display:flex;gap:16px;align-items:flex-start;border-radius:26px">'
        f'<span style="font-size:{fs+6}px;font-weight:700;color:var(--acc);line-height:1">✓</span>'
        f'<span style="font-size:{fs}px;font-weight:700;line-height:1.24">{t}</span></div>' for t in items)

def _numerati(items):
    return "".join(
        f'<div class="card" style="display:flex;gap:22px;align-items:flex-start">'
        f'<span style="font-size:40px;font-weight:700;color:var(--acc);min-width:44px;line-height:1.1">{i+1}</span>'
        f'<span style="font-size:31px;font-weight:600;line-height:1.3">{t}</span></div>' for i, t in enumerate(items))

def _chiusa(t):
    return f'<div style="font-size:28px;font-weight:700;color:var(--acc);line-height:1.3;padding:0 6px">{t}</div>' if t else ""

def sl_dose(s):
    cks = _punti(s.get("punti", []))
    return (f'<h2>{s["titolo"]}</h2><div style="display:flex;gap:26px;align-items:center;flex:1;min-height:0">'
            f'<div style="flex:none;width:330px;height:100%;display:flex;justify-content:center;align-items:center">'
            f'<img class="sh" src="{_foto(s["foto"])}" style="max-height:min(100%,780px);max-width:330px"></div>'
            f'<div style="flex:1;display:flex;flex-direction:column;gap:14px">'
            f'<div class="card scuro" style="padding:26px 30px;border-radius:32px">'
            f'<div style="font-size:22px;font-weight:700;letter-spacing:2px;opacity:.75;text-transform:uppercase">{s["etichetta"]}</div>'
            f'<div style="font-size:52px;font-weight:700;line-height:1.05;margin-top:6px">{s["valore"]}</div>'
            f'<div style="font-size:24px;font-weight:500;opacity:.85;margin-top:6px">{s.get("nota","")}</div></div>{cks}</div></div>')

def sl_grande(s):
    return (f'<h2>{s["titolo"]}</h2><div class="card scuro" style="padding:36px 42px;border-radius:38px">'
            f'<div style="font-size:26px;font-weight:700;letter-spacing:2px;opacity:.75;text-transform:uppercase">{s["etichetta"]}</div>'
            f'<div style="font-size:80px;font-weight:700;line-height:1.05;margin-top:8px">{s["valore"]}</div>'
            f'<div style="font-size:30px;font-weight:500;opacity:.85;margin-top:8px">{s.get("nota","")}</div></div>'
            + _punti(s.get("punti", []), 33) + _chiusa(s.get("chiusa")))

def sl_elenco(s):
    return f'<h2>{s["titolo"]}</h2>' + _numerati(s["punti"]) + _chiusa(s.get("chiusa"))

def sl_schede(s):
    return f'<h2>{s["titolo"]}</h2>' + "".join(
        f'<div class="card" style="display:flex;gap:22px;align-items:flex-start"><span style="font-size:40px;line-height:1.1">{e}</span>'
        f'<div><div style="font-size:33px;font-weight:700;line-height:1.2">{a}</div>'
        f'<div style="font-size:27px;font-weight:500;line-height:1.32;margin-top:6px;opacity:.88">{b}</div></div></div>'
        for e, a, b in s["voci"]) + _chiusa(s.get("chiusa"))

def sl_sapevi(s):
    return (f'<h2>Lo sapevi?<br><em>{s["titolo"]}</em></h2>'
            f'<div class="card scuro" style="padding:32px 38px;border-radius:36px">'
            f'<div style="font-size:42px;font-weight:700;line-height:1.15">{s["grande"]}</div>'
            f'<div style="font-size:29px;font-weight:500;opacity:.85;margin-top:10px;line-height:1.3">{s.get("piccolo","")}</div></div>'
            + _numerati(s.get("punti", [])) + _chiusa(s.get("chiusa")))

def sl_passi(s):
    rows = "".join(
        f'<div style="display:flex;gap:26px;align-items:center"><div style="flex:none;width:190px;min-height:104px;padding:10px;border-radius:30px;'
        f'background:{"var(--dark)" if i == 0 else "var(--acc)"};color:#fff;display:flex;align-items:center;justify-content:center;'
        f'font-size:30px;font-weight:700;text-align:center;line-height:1.1">{a}</div>'
        f'<div><div style="font-size:36px;font-weight:700;line-height:1.15">{b}</div>'
        f'<div style="font-size:27px;font-weight:500;line-height:1.3;opacity:.88;margin-top:4px">{c}</div></div></div>'
        for i, (a, b, c) in enumerate(s["passi"]))
    box = (f'<div class="card" style="font-size:29px;font-weight:700;line-height:1.28">{s["box"]}</div>' if s.get("box") else "")
    return f'<h2>{s["titolo"]}</h2><div style="display:flex;flex-direction:column;gap:20px">{rows}</div>{box}'

def sl_abbinamento(s):
    imgs = "".join(f'<img class="sh" src="{_foto(f)}" style="max-height:100%;max-width:{int(92/len(s["foto"]))}%">' for f in s["foto"])
    return (f'<h2>{s["titolo"]}</h2><div style="flex:1;min-height:200px;max-height:460px;display:flex;gap:30px;justify-content:center;align-items:flex-end">{imgs}</div>'
            + _punti(s.get("punti", []), 31) + _chiusa(s.get("chiusa")))

def sl_confronto(s):
    cols = ""
    for c in s["colonne"]:
        img = (f'<div style="height:300px;display:flex;justify-content:center;align-items:flex-end">'
               f'<img class="sh" src="{_foto(c["foto"])}" style="max-height:100%;max-width:100%"></div>') if c.get("foto") else ""
        rows = "".join(f'<div style="font-size:26px;font-weight:600;line-height:1.28;padding:10px 0;border-top:2px solid rgba(0,0,0,.08)">{r}</div>' for r in c["righe"])
        cols += (f'<div style="flex:1;min-width:0;display:flex;flex-direction:column;gap:14px">{img}'
                 f'<div class="card" style="padding:20px 24px;flex:1"><div style="font-size:32px;font-weight:700;color:var(--acc);line-height:1.1;padding-bottom:10px">{c["nome"]}</div>{rows}</div></div>')
    return f'<h2>{s["titolo"]}</h2><div style="display:flex;gap:20px;flex:1;min-height:0">{cols}</div>' + _chiusa(s.get("chiusa"))

def sl_scala(s):
    return f'<h2>{s["titolo"]}</h2>' + "".join(
        f'<div class="card" style="padding:16px 28px;border-radius:26px;display:flex;align-items:center;gap:24px">'
        f'<span style="flex:none;width:66px;height:66px;border-radius:50%;background:{c}"></span>'
        f'<span style="font-size:34px;font-weight:800;min-width:170px">{a}</span><span style="font-size:29px;font-weight:600;line-height:1.2">{b}</span></div>'
        for c, a, b in s["righe"]) + _chiusa(s.get("chiusa"))

SLIDE = {"dose": sl_dose, "grande": sl_grande, "elenco": sl_elenco, "schede": sl_schede, "sapevi": sl_sapevi,
         "passi": sl_passi, "abbinamento": sl_abbinamento, "confronto": sl_confronto, "scala": sl_scala}
TAG_DEFAULT = {"dose": "La dose giusta", "grande": "Il dato", "elenco": "In pratica", "schede": "In pratica", "sapevi": "Lo sapevi?",
               "passi": "Passo per passo", "abbinamento": "Con chi lo abbini", "confronto": "A confronto", "scala": "La guida"}

def _vars(colore):
    a, d, b1, b2, _ = _pal(colore)
    return f"--acc:{a};--dark:{d};--bg1:{b1};--bg2:{b2}"

def html_carosello(u):
    """u: uscita di tipo carosello. Ritorna l'HTML con tutte le slide."""
    T = len(u["slide"]); arg = u.get("argomento", "")
    out = []
    for i, s in enumerate(u["slide"]):
        n = i + 1
        head = f'<img class="logo" src="{LOGO.as_uri()}"><div class="num">{n}/{T}</div>'
        if s["tipo"] == "copertina":
            if i != 0:
                raise ValueError("la copertina deve essere la prima slide")
            if s.get("foto"):
                media = f'<div class="cvmedia"><img class="sh" src="{_foto(s["foto"])}"></div>'
            elif s.get("emoji"):
                media = f'<div class="cvmedia" style="width:300px"><span style="font-size:230px;line-height:1">{s["emoji"]}</span></div>'
            else:
                media = ""
            out.append(
                f'<div class="s" style="{_vars(u["colore"])}"><div class="tag"><span class="dot"></span>{s.get("tag", arg)}</div>{head}'
                f'<div class="cv"><div class="cvtop"><div class="cvtxt fitbox" data-min="0.62" data-max="1.12"><div class="zz">'
                f'<h1>{s["titolo"]}</h1><div class="cvsub">{s["sotto"]}</div></div></div>{media}</div>'
                f'<div class="cvbox scuro">{s["box"]}</div><div class="swipe">scorri →</div></div></div>')
            continue
        if s["tipo"] not in SLIDE:
            raise ValueError(f'tipo di slide sconosciuto: {s["tipo"]} (disponibili: copertina, {", ".join(SLIDE)})')
        tag = s.get("tag", TAG_DEFAULT[s["tipo"]]) + (f" · {arg}" if arg else "")
        fonte = s.get("fonte", "").strip()
        out.append(
            f'<div class="s" style="{_vars(u["colore"])}"><div class="tag"><span class="dot"></span>{tag}</div>{head}'
            f'<div class="col"><div class="fit fitbox" data-min="0.78" data-max="1.22"><div class="zz">{SLIDE[s["tipo"]](s)}</div></div>'
            f'<div class="disc">{fonte + " " if fonte else ""}{DISC}</div></div></div>')
    return f"<!DOCTYPE html><html><head><meta charset='utf-8'><style>{CSS_POST}</style></head><body>{''.join(out)}</body></html>"

# ---------------------------------------------------------------- storie
PIEDE = {"richiamo": "Il post completo è sul profilo →", "curiosita": "Ogni giorno una curiosità dal banco 🌱", "sondaggio": "Dicci la tua 👇"}

def html_storia(st, tipo):
    """st: {titolo, colore, foto:[..] | emoji, etichetta, grande, piccolo, adesivo?, piede?}"""
    a, d, _, _, hl = _pal(st["colore"])
    if st.get("foto"):
        fl = st["foto"] if isinstance(st["foto"], list) else [st["foto"]]
        media = "".join(f'<img {"class=solo " if len(fl) == 1 else ""}src="{_foto(f)}">' for f in fl[:2])
    else:
        media = f'<span class="emo">{st.get("emoji", "🌱")}</span>'
    box = (f'<div class="box"><div class="lab">{st["etichetta"]}</div><div class="big">{st["grande"]}</div>'
           + (f'<div class="sm">{st["piccolo"]}</div>' if st.get("piccolo") else "") + "</div>")
    stick = f'<div class="st">Spazio per l\'adesivo {st.get("adesivo", "sondaggio")}</div>' if tipo == "sondaggio" else ""
    piede = st.get("piede", PIEDE[tipo])
    return (f"<!DOCTYPE html><html><head><meta charset='utf-8'><style>{CSS_STORIA}</style></head>"
            f'<body style="background:linear-gradient(170deg,{a},{d});--ac:{a};--dk:{d};--hl:{hl}">'
            f'<div class="logo"><img src="{LOGO.as_uri()}"></div><div class="w"><h1>{st["titolo"]}</h1>'
            f'<div class="media">{media}</div>{box}{stick}<div class="foot">{piede}</div></div></body></html>')

# ---------------------------------------------------------------- resa in immagini
JS_FIT = """() => {
  const out = [];
  document.querySelectorAll('.fitbox').forEach(b => {
    const z = b.querySelector('.zz'); const mn = parseFloat(b.dataset.min), mx = parseFloat(b.dataset.max);
    const cov = b.classList.contains('cvtxt');
    let k = mx, ok = false;
    for (; k >= mn - 0.001; k -= 0.02) {
      z.style.zoom = k;
      if (cov) { if (b.scrollHeight <= b.clientHeight + 1 && b.scrollWidth <= b.clientWidth + 1) { ok = true; break; } }
      else { z.style.height = (b.clientHeight / k) + 'px'; if (z.scrollHeight <= z.clientHeight + 1 && z.scrollWidth <= z.clientWidth + 1) { ok = true; break; } }
    }
    out.push([ok, Math.round(k * 100) / 100]);
  });
  return out;
}"""

JS_STORIA = """() => {
  const w = document.querySelector('.w'), m = document.querySelector('.media'), e = document.querySelector('.emo');
  const mh = m.getBoundingClientRect().height;
  if (e) e.style.fontSize = Math.max(120, Math.min(260, mh * 0.7)) + 'px';
  return [w.scrollHeight <= w.clientHeight + 1, Math.round(mh)];
}"""

def rendi(lavori):
    """lavori: lista di dict {kind:'post'|'storia', html, out:[percorsi jpg]}. Ritorna, per ogni lavoro, la lista dei problemi."""
    from playwright.sync_api import sync_playwright
    from PIL import Image
    TMP.mkdir(exist_ok=True)
    esiti = []
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        pp = b.new_page(viewport={"width": 1080, "height": 1350})
        ps = b.new_page(viewport={"width": 1080, "height": 1920})
        for i, L in enumerate(lavori):
            f = TMP / f"p{i}.html"; f.write_text(L["html"], encoding="utf-8")
            prob = []
            if L["kind"] == "post":
                pp.goto(f.as_uri()); pp.wait_for_timeout(500)
                fits = pp.evaluate(JS_FIT)
                for n, (ok, k) in enumerate(fits):
                    if not ok:
                        prob.append(f"slide {n+1}: troppo testo, non entra nemmeno rimpicciolito. Accorcia.")
                    elif k < 0.86:
                        prob.append(f"AVVISO slide {n+1}: testo molto fitto (scala {k}). Meglio accorciare.")
                els = pp.locator(".s")
                for n, out in enumerate(L["out"]):
                    png = TMP / "s.png"; els.nth(n).screenshot(path=str(png))
                    Image.open(png).convert("RGB").save(out, quality=92)
            else:
                ps.goto(f.as_uri()); ps.wait_for_timeout(400)
                ok, mh = ps.evaluate(JS_STORIA)
                if not ok or mh < 230:
                    prob.append("storia: troppo testo (lo spazio per foto/emoji è troppo piccolo). Accorcia titolo o riquadro.")
                png = TMP / "s.png"; ps.screenshot(path=str(png))
                Image.open(png).convert("RGB").save(L["out"][0], quality=92)
            esiti.append(prob)
        b.close()
    return esiti

# ---------------------------------------------------------------- controlli sui testi (filtro di conformità)
PRODUTTORI = ["yara", "prayon", "aifar", "corteva", "biogard", "syngenta", "bayer", "basf", "upl", "compo expert", "compo",
              "atlantica", "atlántica", "rovensa", "sumitomo", "certis", "gowan", "adama", "fmc", "sipcam", "koppert", "cbc",
              "shin-etsu", "hortipray", "serbios", "ccs aosta", "novozymes", "novonesis", "l. gobbi", "gobbi", "cifo", "biolchim",
              "valagro", "haifa", "sqm", "icl", "timac", "isagro", "nufarm", "belchim", "ascenza", "chimiberg", "diachem"]
ASSOLUTE = ["elimina", "elimini", "eliminazione", "100%", "senza rischi", "senza rischio", "garantito", "garantita", "garanzia",
            "definitivo", "definitiva", "innocuo", "non tossico", "ecologico", "miracoloso", "miracolo", "infallibile", "totale",
            "per sempre", "zero residui", "zero rischi", "il migliore", "la migliore", "imbattibile", "sicuro al 100"]
PREZZI = ["€", "euro", "sconto", "offerta", "promo", "prezzo", "gratis", "omaggio", "saldi"]
PAROLE_NO = {"galle": "scrivi 'nematodi', non 'galle'", "galla": "scrivi 'nematodi', non 'galle'", "bolle": "scrivi 'documenti di trasporto', non 'bolle'",
             "bolla": "scrivi 'documenti di trasporto', non 'bolle'"}
BANALI = ["agita prima dell'uso", "agitare prima dell'uso", "agita bene", "conserva tra", "conservare tra", "si conserva tra", "tieni lontano dai bambini",
          "usa i guanti", "occhiali e guanti", "leggi l'etichetta", "non superare la dose", "evita i ristagni"]
RE_DOSE = re.compile(r"\d[\d.,]*(?:\s*[–-]\s*\d[\d.,]*)?\s*(?:ml|cc|l|g|kg)\s*/\s*(?:hl|ha)\b", re.I)

def _norm_dose(s):
    return re.sub(r"\s+", "", s.lower()).replace("-", "–")

def testo_piatto(x):
    """Tutto il testo di una struttura (slide, storia, didascalia) senza tag HTML."""
    if isinstance(x, str):
        return re.sub(r"<[^>]+>", " ", x)
    if isinstance(x, dict):
        return " ".join(testo_piatto(v) for k, v in x.items() if k not in ("foto", "colore", "tipo", "emoji"))
    if isinstance(x, (list, tuple)):
        return " ".join(testo_piatto(v) for v in x)
    return ""

def _parola(p, low):
    return re.search(r"(?<![a-zà-ù])" + re.escape(p) + r"(?![a-zà-ù])", low) is not None

def controlla_testi(u, prodotti):
    """Ritorna (errori, avvisi) per un'uscita della specifica."""
    err, avv = [], []
    tipo = u["tipo"]
    tutto = testo_piatto({k: v for k, v in u.items() if k in ("slide", "storia", "didascalia", "titolo", "etichetta", "grande", "piccolo")})
    low = tutto.lower()
    nomi_prod = " ".join(prodotti[p]["nome"].lower() for p in prodotti)
    for p in PRODUTTORI:
        if _parola(p, low) and not _parola(p, nomi_prod):
            err.append(f"nome di produttore nel testo: '{p}' (regola: mai citare i produttori)")
    for p in ASSOLUTE:
        if _parola(p, low):
            err.append(f"linguaggio assoluto vietato: '{p}'")
    for p in PREZZI:
        if _parola(p, low):
            err.append(f"prezzi/promozioni vietati senza ok scritto di Valerio: '{p}'")
    for p, msg in PAROLE_NO.items():
        if _parola(p, low):
            err.append(msg)
    for p in BANALI:
        if p in low:
            err.append(f"consiglio banale da togliere: '{p}' (Valerio vuole solo cose utili all'agricoltore)")
    # dosi: solo quelle registrate in kit/prodotti.json per i prodotti dichiarati
    ammesse = set()
    for p in u.get("prodotti", []):
        if p not in prodotti:
            err.append(f"prodotto '{p}' non presente in kit/prodotti.json")
            continue
        ammesse |= {_norm_dose(d) for d in prodotti[p].get("dosi", [])}
    for d in RE_DOSE.findall(tutto):
        if _norm_dose(d) not in ammesse:
            err.append(f"dose '{d.strip()}' non presente in kit/prodotti.json per i prodotti dichiarati {u.get('prodotti', [])}: "
                       f"usa solo dosi da etichetta/scheda già registrate, oppure togli la dose")
    if tipo == "carosello":
        if not u.get("slide") or u["slide"][0]["tipo"] != "copertina":
            err.append("la prima slide deve essere una copertina che aggancia (problema dell'agricoltore)")
        if not any(s["tipo"] == "sapevi" for s in u.get("slide", [])):
            err.append("manca la slide 'Lo sapevi?' (obbligatoria in ogni carosello)")
        if not 3 <= len(u.get("slide", [])) <= 8:
            err.append("un carosello ha da 3 a 8 slide")
        if not u.get("storia"):
            err.append("manca la storia di richiamo (direttiva: ogni post ha la sua storia 5 minuti dopo)")
        d = u.get("didascalia", "")
        if len(d) < 250:
            err.append("didascalia troppo corta: deve essere informativa (stile newsletter)")
        if len(d) > 2100:
            err.append("didascalia troppo lunga (limite Instagram 2.200 caratteri con la frase obbligatoria)")
        if d.count("#") > 12:
            avv.append("troppi hashtag (massimo 8–10)")
    for k in ("tema", "dato", "fonte_dato"):
        if tipo in ("carosello", "curiosita", "sondaggio") and not str(u.get(k, "")).strip():
            err.append(f"campo '{k}' mancante: ogni uscita dichiara tema, dato tecnico e da dove viene")
    return err, avv

def didascalia_finale(d):
    d = d.strip()
    if DISC not in d:
        if "#" in d.splitlines()[-1]:
            righe = d.splitlines(); tags = righe.pop()
            d = "\n".join(righe).rstrip() + "\n\n" + DISC + "\n\n" + tags
        else:
            d = d + "\n\n" + DISC
    return d + "\n"

# ---------------------------------------------------------------- registro duplicati
def uscite_registrate():
    """Tutte le uscite note: calendari delle settimane + pubblicazioni a mano."""
    out = []
    for f in sorted((REPO / "settimane").glob("*/calendario.json")):
        for u in json.loads(f.read_text(encoding="utf-8")).get("uscite", []):
            if u.get("tema"):
                out.append({"data": u["data"], "id": f"{f.parent.name}/{u['id']}", "tema": u["tema"], "prodotti": u.get("prodotti", []),
                            "titolo": u.get("titolo", ""), "tipo": u["tipo"]})
    man = REPO / "registro" / "manuali.json"
    if man.exists():
        out += json.loads(man.read_text(encoding="utf-8"))
    return out

def controlla_duplicati(u, settimana, registro, giorni=30):
    err, avv = [], []
    d0 = datetime.date.fromisoformat(u["data"])
    me = f"{settimana}/{u['id']}"
    for r in registro:
        if r["id"] == me or r["id"].startswith(me + "_"):
            continue
        dist = abs((d0 - datetime.date.fromisoformat(r["data"])).days)
        if r["tema"] == u.get("tema") and dist <= giorni and r["tipo"] != "storia_richiamo":
            err.append(f"tema '{u['tema']}' già usato il {r['data']} ({r['titolo']}): bloccato per {giorni} giorni")
        elif u["tipo"] == "carosello" and r["tipo"] == "carosello" and dist <= 10 and u.get("prodotti") and set(u["prodotti"][:1]) & set(r.get("prodotti", [])[:1]):
            avv.append(f"prodotto principale '{u['prodotti'][0]}' già protagonista il {r['data']} ({r['titolo']})")
    return err, avv
