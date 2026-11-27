#!/usr/bin/env python3
"""Video TikTok "foto e domanda" (27/11/2026). Richiesta di Valerio: video diversi da quelli a slide, "un nuovo tipo di
video con immagini inerenti al prodotto e quindi più interattive".

Come è fatto (1080x1920, 30 fotogrammi al secondo, circa 24 secondi, senza audio: la musica la mette Valerio dall'app):
  1. aggancio   foto vera a tutto schermo (problema, insetto, coltura) con il titolo che incuriosisce
  2. domanda    la foto si stringe in un riquadro, domanda con due o tre risposte e conto alla rovescia di 3 secondi
  3. risposta   si accende la risposta giusta, con una riga di spiegazione
  4. prodotto   la confezione scontornata entra al centro, nome e tre punti
  5. dose       foto della coltura, dose di etichetta in grande, tre regole d'uso
  6. banco      logo, invito al banco di Vittoria, frase di legge
Stile Studio 4: sfondo chiaro del kit nel colore del prodotto, logo e carattere del kit (kit/s4kit.py, non modificato).

Uso:  NODE_PATH=$(npm root -g) python3 genera_video.py [id ...] [--prova]
  --prova   salva solo 12 fotogrammi di controllo in prova_<id>/ (niente video)
Dati: video_foto.json. Foto: foto_video/ (ogni foto ha autore e licenza in foto_video/CREDITI.md).
"""
import json, re, shutil, subprocess, sys
from pathlib import Path
QUI = Path(__file__).resolve().parent; REPO = QUI.parent.parent
sys.path.insert(0, str(REPO / "kit")); import s4kit as k
FOTO = QUI / "foto_video"
FPS = 30
# inizio di ogni scena, in secondi: Q domanda, C conto alla rovescia, R risposta, P prodotto, D dose, F finale
TEMPI = {"Q": 3.2, "C": 4.3, "R": 7.3, "P": 11.1, "D": 15.3, "F": 20.9, "FINE": 25.0}
FONDO = 1560    # sotto questa quota TikTok mette nome e didascalia: i testi devono finire prima (a destra, oltre x 940, ci sono le icone)

CSS = """
*{box-sizing:border-box;margin:0;padding:0}
html,body{width:1080px;height:1920px;overflow:hidden}
body{font-family:P,'Noto Color Emoji',sans-serif;color:var(--dark);position:relative;background:linear-gradient(160deg,var(--bg1) 0%,var(--bg2) 100%)}
em{font-style:normal;color:var(--acc)}
.blob{position:absolute;border-radius:50%;background:var(--acc)}
.b1{width:900px;height:900px;left:-420px;top:1180px;opacity:.10;animation:drift1 25s ease-in-out 0s infinite alternate}
.b2{width:560px;height:560px;left:800px;top:380px;opacity:.07;animation:drift2 25s ease-in-out 0s infinite alternate}
@keyframes drift1{to{transform:translate(140px,-180px) scale(1.12)}}
@keyframes drift2{to{transform:translate(-110px,160px) scale(.88)}}
@keyframes svanisci{to{opacity:0}}
@keyframes pop{from{transform:scale(0)}to{transform:scale(1)}}
@keyframes suIn{from{transform:translateY(46px);opacity:0}to{transform:none;opacity:1}}
@keyframes daSin{from{transform:translateX(-80px);opacity:0}to{transform:none;opacity:1}}
@keyframes daDes{from{transform:translateX(150px);opacity:0}to{transform:none;opacity:1}}
@keyframes viaSu{to{transform:translateY(-50px);opacity:0}}

/* ---- foto A: a tutto schermo, poi riquadro */
#fa{position:absolute;left:0;top:0;width:1080px;height:1920px;overflow:hidden;z-index:2;box-shadow:0 26px 60px rgba(0,0,0,.24);
 animation:faCard .9s cubic-bezier(.7,0,.2,1) [[Q]] forwards, faVia .55s cubic-bezier(.6,0,.9,.3) [[P-0.45]] forwards}
#fa img,#fb img{width:100%;height:100%;object-fit:cover;display:block}
#fa img{animation:kb [[P]] linear 0s both}
@keyframes kb{from{transform:scale(1.02)}to{transform:scale(1.2)}}
@keyframes faCard{to{left:60px;top:290px;width:960px;height:var(--ch);border-radius:56px}}
@keyframes faVia{to{transform:translateX(-1150px) rotate(-7deg);opacity:0}}
.cred{position:absolute;left:30px;bottom:16px;font-size:20px;font-weight:500;color:#fff;opacity:0;text-shadow:0 1px 5px rgba(0,0,0,.9),0 0 2px rgba(0,0,0,.9);white-space:nowrap}
#fa .cred{animation:compari .4s ease [[Q+0.8]] forwards}
#fb .cred{opacity:.95}
@keyframes compari{to{opacity:.95}}
/* apertura "scheda": la foto parte già in un riquadro (foto piccole, che a tutto schermo verrebbero sgranate) */
body.scheda #fa{left:60px;top:290px;width:960px;height:720px;border-radius:56px}
body.scheda #hook{bottom:auto;top:1050px;transform-origin:20% 0}
body.scheda #velo{display:none}
body.scheda #fa .cred{animation:none;opacity:.95}
#velo{position:absolute;left:0;top:0;width:1080px;height:440px;z-index:3;
 background:linear-gradient(180deg,rgba(255,255,255,.97) 0%,rgba(255,255,255,.93) 55%,rgba(255,255,255,0) 100%);animation:svanisci .5s ease [[Q+0.2]] forwards}
#tag{position:absolute;left:60px;top:186px;z-index:9;font-size:29px;font-weight:700;letter-spacing:3px;text-transform:uppercase;color:var(--acc);white-space:nowrap;max-width:700px;overflow:hidden}
.dot{display:inline-block;width:16px;height:16px;border-radius:50%;background:var(--acc);margin-right:14px}
#logo{position:absolute;left:790px;top:160px;width:230px;z-index:9;animation:svanisci .3s ease [[F-0.1]] forwards}

/* ---- 1. aggancio */
#hook{position:absolute;left:60px;bottom:400px;width:880px;z-index:6;background:#fff;border-radius:48px;padding:42px 46px 38px;box-shadow:0 26px 70px rgba(0,0,0,.30);transform-origin:20% 100%;
 animation:hookIn .7s cubic-bezier(.2,1.4,.3,1) 0s both, hookVia .4s cubic-bezier(.6,0,.9,.3) [[Q-0.1]] forwards}
@keyframes hookIn{from{transform:translateY(50px) scale(.95)}to{transform:none}}
@keyframes hookVia{to{transform:translateY(120px) scale(.9);opacity:0}}
#hook h1{font-size:86px;line-height:1.06;font-weight:700;letter-spacing:-2.8px;max-height:480px}
#hook h1 em{background:linear-gradient(var(--bg2),var(--bg2)) no-repeat 0 90%/0% 30%;animation:evid .6s cubic-bezier(.3,0,.2,1) .55s forwards;box-decoration-break:clone;-webkit-box-decoration-break:clone}
@keyframes evid{to{background-size:100% 30%}}
.invito{margin-top:26px;display:inline-flex;align-items:center;gap:14px;background:var(--acc);color:#fff;border-radius:999px;padding:12px 30px;font-size:34px;font-weight:700;transform-origin:0 50%;
 animation:pulsa .8s ease-in-out 1.1s infinite alternate}
@keyframes pulsa{to{transform:scale(1.06)}}

/* ---- 2. domanda e 3. risposta */
#quiz{position:absolute;left:0;top:0;width:1080px;height:1920px;z-index:6;animation:viaSu .4s ease-in [[P-0.4]] forwards}
#ring{position:absolute;left:776px;top:calc(208px + var(--ch));width:164px;height:164px;border-radius:50%;background:#fff;box-shadow:0 14px 34px rgba(0,0,0,.22);
 animation:pop .5s cubic-bezier(.2,1.5,.3,1) [[Q+0.7]] both, ringVia .3s ease-in [[R]] forwards}
@keyframes ringVia{to{transform:scale(0);opacity:0}}
#ring svg{position:absolute;left:0;top:0;width:164px;height:164px;transform:rotate(-90deg)}
#ring circle{fill:none;stroke-width:12}
#ring .tr{stroke:var(--bg2)}
#ring .pr{stroke:var(--acc);stroke-linecap:round;stroke-dasharray:408.4;stroke-dashoffset:0;animation:giro 3s linear [[C]] both}
@keyframes giro{to{stroke-dashoffset:408.4}}
#ring b{position:absolute;left:0;top:0;width:164px;height:164px;display:flex;align-items:center;justify-content:center;font-size:84px;font-weight:700;color:var(--dark);opacity:0}
#ring .n0{font-size:66px;animation:attesa [[C-Q-0.7]] linear [[Q+0.7]] both}
#ring .n3{animation:cifra 1s linear [[C]] both}
#ring .n2{animation:cifra 1s linear [[C+1]] both}
#ring .n1{animation:cifra 1s linear [[C+2]] both}
@keyframes attesa{0%{opacity:1}85%{opacity:1}100%{opacity:0}}
@keyframes cifra{0%{opacity:0;transform:scale(1.7)}14%{opacity:1;transform:scale(1)}86%{opacity:1;transform:scale(1)}100%{opacity:0;transform:scale(.6)}}
#qlab{position:absolute;left:60px;top:calc(326px + var(--ch));background:var(--acc);color:#fff;font-size:27px;font-weight:700;letter-spacing:3px;padding:9px 24px;border-radius:999px;text-transform:uppercase;
 animation:daSin .5s cubic-bezier(.2,1.2,.3,1) [[Q+0.55]] both}
#qq{position:absolute;left:60px;top:calc(390px + var(--ch));width:880px;height:146px;font-size:62px;line-height:1.08;font-weight:700;letter-spacing:-1.6px;display:flex;align-items:center;
 animation:suIn .55s cubic-bezier(.2,1.2,.3,1) [[Q+0.7]] both}
.opt{position:absolute;left:60px;width:880px;border-radius:36px;background-color:#fff;box-shadow:0 12px 34px rgba(0,0,0,.10);display:flex;align-items:center;gap:22px;padding:0 26px;font-size:38px;font-weight:700;line-height:1.12}
.opt i{flex:none;width:66px;height:66px;border-radius:50%;background-color:var(--bg2);color:var(--acc);font-style:normal;display:flex;align-items:center;justify-content:center;font-size:34px;font-weight:700}
.opt span{flex:1;display:block;max-height:100%}
.opt u{flex:none;text-decoration:none;width:60px;height:60px;border-radius:50%;background:#fff;color:var(--acc);display:flex;align-items:center;justify-content:center;font-size:40px;font-weight:700;transform:scale(0)}
@keyframes giusta{0%{transform:scale(1)}45%{transform:scale(1.07);background-color:var(--acc);color:#fff}100%{transform:scale(1.03);background-color:var(--acc);color:#fff}}
@keyframes sbagliata{to{opacity:.4;transform:scale(.96)}}
.ok i{animation:bianco .3s ease [[R+0.1]] forwards}
@keyframes bianco{to{background-color:#fff}}
.ok u{animation:pop .45s cubic-bezier(.2,1.6,.3,1) [[R+0.25]] both}
.ok::after{content:"";position:absolute;left:50%;top:50%;width:60px;height:60px;margin:-30px;border-radius:50%;border:5px solid var(--acc);opacity:0;animation:onda .7s ease-out [[R]] forwards}
@keyframes onda{0%{opacity:.85;width:60px;height:60px;margin:-30px}100%{opacity:0;width:1100px;height:1100px;margin:-550px}}
#spiega{position:absolute;left:60px;width:880px;border-radius:36px;padding:26px 34px;background:var(--dark);color:#fff;font-size:35px;font-weight:600;line-height:1.26;
 animation:suIn .6s cubic-bezier(.2,1.2,.3,1) [[R+0.55]] both}
#spiega b{font-weight:700;color:var(--hl)}

/* ---- 4. prodotto */
#disc{position:absolute;left:150px;top:350px;width:780px;height:780px;border-radius:50%;z-index:4;
 background:linear-gradient(150deg,color-mix(in srgb,var(--acc) 70%,#fff) 0%,var(--acc) 66%,color-mix(in srgb,var(--acc) 80%,var(--dark)) 100%);
 animation:pop .7s cubic-bezier(.2,1.3,.3,1) [[P-0.05]] both, discVia .5s ease-in [[D-0.1]] forwards}
@keyframes discVia{to{transform:scale(0);opacity:0}}
#pmove{position:absolute;left:190px;top:330px;width:700px;height:820px;z-index:8;display:flex;align-items:center;justify-content:center;
 animation:pEntra .85s cubic-bezier(.2,1.3,.3,1) [[P+0.1]] both, pDose .8s cubic-bezier(.65,0,.2,1) [[D]] forwards, pVia .45s ease-in [[F-0.3]] forwards}
@keyframes pEntra{from{transform:translateY(1900px) rotate(-10deg) scale(.7)}to{transform:none}}
@keyframes pDose{to{transform:translate(-335px,640px) scale(var(--ps))}}
@keyframes pVia{from{transform:translate(-335px,640px) scale(var(--ps))}to{transform:translate(-335px,1700px) scale(var(--ps))}}
#pimg{max-width:640px;max-height:780px;filter:drop-shadow(0 26px 30px rgba(0,0,0,.30));animation:galla 3s ease-in-out [[P+1]] infinite}
@keyframes galla{0%,100%{transform:translateY(0) rotate(0)}50%{transform:translateY(-14px) rotate(.8deg)}}
#ptxt{position:absolute;left:0;top:0;width:1080px;height:1920px;z-index:7;animation:viaSu .4s ease-in [[D-0.35]] forwards}
#pnome{position:absolute;left:140px;top:1186px;width:800px;text-align:center;font-size:104px;line-height:1.05;font-weight:700;letter-spacing:-3.5px;white-space:nowrap;animation:suIn .6s cubic-bezier(.2,1.2,.3,1) [[P+0.55]] both}
#ptipo{position:absolute;left:140px;top:1310px;width:800px;text-align:center;font-size:40px;font-weight:700;color:var(--acc);white-space:nowrap;animation:suIn .6s cubic-bezier(.2,1.2,.3,1) [[P+0.7]] both}
#pregi{position:absolute;left:140px;top:1392px;width:800px;display:flex;flex-wrap:wrap;gap:14px;justify-content:center;font-size:31px}
.pregio{background:#fff;border-radius:999px;box-shadow:0 10px 26px rgba(0,0,0,.10);font-size:1em;font-weight:700;padding:.42em .84em;white-space:nowrap}

/* ---- 5. dose */
#dose{position:absolute;left:0;top:0;width:1080px;height:1920px;z-index:6;animation:viaSu .4s ease-in [[F-0.4]] forwards}
#fb{position:absolute;left:60px;top:290px;width:960px;height:600px;border-radius:56px;overflow:hidden;box-shadow:0 26px 60px rgba(0,0,0,.22);
 animation:fbIn .8s cubic-bezier(.2,1.15,.3,1) [[D]] both}
@keyframes fbIn{from{transform:translateX(1150px) rotate(5deg)}to{transform:none}}
#fb img{animation:kb2 [[F-D+1]] linear [[D]] both}
@keyframes kb2{from{transform:scale(1.04)}to{transform:scale(1.17)}}
.phlab{position:absolute;right:26px;top:24px;background:rgba(255,255,255,.95);color:var(--dark);border-radius:999px;padding:9px 24px;font-size:27px;font-weight:700}
#dcol{position:absolute;left:60px;top:926px;width:880px;display:flex;flex-direction:column;gap:22px}
#dbox{border-radius:40px;padding:26px 40px 28px;background:var(--dark);color:#fff;animation:suIn .6s cubic-bezier(.2,1.2,.3,1) [[D+0.35]] both}
#dbox .dl{font-size:25px;font-weight:700;letter-spacing:3px;text-transform:uppercase;opacity:.78}
#dbox .dv{font-size:98px;font-weight:700;line-height:1.06;letter-spacing:-2.5px;margin-top:2px;white-space:nowrap;width:800px;transform-origin:0 50%;animation:timbro .55s cubic-bezier(.2,1.6,.3,1) [[D+0.8]] both}
@keyframes timbro{from{transform:scale(1.45);opacity:0}to{transform:none;opacity:1}}
#dbox .dn{font-size:31px;font-weight:500;opacity:.9;margin-top:4px;line-height:1.25}
#dpunti{margin-left:330px;display:flex;flex-direction:column;gap:14px}
.dp{min-height:98px;background:#fff;border-radius:28px;box-shadow:0 10px 28px rgba(0,0,0,.09);padding:14px 22px;display:flex;gap:14px;align-items:center;font-size:30px;font-weight:700;line-height:1.2}
.dp i{font-style:normal;color:var(--acc);font-size:36px;font-weight:700;line-height:1}

/* ---- 6. banco */
#flogo{position:absolute;left:170px;top:360px;width:740px;height:290px;z-index:6;background:#fff;border-radius:60px;box-shadow:0 24px 60px rgba(0,0,0,.13);display:flex;align-items:center;justify-content:center;
 animation:pop .7s cubic-bezier(.2,1.3,.3,1) [[F]] both}
#flogo img{width:560px}
#fcol{position:absolute;left:60px;top:740px;width:880px;z-index:6;display:flex;flex-direction:column;gap:36px;align-items:flex-start}
#ftit{max-height:350px;font-size:80px;line-height:1.07;font-weight:700;letter-spacing:-2.5px;animation:suIn .6s cubic-bezier(.2,1.2,.3,1) [[F+0.3]] both}
#fcomm{background:#fff;border-radius:36px;box-shadow:0 12px 34px rgba(0,0,0,.10);padding:22px 32px;font-size:36px;font-weight:700;line-height:1.2;animation:suIn .6s cubic-bezier(.2,1.2,.3,1) [[F+0.65]] both}
#flegge{font-size:27px;line-height:1.42;font-weight:500;opacity:.82;border-top:2px solid rgba(0,0,0,.16);padding-top:22px;animation:compari2 .6s ease [[F+0.9]] both}
@keyframes compari2{from{opacity:0}to{opacity:.82}}
"""

def _t(expr, T):
    return f"{eval(expr, {}, T):.3f}s"


def html_video(v, T=TEMPI):
    acc, dark, bg1, bg2, hl = k._pal(v["colore"])
    n = len(v["opzioni"])
    ch = v.get("ch", 560 if n == 2 else 470)    # altezza del riquadro della foto durante la domanda (rendi_video.js la riduce se la spiegazione non ci sta)
    oh = 118 if n == 2 else 104                 # altezza di una risposta
    y0 = 556                                    # prima risposta, misurata dal fondo del riquadro foto (290 + 266)
    from PIL import Image
    pw, ph = Image.open(k.FOTO / f"{v['prodotto']}.png").size; f0 = min(640 / pw, 780 / ph)
    ps = min(290 / (pw * f0), 440 / (ph * f0), 0.75)
    css = re.sub(r"\[\[(.+?)\]\]", lambda m: _t(m.group(1), T), CSS)
    legge = k.DISC if v.get("fito", True) else "Prima dell'uso leggere sempre l'etichetta del prodotto."
    fa, fb = v["foto_a"], v["foto_b"]
    opts = ""
    for i, o in enumerate(v["opzioni"]):
        ok = i == v["giusta"]
        anim = f"daDes .55s cubic-bezier(.2,1.2,.3,1) {T['Q'] + 0.95 + i * 0.16:.3f}s both, " + (
            f"giusta .6s cubic-bezier(.2,1.4,.3,1) {T['R']:.3f}s forwards" if ok else f"sbagliata .4s ease {T['R']:.3f}s forwards")
        opts += (f'<div class="opt{" ok" if ok else ""}" style="top:calc(var(--ch) + {y0 + i * (oh + 14)}px);height:{oh}px;animation:{anim}">'
                 f'<i>{"ABC"[i]}</i><span data-min="28"><div>{o}</div></span>{"<u>✓</u>" if ok else ""}</div>')
    ysp = y0 + n * (oh + 14) + 8
    pregi = "".join(f'<div class="pregio" style="animation:suIn .5s cubic-bezier(.2,1.3,.3,1) {T["P"] + 0.95 + i * 0.18:.3f}s both">{p}</div>'
                    for i, p in enumerate(v["pregi"]))
    punti = "".join(f'<div class="dp" style="animation:daDes .55s cubic-bezier(.2,1.2,.3,1) {T["D"] + 1.2 + i * 0.22:.3f}s both"><i>✓</i><span>{p}</span></div>'
                    for i, p in enumerate(v["dose"]["punti"]))
    d = v["dose"]
    return f"""<!DOCTYPE html><html><head><meta charset="utf-8"><style>{k.FONT}{css}</style></head>
<body class="{v.get('apertura', '')}" style="{k._vars(v['colore'])};--hl:{hl};--ch:{ch}px;--ps:{ps:.3f}">
<div class="blob b1"></div><div class="blob b2"></div>
<div id="fa"><img src="{(FOTO / fa['file']).as_uri()}" style="object-position:{fa.get('pos', '50% 50%')};transform-origin:{fa.get('pos', '50% 50%')}"><div class="cred">{fa.get('credito', '')}</div></div>
<div id="velo"></div>
<div id="tag"><span class="dot"></span>{v['tag']}</div><img id="logo" src="{k.LOGO.as_uri()}">
<div id="hook"><h1 data-min="60"><div>{v['aggancio']}</div></h1><div class="invito">{v['invito']}</div></div>
<div id="quiz">
 <div id="ring"><svg viewBox="0 0 164 164"><circle class="tr" cx="82" cy="82" r="65"/><circle class="pr" cx="82" cy="82" r="65"/></svg><b class="n0">⏱</b><b class="n3">3</b><b class="n2">2</b><b class="n1">1</b></div>
 <div id="qlab">{v.get('etichetta_domanda', 'Tu cosa rispondi?')}</div>
 <div id="qq" data-min="40"><div>{v['domanda']}</div></div>
 {opts}
 <div id="spiega" data-fondo="{FONDO}" style="top:calc(var(--ch) + {ysp}px)">{v['spiega']}</div>
</div>
<div id="disc"></div>
<div id="pmove"><img id="pimg" src="{k._foto(v['prodotto'])}"></div>
<div id="ptxt"><div id="pnome" data-min="56"><div>{v['nome']}</div></div><div id="ptipo" data-min="28"><div>{v['tipo']}</div></div><div id="pregi" data-fondo="{FONDO}" data-minf="29">{pregi}</div></div>
<div id="dose">
 <div id="fb"><img src="{(FOTO / fb['file']).as_uri()}" style="object-position:{fb.get('pos', '50% 50%')};transform-origin:{fb.get('pos', '50% 50%')}"><div class="cred">{fb.get('credito', '')}</div><div class="phlab">{fb['etichetta']}</div></div>
 <div id="dcol" data-fondo="{FONDO}"><div id="dbox"><div class="dl">{d['etichetta']}</div><div class="dv" data-min="54"><div>{d['valore']}</div></div><div class="dn">{d['nota']}</div></div>
 <div id="dpunti">{punti}</div></div>
</div>
<div id="flogo" ><img src="{k.LOGO.as_uri()}"></div>
<div id="fcol" data-fondo="{FONDO}"><div id="ftit" data-min="56"><div>{v['chiusa']}</div></div><div id="fcomm">{v['commenti']}</div><div id="flegge">{legge}</div></div>
</body></html>"""


def controlla(v):
    """Stessi divieti del kit sui testi: produttori, parole assolute, prezzi, parole da non usare."""
    low = k.testo_piatto({a: b for a, b in v.items() if a not in ("id", "prodotto", "foto_a", "foto_b")}).lower()
    err = [f"produttore: {p}" for p in k.PRODUTTORI if k._parola(p, low)]
    err += [f"parola assoluta: {p}" for p in k.ASSOLUTE if k._parola(p, low)]
    err += [f"prezzo: {p}" for p in k.PREZZI if k._parola(p, low)]
    err += [m for p, m in k.PAROLE_NO.items() if k._parola(p, low)]
    return err


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]; prova = "--prova" in sys.argv
    for v in json.loads((QUI / "video_foto.json").read_text(encoding="utf-8")):
        if args and v["id"] not in args: continue
        T = dict(TEMPI, **v.get("tempi", {}))
        err = controlla(v)
        if err: print(v["id"], "TESTI DA CORREGGERE:", err); continue
        html = QUI / f".{v['id']}_video.html"; html.write_text(html_video(v, T), encoding="utf-8")
        fr = QUI / (f"prova_{v['id']}" if prova else f".frame_{v['id']}")
        shutil.rmtree(fr, ignore_errors=True); fr.mkdir()
        cmd = ["node", str(QUI / "rendi_video.js"), str(html), str(fr), str(T["FINE"]), str(FPS)]
        if prova:
            cmd.append(",".join(str(int(t * FPS)) for t in (0, 1.6, T["Q"] + 0.45, T["C"] + 0.5, T["C"] + 2.5, T["R"] + 0.3, T["R"] + 2.5,
                                                           T["P"] + 0.5, T["P"] + 3, T["D"] + 0.5, T["D"] + 4, T["F"] + 2.5)))
        r = subprocess.run(cmd, capture_output=True, text=True)
        print(v["id"], r.stdout.strip(), r.stderr.strip()[-400:])
        html.unlink()
        if prova or r.returncode: continue
        out = QUI / f"{v['id']}_tiktok.mp4"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", str(fr / "f%05d.jpg"),
                        "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo", "-shortest", "-c:v", "libx264", "-preset", "slow", "-crf", "18",
                        "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", str(out)], check=True)
        shutil.rmtree(fr); print("  ->", out.name, f"{out.stat().st_size / 1e6:.1f} MB")


if __name__ == "__main__":
    main()
