#!/usr/bin/env python3
"""Confronto Fortezza / Vertimec EC (richiesta del 26/11/2026).
Carosello Instagram 1080x1350 + slide TikTok 1080x1920 + video TikTok, nello stile del kit (kit/s4kit.py, non modificato).
Uso: NODE_PATH=$(npm root -g) python3 genera.py
Tutti i dati vengono dalle due etichette ministeriali (Fortezza reg. 15119, valida dal 07/10/2026;
Vertimec EC reg. 8795, valida dal 03/01/2024), lette nel Prontuario del banco il 26/11/2026.

Regole seguite: nessun nome di produttore, nessun giudizio su quale funzioni meglio: solo dati d'etichetta.
Decisioni di Valerio del 26/11: in titolo e testi si scrive "stesso principio attivo" (è scritto così su tutte e due
le etichette); niente "quasi uguali", "uguali" o "molto simili" riferito ai due prodotti (le percentuali differiscono
di qualche centesimo); sul prezzo si dice solo quale costa meno, senza cifre ("meno della metà": a listino nel
Prontuario, export del gestionale del 23/10/2026, vale sia per 1 litro sia per 5 litri).
"Stessa dose" si scrive sempre insieme alle colture a cui si riferisce (pomodoro, peperone, melanzana, cetriolo,
melone): su fragola le dosi delle due etichette sono diverse.
Fonti del "Lo sapevi?" (archivio interno, non vanno nei post):
- IRAC, MoA Classification, ed. 11.5 (febbraio 2026): gruppo 6 = avermectine e milbemicine (abamectina,
  emamectina benzoato, milbemectina); la rotazione si basa solo sul numero di gruppo.
- Villacis-Perez et al. 2023, Evolutionary Applications 16(4):863-879: resistenza all'abamectina in
  Tetranychus urticae, mutazioni G314D (GluCl1) e G326E (GluCl3) e detossificazione (P450).
- 60 ml/hl x 18 g/l = 1,08 g di abamectina in 100 litri (conto dall'etichetta).
"""
import json, re, subprocess, sys
from pathlib import Path
from PIL import Image, ImageFilter, ImageEnhance

QUI = Path(__file__).resolve().parent
REPO = QUI.parent.parent
sys.path.insert(0, str(REPO / "kit"))
import s4kit as k

ID = "confronto"
COLORE = "petrolio"
F, V = "Fortezza", "Vertimec EC"

# ---------------------------------------------------------------- contenuti
COPERTINA = {
    "tag": "Abamectina a confronto",
    "titolo": "Stesso principio attivo.<br><em>Prezzo diverso.</em>",
    "sotto": "Fortezza e<br>Vertimec&nbsp;EC:<br><span>abamectina 18&nbsp;g/l</span><br>contro ragnetto rosso, tripidi e minatrici in&nbsp;serra.",
    "box": "Stessa dose sulle orticole in comune. E uno costa meno della metà. Scorri.",
}

UGUALI = {
    "tag": "Cosa hanno in comune",
    "titolo": "Stesso principio attivo,<br><em>stessa dose.</em>",
    "voci": [("Principio attivo", "Abamectina"), ("Concentrazione", "18 g/l"),
             ("Formulazione (EC)", "Emulsionabile"), ("Gruppo IRAC", "6 · avermectine")],
    "dose_su": "Dose sulle orticole in comune",
    "colture": "Pomodoro, peperone, melanzana, cetriolo, melone",
    "dosi": [("60 ml/hl", "Ragnetto rosso ed eriofide"), ("75 ml/hl", "Larve di tripide"),
             ("60 ml/hl", "Minatrici, 2 volte ogni 7–10 giorni")],
    "punti": ["Sulle orticole solo in serre permanenti", "Azione lenta: massimo effetto in 3–5 giorni"],
    "fonte": "Da etichetta.",
}

NO = '<span class="no">no nov–feb</span>'
X = '<span class="xx">✕ non in etichetta</span>'
TABELLA = {
    "tag": "Dove cambiano",
    "titolo": "Cambia l'etichetta,<br><em>coltura per coltura.</em>",
    "intesta": "Giorni di carenza",
    "righe": [
        ("Pomodoro", "<b>7 giorni</b>", "<b>7 giorni</b>"),
        ("Melanzana", "<b>7 giorni</b>", "<b>3 giorni</b>"),
        ("Peperone", "<b>3 giorni</b>", f"<b>3 giorni</b>{NO}"),
        ("Cetriolo, melone", "<b>3 giorni</b>", f"<b>3 giorni</b>{NO}"),
        ("Zucchino, cocomero, zucca", X, f"<b>3 giorni</b>{NO}"),
        ("Fragola", "<b>7 giorni</b>", f"<b>3 giorni</b>{NO}"),
        ("Lattughe,<br>baby leaf", X, f"<b>14 giorni</b>{NO}"),
    ],
    "nota": "<b>No nov–feb</b>: l'etichetta non lo ammette da novembre a febbraio. Su fragola cambia anche la dose.",
    "fonte": "Da etichetta.",
}

PRATICA = {
    "tag": "In pratica",
    "titolo": "Tre cose da sapere<br><em>prima di scegliere.</em>",
    "voci": [
        ["🐝", "Bombi in serra",
         f"<b>{F}:</b> colonie chiuse e coperte durante il trattamento, serra chiusa 24 ore.<br><b>{V}:</b> 4 giorni prima di farli rientrare."],
        ["🔁", "Quanti trattamenti",
         f"<b>{F}:</b> consigliati non più di 2 per ciclo.<br><b>{V}:</b> al massimo 2 l'anno su pomodoro, peperone, cetriolo e zucchino; 3 su melanzana, melone, cocomero e zucca."],
    ],
    "prezzo": ["🏷️", f"{F} costa meno della metà",
               "Al nostro banco, a parità di confezione. Dove dose e carenza coincidono, come sul pomodoro, è il prezzo a fare la differenza."],
    "chiusa": "Vale sempre l'etichetta della confezione che usi.",
    "fonte": "Da etichetta.",
}

SAPEVI = {
    "tipo": "sapevi", "tag": "Lo sapevi?",
    "titolo": "Cambiare marca non è ruotare.",
    "grande": "Se il ragnetto non risponde più a uno, non risponde nemmeno all'altro.",
    "piccolo": "Stessa molecola, stesso bersaglio: la rotazione si fa cambiando numero di gruppo IRAC, non nome sulla confezione.",
    "punti": [
        "Anche emamectina (Affirm) e milbemectina (Milbeknock) sono gruppo 6: alternarle all'abamectina non è cambiare gruppo",
        "Nel ragnetto rosso la resistenza all'abamectina è legata a mutazioni del bersaglio (come G314D e G326E) e a enzimi che la degradano",
        "A 60 ml/hl, in 100 litri d'acqua c'è circa 1 grammo di abamectina: per questo contano bagnatura e dose per ettaro",
    ],
    "chiusa": "Passa al banco di Studio 4: ti diciamo quale dei due va sulla tua coltura.",
    "fonte": "Etichette e letteratura scientifica.",
}

DIDASCALIA = f"""{F} e {V}: stesso principio attivo, prezzo diverso 🕷️
Tutti e due sono a base di abamectina a 18 g/l (IRAC 6), concentrato emulsionabile, e sulle orticole si usano solo in serre permanenti. Su pomodoro, peperone, melanzana, cetriolo e melone la dose è la stessa: 60 ml/hl contro ragnetto rosso ed eriofide, 75 ml/hl sulle larve di tripide, 60 ml/hl sulle minatrici in 2 applicazioni ogni 7–10 giorni.

⚠️ Quello che cambia è l'etichetta. Zucchino, cocomero, zucca e lattughe sono solo su {V}. Su melanzana e fragola la carenza è 7 giorni con {F} e 3 con {V}. Da novembre a febbraio l'etichetta di {V} non lo ammette su peperone, cucurbitacee, fragola e lattughe; quella di {F} non ha questo limite. Cambiano anche le regole per i bombi.

💡 Lo sapevi? Passare dall'uno all'altro non è una rotazione: stessa molecola, stesso gruppo 6, come emamectina e milbemectina. Se il ragnetto non risponde più all'abamectina, cambiare marca non serve: serve cambiare gruppo.

Sul pomodoro dose e carenza coincidono: lì la differenza la fa soprattutto il prezzo. Al nostro banco, a parità di confezione, {F} costa meno della metà di {V}. Salva la tabella e passa al banco di Studio 4, a Vittoria: ti diciamo quale conviene sulla tua coltura 👇

{k.DISC}

#studio4srl #ragnettorosso #abamectina #serra #agricoltura
"""

# ---------------------------------------------------------------- stile in più (solo per le tre slide su misura)
CSS_EXTRA = """
.c2{position:absolute;left:80px;right:80px;top:140px;bottom:70px;display:flex;flex-direction:column;gap:26px}
.c2 h1{font-size:82px}
.c2mid{flex:1;min-height:0;display:flex;gap:28px}
.c2txt{flex:1;min-width:0;display:flex;flex-direction:column;justify-content:center}
.c2txt .cvsub{font-size:42px}
.c2duo{flex:none;display:flex;gap:22px;height:100%}
.c2duo figure{height:100%;display:flex;flex-direction:column;align-items:center;justify-content:flex-end;gap:14px}
.c2duo img{height:calc(100% - 50px)}
.c2duo figcaption{font-size:27px;font-weight:700;line-height:1.3;color:var(--dark)}
.g2{display:grid;grid-template-columns:1fr 1fr;gap:16px}
.kv{padding:18px 28px;border-radius:26px}
.kv .kk{font-size:21px;font-weight:700;letter-spacing:2px;text-transform:uppercase;color:var(--acc)}
.kv .vv{font-size:38px;font-weight:700;line-height:1.15;margin-top:2px}
.db{padding:26px 32px;border-radius:32px}
.db .lab{font-size:21px;font-weight:700;letter-spacing:2px;opacity:.78;text-transform:uppercase;line-height:1.3}
.db .clt{font-size:25px;font-weight:600;line-height:1.25;margin-top:2px}
.d3{display:grid;grid-template-columns:1fr 1fr 1fr;margin-top:16px}
.d3 .dv{font-size:48px;font-weight:700;line-height:1.05;white-space:nowrap}
.d3 .dn{font-size:24px;font-weight:500;opacity:.88;line-height:1.25;margin-top:6px}
.d3>div+div{border-left:2px solid rgba(255,255,255,.22);padding-left:18px}
.tb{display:flex;flex-direction:column;gap:10px}
.tr{display:grid;grid-template-columns:276px 1fr 1fr;gap:10px}
.tr>div{background:#fff;border-radius:20px;padding:10px 16px;display:flex;align-items:center;gap:6px 10px;flex-wrap:wrap;
 box-shadow:0 8px 22px rgba(0,0,0,.07);min-height:76px}
.tr>div.cl{background:var(--dark);color:#fff;font-size:26px;font-weight:700;line-height:1.14}
.tr b{font-size:29px;font-weight:700;white-space:nowrap}
.th>div{background:none;box-shadow:none;padding:0 6px;min-height:0;align-items:flex-end}
.th .ph{justify-content:center;gap:14px;flex-wrap:nowrap}
.th .ph img{height:178px}
.th .pn{font-size:29px;font-weight:700;line-height:1.1;padding-bottom:8px}
.th .ih{font-size:21px;font-weight:700;letter-spacing:2px;text-transform:uppercase;color:var(--acc);padding-bottom:10px;line-height:1.25}
.no{font-size:19px;font-weight:700;color:#A3241B;background:#FCE4E0;border-radius:999px;padding:3px 10px;white-space:nowrap}
.xx{font-size:23px;font-weight:600;color:#70757D;white-space:nowrap}
.tnota{font-size:23px;font-weight:500;line-height:1.3;padding:2px 6px;opacity:.9}
.tnota b{font-weight:700;color:#A3241B}
.card b{font-weight:700}
"""

def sl_uguali(s):
    voci = "".join(f'<div class="card kv"><div class="kk">{a}</div><div class="vv">{b}</div></div>' for a, b in s["voci"])
    dosi = "".join(f'<div><div class="dv">{a}</div><div class="dn">{b}</div></div>' for a, b in s["dosi"])
    return (f'<h2>{s["titolo"]}</h2><div class="g2">{voci}</div>'
            f'<div class="card scuro db"><div class="lab">{s["dose_su"]}</div><div class="clt">{s["colture"]}</div>'
            f'<div class="d3">{dosi}</div></div>'
            + k._punti(s["punti"], 30))

def sl_pratica(s):
    e, a, b = s["prezzo"]
    prezzo = (f'<div class="card scuro" style="display:flex;gap:22px;align-items:flex-start;border-radius:32px;padding:26px 32px">'
              f'<span style="font-size:40px;line-height:1.1">{e}</span>'
              f'<div><div style="font-size:21px;font-weight:700;letter-spacing:2px;opacity:.78;text-transform:uppercase">Prezzo</div>'
              f'<div style="font-size:36px;font-weight:700;line-height:1.18;margin-top:2px">{a}</div>'
              f'<div style="font-size:27px;font-weight:500;line-height:1.32;margin-top:8px;opacity:.9">{b}</div></div></div>')
    return k.sl_schede({"titolo": s["titolo"], "voci": s["voci"]}) + prezzo + k._chiusa(s["chiusa"])

def sl_tabella(s):
    testa = (f'<div class="tr th"><div class="ih">{s["intesta"]}</div>'
             f'<div class="ph"><img class="sh" src="{k._foto("fortezza")}"><span class="pn">{F}</span></div>'
             f'<div class="ph"><img class="sh" src="{k._foto("vertimec")}"><span class="pn">{V}</span></div></div>')
    righe = "".join(f'<div class="tr"><div class="cl">{a}</div><div>{b}</div><div>{c}</div></div>' for a, b, c in s["righe"])
    return f'<h2>{s["titolo"]}</h2><div class="tb">{testa}{righe}</div><div class="tnota">{s["nota"]}</div>'

def html():
    slide = [("copertina2", COPERTINA), ("uguali", UGUALI), ("tabella", TABELLA), ("pratica", PRATICA), ("kit", SAPEVI)]
    T = len(slide); out = []
    for i, (tipo, s) in enumerate(slide):
        head = f'<img class="logo" src="{k.LOGO.as_uri()}"><div class="num">{i+1}/{T}</div>'
        apri = f'<div class="s" style="{k._vars(COLORE)}"><div class="tag"><span class="dot"></span>{s["tag"]}</div>{head}'
        if tipo == "copertina2":
            out.append(
                f'{apri}<div class="c2"><h1>{s["titolo"]}</h1><div class="c2mid">'
                f'<div class="c2txt"><div class="cvsub">{s["sotto"]}</div></div>'
                f'<div class="c2duo"><figure><img class="sh" src="{k._foto("fortezza")}"><figcaption>{F}</figcaption></figure>'
                f'<figure><img class="sh" src="{k._foto("vertimec")}"><figcaption>{V}</figcaption></figure></div></div>'
                f'<div class="cvbox scuro">{s["box"]}</div><div class="swipe">scorri →</div></div></div>')
            continue
        corpo = {"uguali": sl_uguali, "tabella": sl_tabella, "pratica": sl_pratica}[tipo](s) if tipo != "kit" else k.SLIDE[s["tipo"]](s)
        out.append(
            f'{apri}<div class="col"><div class="fit fitbox" data-min="0.78" data-max="1.22"><div class="zz">{corpo}</div></div>'
            f'<div class="disc">{s["fonte"]} {k.DISC}</div></div></div>')
    # in coda: la copertina senza la seconda riga del titolo, usata solo come primo secondo del video
    out.append(out[0].replace("<em>", '<em style="visibility:hidden">', 1))
    return (f"<!DOCTYPE html><html><head><meta charset='utf-8'><style>{k.CSS_POST}{CSS_EXTRA}</style></head>"
            f"<body>{''.join(out)}</body></html>"), T

# ---------------------------------------------------------------- controlli sui testi (stesse liste del kit)
def controlli():
    prodotti = json.loads((REPO / "kit" / "prodotti.json").read_text(encoding="utf-8"))
    tutto = k.testo_piatto([COPERTINA, UGUALI, TABELLA, PRATICA, SAPEVI, DIDASCALIA])
    low = tutto.lower(); esito = []
    nomi = " ".join(prodotti[p]["nome"].lower() for p in prodotti)
    for p in k.PRODUTTORI:
        if k._parola(p, low) and not k._parola(p, nomi):
            esito.append(f"ERRORE produttore: {p}")
    for p in k.ASSOLUTE:
        if k._parola(p, low):
            esito.append(f"ERRORE linguaggio assoluto: {p}")
    for p in k.PREZZI:
        if k._parola(p, low):
            esito.append(f"nota: parola '{p}' (qui voluta: Valerio ha chiesto di dire che il prezzo è diverso e quale costa meno, senza cifre)")
    for p, msg in k.PAROLE_NO.items():
        if k._parola(p, low):
            esito.append("ERRORE " + msg)
    for p in k.BANALI:
        if p in low:
            esito.append(f"ERRORE consiglio banale: {p}")
    ammesse = {k._norm_dose(d) for p in ("fortezza", "vertimec") for d in prodotti[p]["dosi"]}
    for d in k.RE_DOSE.findall(tutto):
        if k._norm_dose(d) not in ammesse:
            esito.append(f"ERRORE dose non registrata in kit/prodotti.json: {d.strip()}")
    if re.search(r"\d\s*(€|euro)", low):
        esito.append("ERRORE cifra di prezzo nel testo")
    return esito

# ---------------------------------------------------------------- resa
def nove_sedicesimi(src, dst, fondo=None):
    """Slide del kit 1080x1350 su fondo sfocato della stessa slide (1080x1920), come gli altri video prodotto."""
    s = Image.open(src).convert("RGB")
    f = Image.open(fondo).convert("RGB") if fondo else s
    bg = f.resize((1536, 1920)).crop((228, 0, 1308, 1920)).filter(ImageFilter.GaussianBlur(40))
    bg = ImageEnhance.Brightness(bg).enhance(1.04)
    bg.paste(s, (0, 285)); bg.save(dst)

# video: apertura con la prima riga del titolo da sola, poi compare "Prezzo diverso."; le altre slide scorrono a sinistra.
# (durata in secondi, passaggio verso questa slide, durata del passaggio)
APERTURA = 1.1
SCENE = [(3.3, "fade", 0.25), (5.8, "slideleft", 0.4), (7.5, "slideleft", 0.4), (6.8, "slideleft", 0.4), (7.0, "slideleft", 0.4)]

def video(apertura, pngs, out):
    clip = [(apertura, APERTURA, None, 0)] + [(p, d, t, x) for p, (d, t, x) in zip(pngs, SCENE)]
    inp, filt = [], ""
    for i, (p, d, _, _) in enumerate(clip):
        inp += ["-loop", "1", "-t", str(d), "-framerate", "30", "-i", str(p)]
        filt += f"[{i}:v]scale=1080:1920,format=yuv420p,setsar=1[v{i}];"
    prev, acc = "v0", clip[0][1]
    for i in range(1, len(clip)):
        _, d, t, x = clip[i]
        o = round(acc - x, 3)
        filt += f"[{prev}][v{i}]xfade=transition={t}:duration={x}:offset={o}[x{i}];"
        prev = f"x{i}"; acc = o + d
    n = len(clip)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *inp, "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
                    "-filter_complex", filt.rstrip(";"), "-map", f"[{prev}]", "-map", f"{n}:a", "-shortest",
                    "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-r", "30", "-pix_fmt", "yuv420p",
                    "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", str(out)], check=True)

def main():
    for r in controlli():
        print(r)
    IG = QUI / "instagram"; TK = QUI / "tiktok_slide"; tmp = QUI / ".tmp"
    for d in (IG, TK, tmp):
        d.mkdir(exist_ok=True)
    h, T = html()
    f = QUI / f".{ID}.html"; f.write_text(h, encoding="utf-8")
    jsf = QUI / ".js_fit.txt"; jsf.write_text(k.JS_FIT)
    r = subprocess.run(["node", str(QUI / "rendi_kit.js"), str(f), str(jsf), str(tmp)], capture_output=True, text=True)
    print("resa:", r.stdout.strip() or "ok", r.stderr.strip()[-400:])
    pngs = []
    apertura = tmp / "apertura.png"
    nove_sedicesimi(tmp / f"k{T+1}.png", apertura, fondo=tmp / "k1.png"); (tmp / f"k{T+1}.png").unlink()
    for i in range(T):
        kp = tmp / f"k{i+1}.png"
        Image.open(kp).convert("RGB").save(IG / f"{ID}_s{i+1}.jpg", quality=92)
        nove_sedicesimi(kp, TK / f"{ID}_s{i+1}.png"); pngs.append(TK / f"{ID}_s{i+1}.png"); kp.unlink()
    (QUI / f"{ID}_didascalia.txt").write_text(DIDASCALIA, encoding="utf-8")
    if "--senza-video" not in sys.argv:
        video(apertura, pngs, QUI / f"{ID}_fortezza_vertimec_tiktok.mp4")
    apertura.unlink(); f.unlink(); jsf.unlink(); tmp.rmdir()
    print("fatto")

if __name__ == "__main__":
    main()
