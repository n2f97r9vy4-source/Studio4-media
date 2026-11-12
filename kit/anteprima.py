#!/usr/bin/env python3
"""Crea la pagina di anteprima di una settimana (per Valerio) e un foglio per giorno.
Uso: python3 kit/anteprima.py 2026-11-16 /percorso/cartella_uscita
Produce index.html + img/ (da pubblicare come pagina) e giorno_<data>.jpg (da inviare se la pagina non si può pubblicare).
"""
import sys, json, html, shutil, datetime
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import s4kit as K
from PIL import Image

NOMI = ["Lunedì", "Martedì", "Mercoledì", "Giovedì", "Venerdì", "Sabato", "Domenica"]

def main():
    lun, out = sys.argv[1], Path(sys.argv[2])
    W = K.REPO / "settimane" / lun
    cal = json.loads((W / "calendario.json").read_text(encoding="utf-8"))
    (out / "img").mkdir(parents=True, exist_ok=True)
    shutil.copy(K.LOGO, out / "img" / "logo.png")
    css = (K.KIT / "anteprima.css").read_text()
    d0 = datetime.date.fromisoformat(lun)
    nav, body, np_, ns = "", "", 0, 0
    for i in range(7):
        d = (d0 + datetime.timedelta(days=i)).isoformat()
        du = [u for u in cal["uscite"] if u["data"] == d]
        nav += f'<a href="#d{d[-2:]}">{NOMI[i][:3]} {d[-2:]}</a>'
        body += f'<h2 id="d{d[-2:]}">{NOMI[i]} {int(d[-2:])}</h2>'
        thumbs = []
        for u in du:
            ims = ""
            for f in u["files"]:
                n = Path(f).name; im = Image.open(W / f).convert("RGB"); im.thumbnail((1080, 1920)); im.save(out / "img" / n, quality=80)
                ims += f'<img src="img/{n}" loading="lazy">'
            thumbs.append((u, Image.open(W / u["files"][0]).convert("RGB")))
            st = '<span class="b ok">approvato</span>' if u["approvato"] else '<span class="b no">da approvare</span>'
            if u.get("pubblicato"): st = '<span class="b ok">pubblicato</span>'
            head = f'<div class="hd"><img class="av" src="img/logo.png"><b>studio4.srl</b><span class="t">{"Storia" if u["tipo"] == "storia" else "Post"} · {u["ora"]}</span></div>'
            if u["tipo"] == "storia":
                ns += 1
                kind = "richiamo del post" if u.get("dopo_post") else ("la pubblichi tu, con l'adesivo" if not u.get("automatica", True) else "curiosità")
                extra = (" · risposte: " + " / ".join(u["risposte"])) if u.get("risposte") else ""
                body += f'<div class="card">{head}<div class="st">{ims}</div><div class="cap"><div class="tt">{html.escape(u["titolo"])}</div><span class="b">{kind}{html.escape(extra)}</span>{st}</div></div>'
            else:
                np_ += 1
                cap = (W / u["didascalia"]).read_text(encoding="utf-8")
                body += (f'<div class="card">{head}<div class="car">{ims}</div><div class="n">← scorri · {len(u["files"])} slide</div>'
                         f'<div class="cap"><div class="tt">{html.escape(u["titolo"])}</div>{st}<br><br>{html.escape(cap).replace(chr(10), "<br>")}</div></div>')
        if thumbs:
            h = 480; sheet = Image.new("RGB", (sum(int(t.width * h / t.height) + 10 for _, t in thumbs) + 10, h + 20), "white"); x = 10
            for _, t in thumbs:
                w = int(t.width * h / t.height); sheet.paste(t.resize((w, h)), (x, 10)); x += w + 10
            sheet.save(out / f"giorno_{d}.jpg", quality=85)
    fine = (d0 + datetime.timedelta(days=6))
    titolo = f"Settimana {d0.day}–{fine.day}/{fine.month} – Instagram"
    page = (f'<!DOCTYPE html><html lang="it"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>{titolo}</title><style>{css}</style></head><body><header><h1>{titolo}: {np_} post e {ns} storie</h1><nav>{nav}</nav></header><main>{body}</main></body></html>')
    (out / "index.html").write_text(page, encoding="utf-8")
    print(f"{np_} post, {ns} storie → {out}/index.html")

if __name__ == "__main__":
    main()
