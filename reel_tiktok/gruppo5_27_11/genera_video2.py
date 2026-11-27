#!/usr/bin/env python3
"""Video TikTok "foto e dato" (27/11/2026), seconda versione, dopo la risposta di Valerio al prototipo.

Valerio (27/11, 13:34): il formato con le foto vere va bene, ma "dobbiamo togliere quella domanda perché si perde tempo e
non è il format giusto" e "devi aggiungere cose più tecniche anche per agricoltori esperti". Si perfeziona prima UN video
(Portento SL), poi si rifanno gli altri.

Come è fatto (1080x1920, 30 fotogrammi al secondo, circa 27 secondi, senza audio: la musica la mette Valerio dall'app):
  1. aggancio   foto vera a tutto schermo e, subito, un dato tecnico che incuriosisce (nessuna domanda, nessuna attesa)
  2. perché     la foto si stringe in un riquadro: due dati verificati su cosa fa il fungo e quindi quando intervenire
  3. come       foto della coltura e i meccanismi d'azione scritti in etichetta (da dove arriva ogni dato: vedi video_foto2.json)
  4. prodotto   la confezione scontornata entra al centro con nome, tipo, un bollino con il numero e due punti
  5. dose       foto della coltura, dose di etichetta in grande, tre regole d'uso
  6. banco      logo, invito al banco di Vittoria, frase di legge
Stile Studio 4: sfondo chiaro del kit nel colore del prodotto, logo e carattere del kit (kit/s4kit.py, non modificato).
Zona sicura di TikTok: testi essenziali tra y 131 e y 1560 e senza superare x 940 (a destra ci sono le icone).

Uso:  NODE_PATH=$(npm root -g) python3 genera_video2.py [id ...] [--prova]
  --prova   salva solo i fotogrammi di controllo in prova2_<id>/ (niente video)
Dati: video_foto2.json. Foto: foto_video/ (ogni foto ha autore e licenza in foto_video/CREDITI.md).
"""
import json, re, shutil, subprocess, sys
from pathlib import Path
QUI = Path(__file__).resolve().parent; REPO = QUI.parent.parent
sys.path.insert(0, str(REPO / "kit")); import s4kit as k
FOTO = QUI / "foto_video"
FPS = 30
# inizio di ogni scena, in secondi: S perché, M come, P prodotto, D dose, F finale
TEMPI = {"S": 3.6, "M": 9.2, "P": 14.4, "D": 18.0, "F": 23.6, "FINE": 27.2}
FONDO = 1560    # sotto questa quota TikTok mette nome e didascalia: i testi devono finire prima

CSS = """
*{box-sizing:border-box;margin:0;padding:0}
html,body{width:1080px;height:1920px;overflow:hidden}
body{font-family:P,'Noto Color Emoji',sans-serif;color:var(--dark);position:relative;background:linear-gradient(160deg,var(--bg1) 0%,var(--bg2) 100%)}
em{font-style:normal;color:var(--acc)}
.blob{position:absolute;border-radius:50%;background:var(--acc)}
.b1{width:900px;height:900px;left:-420px;top:1180px;opacity:.10;animation:drift1 27s ease-in-out 0s infinite alternate}
.b2{width:560px;height:560px;left:800px;top:380px;opacity:.07;animation:drift2 27s ease-in-out 0s infinite alternate}
@keyframes drift1{to{transform:translate(140px,-180px) scale(1.12)}}
@keyframes drift2{to{transform:translate(-110px,160px) scale(.88)}}
@keyframes svanisci{to{opacity:0}}
@keyframes pop{from{transform:scale(0)}to{transform:scale(1)}}
@keyframes suIn{from{transform:translateY(46px);opacity:0}to{transform:none;opacity:1}}
@keyframes daSin{from{transform:translateX(-80px);opacity:0}to{transform:none;opacity:1}}
@keyframes daDes{from{transform:translateX(150px);opacity:0}to{transform:none;opacity:1}}
@keyframes viaSu{to{transform:translateY(-50px);opacity:0}}
@keyframes timbro{from{transform:scale(1.45);opacity:0}to{transform:none;opacity:1}}

/* ---- foto A: a tutto schermo, poi riquadro */
#fa{position:absolute;left:0;top:0;width:1080px;height:1920px;overflow:hidden;z-index:2;box-shadow:0 26px 60px rgba(0,0,0,.24);
 animation:faCard .9s cubic-bezier(.7,0,.2,1) [[S]] forwards, faVia .55s cubic-bezier(.6,0,.9,.3) [[M-0.45]] forwards}
#fa img,#fb img,#fc img{width:100%;height:100%;object-fit:cover;display:block}
#fa img{animation:kb [[M]] linear 0s both}
@keyframes kb{from{transform:scale(1.02)}to{transform:scale(1.2)}}
@keyframes faCard{to{left:60px;top:290px;width:960px;height:var(--ch);border-radius:56px}}
@keyframes faVia{to{transform:translateX(-1150px) rotate(-7deg);opacity:0}}
.cred{position:absolute;left:30px;bottom:16px;font-size:20px;font-weight:500;color:#fff;opacity:0;text-shadow:0 1px 5px rgba(0,0,0,.9),0 0 2px rgba(0,0,0,.9);white-space:nowrap}
#fa .cred{animation:compari .4s ease [[S+0.8]] forwards}
#fb .cred,#fc .cred{opacity:.95}
@keyframes compari{to{opacity:.95}}
/* apertura "scheda": la foto parte già in un riquadro (foto piccole, che a tutto schermo verrebbero sgranate) */
body.scheda #fa{left:60px;top:290px;width:960px;height:720px;border-radius:56px}
body.scheda #velo{display:none}
body.scheda #fa .cred{animation:none;opacity:.95}
body.scheda #hook{bottom:auto;top:1050px;transform-origin:20% 0}
#velo{position:absolute;left:0;top:0;width:1080px;height:440px;z-index:3;
 background:linear-gradient(180deg,rgba(255,255,255,.97) 0%,rgba(255,255,255,.93) 55%,rgba(255,255,255,0) 100%);animation:svanisci .5s ease [[S+0.2]] forwards}
#tag{position:absolute;left:60px;top:186px;z-index:9;font-size:29px;font-weight:700;letter-spacing:3px;text-transform:uppercase;color:var(--acc);white-space:nowrap;max-width:700px;overflow:hidden}
.dot{display:inline-block;width:16px;height:16px;border-radius:50%;background:var(--acc);margin-right:14px}
#logo{position:absolute;left:790px;top:160px;width:230px;z-index:9;animation:svanisci .3s ease [[F-0.1]] forwards}

/* ---- 1. aggancio */
#hook{position:absolute;left:60px;bottom:400px;width:880px;z-index:6;background:#fff;border-radius:48px;padding:42px 46px 38px;box-shadow:0 26px 70px rgba(0,0,0,.30);transform-origin:20% 100%;
 animation:hookIn .7s cubic-bezier(.2,1.4,.3,1) 0s both, hookVia .4s cubic-bezier(.6,0,.9,.3) [[S-0.1]] forwards}
@keyframes hookIn{from{transform:translateY(50px) scale(.95)}to{transform:none}}
@keyframes hookVia{to{transform:translateY(120px) scale(.9);opacity:0}}
#hook h1{font-size:86px;line-height:1.06;font-weight:700;letter-spacing:-2.8px;max-height:480px}
#hook h1 em{background:linear-gradient(var(--bg2),var(--bg2)) no-repeat 0 90%/0% 30%;animation:evid .6s cubic-bezier(.3,0,.2,1) .55s forwards;box-decoration-break:clone;-webkit-box-decoration-break:clone}
@keyframes evid{to{background-size:100% 30%}}
.invito{margin-top:26px;display:inline-flex;align-items:center;gap:14px;background:var(--acc);color:#fff;border-radius:999px;padding:12px 30px;font-size:34px;font-weight:700;transform-origin:0 50%;
 animation:pulsa .8s ease-in-out 1.1s infinite alternate}
@keyframes pulsa{to{transform:scale(1.06)}}

/* ---- 2. perché: due dati verificati */
#ex{position:absolute;left:0;top:0;width:1080px;height:1920px;z-index:6;animation:viaSu .4s ease-in [[M-0.4]] forwards}
#xcol{position:absolute;left:60px;top:calc(328px + var(--ch));width:880px;display:flex;flex-direction:column;gap:22px}
#xs1{border-radius:40px;padding:24px 40px 28px;background:var(--dark);color:#fff;animation:suIn .6s cubic-bezier(.2,1.2,.3,1) [[S+0.5]] both}
#xs1 .xl{font-size:25px;font-weight:700;letter-spacing:3px;text-transform:uppercase;opacity:.78}
#xs1 .xv{font-size:124px;font-weight:700;line-height:1.04;letter-spacing:-3.5px;margin-top:2px;white-space:nowrap;width:800px;transform-origin:0 50%;animation:timbro .55s cubic-bezier(.2,1.6,.3,1) [[S+1.0]] both}
#xs1 .xv small{font-size:.34em;font-weight:600;letter-spacing:0;opacity:.8;margin-right:.3em}
#xs1 .xb{position:relative;height:16px;border-radius:8px;background:rgba(255,255,255,.2);margin:20px 15px 12px}
#xs1 .xb::before{content:"";position:absolute;left:0;top:0;bottom:0;width:100%;border-radius:8px;background:var(--hl);transform-origin:0 50%;animation:riempi 1.6s cubic-bezier(.5,0,.3,1) [[S+1.3]] both}
@keyframes riempi{from{transform:scaleX(0)}to{transform:scaleX(1)}}
#xs1 .xb i{position:absolute;top:50%;width:32px;height:32px;margin:-16px 0 0 -16px;border-radius:50%;background:#fff;box-shadow:0 0 0 7px rgba(255,255,255,.25)}
#xs1 .xb i.a{left:0}
#xs1 .xb i.b{left:100%;animation:pop .45s cubic-bezier(.2,1.7,.3,1) [[S+2.75]] both}
#xs1 .xe{display:flex;justify-content:space-between;font-size:26px;font-weight:700;letter-spacing:.5px}
#xs1 .xn{font-size:34px;font-weight:500;line-height:1.25;opacity:.92;margin-top:14px}
#xs2{display:flex;align-items:center;gap:22px;border-radius:36px;padding:20px 30px 20px 22px;background:#fff;box-shadow:0 12px 34px rgba(0,0,0,.10);font-size:40px;font-weight:700;line-height:1.16;animation:daDes .55s cubic-bezier(.2,1.2,.3,1) [[S+2.0]] both}
#xs2 i{flex:none;position:relative;width:84px;height:84px;border-radius:50%;background:var(--bg2);font-style:normal;font-size:46px;display:flex;align-items:center;justify-content:center}
#xs2 i.no::after{content:"";position:absolute;left:10px;right:10px;top:50%;height:7px;margin-top:-3px;background:var(--acc);border-radius:4px;transform:rotate(-42deg);box-shadow:0 0 0 3px var(--bg2)}
#xs2 b{color:var(--acc);font-weight:700}
#xs3{align-self:flex-start;border-radius:999px;padding:18px 40px;background:var(--acc);color:#fff;font-size:40px;font-weight:700;animation:suIn .55s cubic-bezier(.2,1.3,.3,1) [[S+3.5]] both}

/* ---- 3. come lavora: meccanismi d'azione */
#co{position:absolute;left:0;top:0;width:1080px;height:1920px;z-index:6;animation:viaSu .4s ease-in [[P-0.4]] forwards}
#fc{position:absolute;left:60px;top:290px;width:960px;height:440px;border-radius:56px;overflow:hidden;box-shadow:0 26px 60px rgba(0,0,0,.22);
 animation:fbIn .8s cubic-bezier(.2,1.15,.3,1) [[M]] both}
@keyframes fbIn{from{transform:translateX(1150px) rotate(5deg)}to{transform:none}}
#fc img{animation:kb2 [[P-M+1]] linear [[M]] both}
@keyframes kb2{from{transform:scale(1.04)}to{transform:scale(1.17)}}
.phlab{position:absolute;right:26px;top:24px;background:rgba(255,255,255,.95);color:var(--dark);border-radius:999px;padding:9px 24px;font-size:27px;font-weight:700}
#mcol{position:absolute;left:60px;top:768px;width:880px;display:flex;flex-direction:column;gap:22px}
.mec{display:flex;align-items:center;gap:24px;border-radius:38px;padding:24px 28px 24px 24px;background:#fff;box-shadow:0 12px 34px rgba(0,0,0,.10)}
.mec i{flex:none;width:94px;height:94px;border-radius:50%;background:var(--bg2);font-style:normal;font-size:48px;display:flex;align-items:center;justify-content:center}
.mec strong{display:block;font-size:44px;line-height:1.1;font-weight:700;letter-spacing:-.6px}
.mec span{display:block;font-size:31px;line-height:1.2;font-weight:500;opacity:.86;margin-top:4px}
#bm{align-self:flex-start;border-radius:999px;padding:14px 34px;background:var(--dark);color:#fff;font-size:33px;font-weight:700;white-space:nowrap}

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
#stk{position:absolute;left:760px;top:322px;width:262px;height:262px;border-radius:50%;z-index:9;background:#fff;box-shadow:0 18px 44px rgba(0,0,0,.24);
 display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;padding:0 22px;border:7px solid var(--acc);
 animation:stkIn .65s cubic-bezier(.2,1.6,.3,1) [[P+1.2]] both, discVia .5s ease-in [[D-0.1]] forwards}
@keyframes stkIn{from{transform:scale(0) rotate(-30deg)}to{transform:rotate(8deg)}}
#stk small{font-size:25px;font-weight:700;letter-spacing:2px;text-transform:uppercase;color:var(--acc);line-height:1}
#stk b{font-size:104px;font-weight:700;line-height:.96;letter-spacing:-4px;color:var(--dark)}
#stk span{font-size:23px;font-weight:700;line-height:1.14;color:var(--dark)}
#ptxt{position:absolute;left:0;top:0;width:1080px;height:1920px;z-index:7;animation:viaSu .4s ease-in [[D-0.35]] forwards}
#pnome{position:absolute;left:140px;top:1186px;width:800px;text-align:center;font-size:104px;line-height:1.05;font-weight:700;letter-spacing:-3.5px;white-space:nowrap;animation:suIn .6s cubic-bezier(.2,1.2,.3,1) [[P+0.55]] both}
#ptipo{position:absolute;left:140px;top:1310px;width:800px;text-align:center;font-size:40px;font-weight:700;color:var(--acc);white-space:nowrap;animation:suIn .6s cubic-bezier(.2,1.2,.3,1) [[P+0.7]] both}
#pregi{position:absolute;left:140px;top:1392px;width:800px;display:flex;flex-wrap:wrap;gap:14px;justify-content:center;font-size:31px}
.pregio{background:#fff;border-radius:999px;box-shadow:0 10px 26px rgba(0,0,0,.10);font-size:1em;font-weight:700;padding:.42em .84em;white-space:nowrap}

/* ---- 5. dose */
#dose{position:absolute;left:0;top:0;width:1080px;height:1920px;z-index:6;animation:viaSu .4s ease-in [[F-0.4]] forwards}
#fb{position:absolute;left:60px;top:290px;width:960px;height:600px;border-radius:56px;overflow:hidden;box-shadow:0 26px 60px rgba(0,0,0,.22);
 animation:fbIn .8s cubic-bezier(.2,1.15,.3,1) [[D]] both}
#fb img{animation:kb2 [[F-D+1]] linear [[D]] both}
#dcol{position:absolute;left:60px;top:926px;width:880px;display:flex;flex-direction:column;gap:22px}
#dbox{border-radius:40px;padding:26px 40px 28px;background:var(--dark);color:#fff;animation:suIn .6s cubic-bezier(.2,1.2,.3,1) [[D+0.35]] both}
#dbox .dl{font-size:25px;font-weight:700;letter-spacing:3px;text-transform:uppercase;opacity:.78}
#dbox .dv{font-size:98px;font-weight:700;line-height:1.06;letter-spacing:-2.5px;margin-top:2px;white-space:nowrap;width:800px;transform-origin:0 50%;animation:timbro .55s cubic-bezier(.2,1.6,.3,1) [[D+0.8]] both}
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
    ch = v.get("ch", 500)                      # altezza del riquadro della foto A durante la spiegazione
    ex, me, d = v["spiegazione"], v["meccanismi"], v["dose"]
    from PIL import Image
    pw, ph = Image.open(k.FOTO / f"{v['prodotto']}.png").size; f0 = min(640 / pw, 780 / ph)
    ps = min(290 / (pw * f0), 440 / (ph * f0), 0.75)
    css = re.sub(r"\[\[(.+?)\]\]", lambda m: _t(m.group(1), T), CSS)
    legge = k.DISC if v.get("fito", True) else "Prima dell'uso leggere sempre l'etichetta del prodotto."
    fa, fb, fc = v["foto_a"], v["foto_b"], me["foto"]
    g = ex["grande"]; fatto = ex["fatto"]
    pre = f'<small>{g["prefisso"]}</small>' if g.get("prefisso") else ""
    mecc = "".join(
        f'<div class="mec" style="animation:daDes .55s cubic-bezier(.2,1.2,.3,1) {T["M"] + 0.7 + i * 0.75:.3f}s both"><i>{ic}</i><div><strong>{tit}</strong><span>{txt}</span></div></div>'
        for i, (ic, tit, txt) in enumerate(me["voci"]))
    pregi = "".join(f'<div class="pregio" style="animation:suIn .5s cubic-bezier(.2,1.3,.3,1) {T["P"] + 0.95 + i * 0.18:.3f}s both">{p}</div>'
                    for i, p in enumerate(v["pregi"]))
    punti = "".join(f'<div class="dp" style="animation:daDes .55s cubic-bezier(.2,1.2,.3,1) {T["D"] + 1.2 + i * 0.22:.3f}s both"><i>✓</i><span>{p}</span></div>'
                    for i, p in enumerate(d["punti"]))
    bol = v.get("bollino")
    stk = (f'<div id="stk"><small>{bol["sopra"]}</small><b>{bol["grande"]}</b><span>{bol["sotto"]}</span></div>') if bol else ""
    return f"""<!DOCTYPE html><html><head><meta charset="utf-8"><style>{k.FONT}{css}</style></head>
<body class="{v.get('apertura', '')}" style="{k._vars(v['colore'])};--hl:{hl};--ch:{ch}px;--ps:{ps:.3f}">
<div class="blob b1"></div><div class="blob b2"></div>
<div id="fa"><img src="{(FOTO / fa['file']).as_uri()}" style="object-position:{fa.get('pos', '50% 50%')};transform-origin:{fa.get('pos', '50% 50%')}"><div class="cred">{fa.get('credito', '')}</div></div>
<div id="velo"></div>
<div id="tag"><span class="dot"></span>{v['tag']}</div><img id="logo" src="{k.LOGO.as_uri()}">
<div id="hook"><h1 data-min="60"><div>{v['aggancio']}</div></h1><div class="invito">{v['invito']}</div></div>
<div id="ex">
 <div id="xcol" data-fondo="{FONDO}">
  <div id="xs1"><div class="xl">{g['etichetta']}</div><div class="xv" data-min="64"><div>{pre}{g['valore']}</div></div><div class="xb"><i class="a"></i><i class="b"></i></div><div class="xe"><span>{g['da']}</span><span>{g['a']}</span></div><div class="xn">{g['nota']}</div></div>
  <div id="xs2"><i class="{fatto.get('classe', '')}">{fatto['icona']}</i><div>{fatto['testo']}</div></div>
  <div id="xs3">{ex['chiusa']}</div>
 </div>
</div>
<div id="co">
 <div id="fc"><img src="{(FOTO / fc['file']).as_uri()}" style="object-position:{fc.get('pos', '50% 50%')};transform-origin:{fc.get('pos', '50% 50%')}"><div class="cred">{fc.get('credito', '')}</div><div class="phlab">{fc['etichetta']}</div></div>
 <div id="mcol" data-fondo="{FONDO}">{mecc}<div id="bm" style="animation:suIn .55s cubic-bezier(.2,1.3,.3,1) {T['M'] + 0.7 + len(me['voci']) * 0.75:.3f}s both">{me['chiusa']}</div></div>
</div>
<div id="disc"></div>
<div id="pmove"><img id="pimg" src="{k._foto(v['prodotto'])}"></div>
{stk}
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
    tolti = ("id", "prodotto", "foto_a", "foto_b")
    ammessi = {a: b for a, b in v.items() if a not in tolti}
    ammessi["meccanismi"] = {a: b for a, b in v["meccanismi"].items() if a != "foto"}
    low = k.testo_piatto(ammessi).lower()
    err = [f"produttore: {p}" for p in k.PRODUTTORI if k._parola(p, low)]
    err += [f"parola assoluta: {p}" for p in k.ASSOLUTE if k._parola(p, low)]
    err += [f"prezzo: {p}" for p in k.PREZZI if k._parola(p, low)]
    err += [m for p, m in k.PAROLE_NO.items() if k._parola(p, low)]
    return err


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]; prova = "--prova" in sys.argv
    for v in json.loads((QUI / "video_foto2.json").read_text(encoding="utf-8")):
        if args and v["id"] not in args: continue
        T = dict(TEMPI, **v.get("tempi", {}))
        err = controlla(v)
        if err: print(v["id"], "TESTI DA CORREGGERE:", err); continue
        html = QUI / f".{v['id']}_video2.html"; html.write_text(html_video(v, T), encoding="utf-8")
        fr = QUI / (f"prova2_{v['id']}" if prova else f".frame2_{v['id']}")
        shutil.rmtree(fr, ignore_errors=True); fr.mkdir()
        cmd = ["node", str(QUI / "rendi_video.js"), str(html), str(fr), str(T["FINE"]), str(FPS)]
        if prova:
            ts = (0, 1.5, T["S"] + 0.3, T["S"] + 1.3, T["S"] + 2.6, T["S"] + 4.4, T["M"] + 0.45, T["M"] + 1.5, T["M"] + 3.0, T["M"] + 4.3,
                  T["P"] + 0.5, T["P"] + 2.8, T["D"] + 0.5, T["D"] + 3.0, T["D"] + 4.8, T["F"] + 2.5)
            cmd.append(",".join(str(int(t * FPS)) for t in ts))
        r = subprocess.run(cmd, capture_output=True, text=True)
        print(v["id"], r.stdout.strip(), r.stderr.strip()[-400:])
        html.unlink()
        if prova or r.returncode: continue
        out = QUI / f"{v['id']}_tiktok_v2.mp4"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", str(fr / "f%05d.jpg"),
                        "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo", "-shortest", "-c:v", "libx264", "-preset", "slow", "-crf", "18",
                        "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", str(out)], check=True)
        shutil.rmtree(fr); print("  ->", out.name, f"{out.stat().st_size / 1e6:.1f} MB")


if __name__ == "__main__":
    main()
