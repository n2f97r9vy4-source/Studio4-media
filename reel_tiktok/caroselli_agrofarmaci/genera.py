#!/usr/bin/env python3
"""Caroselli TikTok (foto 9:16, 1080x1920) per Topas 10 EC, Oikos e Pergado SC — 23/11/2026.
Stile: kit Studio 4 (Poppins, verde #1B9A4B / scuro #0E3B22, arancio #DF502E, logo ufficiale, foto reali scontornate).
Dati SOLO da etichetta/catalogo del Ministero (nessuna dose). Le ipotesi sono segnate in LEGGIMI.md.
Uso: python3 genera.py && node rendi.js out/<prodotto>
"""
import json, subprocess
from pathlib import Path

QUI = Path(__file__).resolve().parent
REPO = QUI.parent.parent
KIT = REPO / "kit"
LOGO = (KIT / "assets" / "logo_s4.png").as_uri()
DISC = ("Usare i prodotti fitosanitari con precauzione. Prima dell'uso leggere sempre l'etichetta "
        "e le informazioni sul prodotto. Vendita ai possessori di patentino.")

FONT = "".join(
    f"@font-face{{font-family:P;src:url({(KIT/'fonts'/f).as_uri()});font-weight:{w}}}"
    for f, w in [("Poppins-Regular.ttf", 400), ("Poppins-Medium.ttf", 500), ("Poppins-Bold.ttf", 700)])

CSS = FONT + """
*{margin:0;box-sizing:border-box}
body{width:1080px;height:1920px;overflow:hidden;font-family:P,'Noto Color Emoji',sans-serif;color:#0E3B22;
 background:linear-gradient(170deg,#F2F8F3 0%,#E3F1E7 55%,#D6EBDC 100%);position:relative}
:root{--v:#1B9A4B;--s:#0E3B22;--o:#DF502E}
.head{position:absolute;left:64px;top:64px;display:flex;align-items:center;gap:22px}
.pill{background:#fff;border-radius:22px;padding:12px 18px;line-height:0;box-shadow:0 8px 24px rgba(0,0,0,.08)}
.pill img{width:220px}
.user{font-size:30px;font-weight:700;color:var(--s)}
.num{position:absolute;right:64px;top:84px;font-size:28px;font-weight:700;color:var(--s);opacity:.45}
/* zona sicura TikTok: niente testo sotto 1560 px e a destra oltre 930 px nelle righe basse */
.safe{position:absolute;left:64px;right:64px;top:230px;bottom:360px;display:flex;flex-direction:column;gap:30px;overflow:hidden}
.kick{font-size:30px;font-weight:700;color:var(--o);letter-spacing:2px;text-transform:uppercase}
h1{font-size:104px;line-height:1.02;font-weight:700;letter-spacing:-3px}
h2{font-size:74px;line-height:1.05;font-weight:700;letter-spacing:-2px}
em{font-style:normal;color:var(--o)}
.sub{font-size:40px;font-weight:500;line-height:1.3}
.sub b{color:var(--v)}
.box{background:var(--s);color:#fff;border-radius:36px;padding:34px 40px;font-size:38px;font-weight:500;line-height:1.3}
.box b{color:#9EE6B5}
.card{background:#fff;border-radius:30px;padding:26px 32px;box-shadow:0 14px 40px rgba(0,0,0,.08);display:flex;gap:24px;align-items:flex-start}
.card .e{font-size:50px;line-height:1.1;flex:none}
.card .t{font-size:42px;font-weight:700;line-height:1.15}
.card .d{font-size:34px;font-weight:500;line-height:1.3;margin-top:6px;opacity:.88}
.n{flex:none;width:64px;height:64px;border-radius:50%;background:var(--v);color:#fff;font-size:34px;font-weight:700;display:flex;align-items:center;justify-content:center}
.foto{flex:1;min-height:0;display:flex;justify-content:center;align-items:center}
.foto img{max-height:100%;max-width:100%;filter:drop-shadow(0 30px 34px rgba(0,0,0,.30))}
.swipe{font-size:34px;font-weight:700;color:var(--v)}
.row{display:flex;gap:30px;flex:1;min-height:0}
.tab{background:#fff;border-radius:34px;box-shadow:0 14px 40px rgba(0,0,0,.08);padding:14px 34px;flex:1;align-self:center}
.safe.mid{justify-content:center}
.tab div{padding:20px 0;border-top:2px solid rgba(14,59,34,.08)}
.tab div:first-child{border-top:0}
.tab small{display:block;font-size:24px;font-weight:700;letter-spacing:2px;text-transform:uppercase;color:var(--v)}
.tab span{display:block;font-size:40px;font-weight:700;line-height:1.2;margin-top:4px}
.chips{display:flex;flex-wrap:wrap;gap:18px}
.chip{background:#fff;border-radius:999px;padding:22px 38px;font-size:42px;font-weight:700;box-shadow:0 8px 22px rgba(0,0,0,.07)}
.chip.o{background:var(--o);color:#fff}
.nota{font-size:34px;font-weight:600;line-height:1.35;color:var(--s);opacity:.85}
.disc{position:absolute;left:64px;right:180px;bottom:300px;font-size:22px;line-height:1.4;font-weight:500;opacity:.7}
"""


def pagina(corpo, n, T, disc=False, mid=False):
    return (f"<!DOCTYPE html><html><head><meta charset='utf-8'><style>{CSS}</style></head><body>"
            f"<div class='head'><div class='pill'><img src='{LOGO}'></div><div class='user'>@studio4srl</div></div>"
            f"<div class='num'>{n}/{T}</div><div class='safe{" mid" if mid else ""}'>{corpo}</div>"
            + (f"<div class='disc'>{DISC}</div>" if disc else "") + "</body></html>")


def foto(nome):
    return (KIT / "assets" / "foto" / f"{nome}.png").as_uri()


# ------------------------------------------------------------------ tipi di slide
def s_hook(s):
    return (f"<div class='kick'>{s['kick']}</div><h1>{s['titolo']}</h1><div class='sub'>{s['sotto']}</div>"
            f"<div class='foto'><img src='{foto(s['foto'])}'></div><div class='swipe'>{s.get('swipe', 'scorri →')}</div>")

def s_schede(s):
    c = "".join(f"<div class='card'><div class='e'>{e}</div><div><div class='t'>{t}</div><div class='d'>{d}</div></div></div>"
                for e, t, d in s["voci"])
    return f"<div class='kick'>{s['kick']}</div><h2>{s['titolo']}</h2>{c}" + (f"<div class='nota'>{s['nota']}</div>" if s.get("nota") else "")

def s_carta(s):
    righe = "".join(f"<div><small>{a}</small><span>{b}</span></div>" for a, b in s["righe"])
    return (f"<div class='kick'>{s['kick']}</div><h2>{s['titolo']}</h2>"
            f"<div class='row'><div class='foto' style='flex:none;width:440px'><img src='{foto(s['foto'])}'></div>"
            f"<div class='tab'>{righe}</div></div>")

def s_sapevi(s):
    pts = "".join(f"<div class='card' style='align-items:center'><div class='n'>{i+1}</div><div class='d' style='font-size:34px;font-weight:600;opacity:1;margin:0'>{p}</div></div>"
                  for i, p in enumerate(s.get("punti", [])))
    return (f"<div class='kick'>Lo sapevi? 💡</div><h2>{s['titolo']}</h2><div class='box'>{s['box']}</div>{pts}"
            + (f"<div class='nota' style='color:var(--o);opacity:1;font-weight:700'>{s['chiusa']}</div>" if s.get("chiusa") else ""))

def s_chips(s):
    ch = "".join(f"<div class='chip{' o' if i in s.get('evidenza', []) else ''}'>{c}</div>" for i, c in enumerate(s["chips"]))
    extra = "".join(f"<div class='card'><div class='e'>{e}</div><div><div class='t'>{t}</div><div class='d'>{d}</div></div></div>" for e, t, d in s.get("voci", []))
    return f"<div class='kick'>{s['kick']}</div><h2>{s['titolo']}</h2><div class='chips'>{ch}</div>{extra}<div class='nota'>{s['nota']}</div>"

def s_passi(s):
    pts = "".join(f"<div class='card' style='align-items:center'><div class='n'>{i+1}</div><div><div class='t' style='font-size:36px'>{a}</div><div class='d'>{b}</div></div></div>"
                  for i, (a, b) in enumerate(s["passi"]))
    return f"<div class='kick'>{s['kick']}</div><h2>{s['titolo']}</h2>{pts}" + (f"<div class='nota'>{s['nota']}</div>" if s.get("nota") else "")

def s_fine(s):
    return (f"<h2 style='font-size:84px'>{s['titolo']}</h2><div class='sub'>{s['sotto']}</div>"
            f"<div class='box'>{s['box']}</div><div class='foto' style='max-height:520px'><img src='{foto(s['foto'])}'></div>")

TIPI = {"hook": s_hook, "schede": s_schede, "carta": s_carta, "sapevi": s_sapevi, "chips": s_chips, "passi": s_passi, "fine": s_fine}


def main():
    spec = json.loads((QUI / "caroselli.json").read_text(encoding="utf-8"))
    for c in spec:
        out = QUI / c["id"]; out.mkdir(exist_ok=True)
        for f in out.glob("s*.*"): f.unlink()
        T = len(c["slide"])
        for i, s in enumerate(c["slide"]):
            html = pagina(TIPI[s["tipo"]](s), i + 1, T, disc=s.get("disc", False), mid=s["tipo"] not in ("hook",))
            (out / f"s{i+1}.html").write_text(html, encoding="utf-8")
        (QUI / f"{c['id']}_didascalia.txt").write_text(c["didascalia"] + "\n", encoding="utf-8")
        r = subprocess.run(["node", str(QUI / "rendi.js"), str(out)], capture_output=True, text=True)
        print(c["id"], r.stdout.strip(), r.stderr.strip()[-400:])
        for f in out.glob("*.html"): f.unlink()


if __name__ == "__main__":
    main()
