# Genera le slide 1080x1920 dei video TikTok Signum, Affirm, Nifert (25/11/2026).
# Stile: foto del prodotto sfocata a tutto schermo + prodotto scontornato, logo ufficiale
# direttamente sullo sfondo con numero slide in verde (come i video del 24/11).
# Uso: python3 genera.py  -> scrive html/<prodotto>.html; poi node rendi.js
import json, os, base64, sys
IG = 'ig' in sys.argv  # python3 genera.py ig -> carosello Instagram 1080x1350 in html/<prodotto>_ig.html
QUI = os.path.dirname(os.path.abspath(__file__))
KIT = os.path.join(QUI, '..', '..', 'kit')
def b64(p):
    return 'data:image/%s;base64,' % ('png' if p.endswith('png') else 'jpeg') + base64.b64encode(open(p, 'rb').read()).decode()

FITO = "Usare i prodotti fitosanitari con precauzione. Prima dell'uso leggere sempre l'etichetta e le informazioni sul prodotto. Vendita ai possessori di patentino."
CONC = "Prima dell'uso leggere sempre l'etichetta del prodotto."

CSS = """
@font-face{font-family:P;src:url(@@F@@/Poppins-Regular.ttf);font-weight:400}
@font-face{font-family:P;src:url(@@F@@/Poppins-Medium.ttf);font-weight:500}
@font-face{font-family:P;src:url(@@F@@/Poppins-Bold.ttf);font-weight:700}
*{margin:0;padding:0;box-sizing:border-box}
body{background:#000;font-family:P,sans-serif}
.s{width:1080px;height:1920px;position:relative;overflow:hidden;color:#fff}
.bg{position:absolute;inset:-80px;width:calc(100% + 160px);height:calc(100% + 160px);object-fit:cover;filter:blur(38px) brightness(.55) saturate(1.1)}
.ov{position:absolute;inset:0;background:linear-gradient(180deg,rgba(8,30,16,.55) 0%,rgba(8,30,16,.25) 35%,rgba(6,24,12,.75) 70%,rgba(4,18,9,.95) 100%)}
.top{position:absolute;top:64px;left:64px;right:64px;display:flex;justify-content:space-between;align-items:center}
.tag{background:#1B9A4B;color:#fff;font-weight:700;font-size:28px;letter-spacing:2px;padding:14px 30px;border-radius:40px;text-transform:uppercase}
.lg{display:flex;align-items:center;gap:18px}.lg img{width:180px}.lg span{color:#2fc26a;font-weight:700;font-size:34px}
.c{position:absolute;top:190px;left:64px;right:64px;bottom:150px;display:flex;flex-direction:column}
h1{font-size:96px;line-height:1.06;font-weight:700;letter-spacing:-1.5px}
h1 em{font-style:normal;color:#3ad17a}
.sub{font-size:44px;font-weight:500;line-height:1.3;margin-top:34px}
.sub b{color:#3ad17a}
.prod{position:absolute;left:50%;transform:translateX(-50%);filter:drop-shadow(0 30px 50px rgba(0,0,0,.6))}
.btn{position:absolute;left:64px;bottom:150px;background:#fff;color:#0f3d22;font-weight:700;font-size:38px;padding:22px 40px;border-radius:50px}
.cards{display:flex;flex-direction:column;gap:26px;margin-top:50px}
.card{background:rgba(10,28,16,.82);border:2px solid rgba(255,255,255,.12);border-radius:30px;padding:34px 38px;display:flex;gap:28px;align-items:flex-start}
.card.w{background:rgba(255,255,255,.95);color:#13301e;border:none}
.ic{font-size:52px;line-height:1;min-width:60px}
.card h3{font-size:42px;font-weight:700;line-height:1.2}
.card p{font-size:35px;line-height:1.38;margin-top:8px;opacity:.92}
.card .g{color:#2fc26a;font-weight:700}
.card.w .g{color:#1B9A4B}
.cta{margin-top:30px;background:#1B9A4B;border-radius:28px;padding:32px 38px;font-size:38px;font-weight:700;line-height:1.3}
.foot{position:absolute;left:64px;right:64px;bottom:60px;font-size:22px;line-height:1.4;opacity:.75}
.dose{margin-top:44px;background:#fff;color:#13301e;border-radius:30px;padding:34px 40px}
.dose .k{font-size:28px;font-weight:700;letter-spacing:2px;color:#1B9A4B;text-transform:uppercase}
.dose .v{font-size:76px;font-weight:700;line-height:1.1;margin-top:6px}
.dose .n{font-size:34px;line-height:1.35;margin-top:8px}
"""

def slide(p, i, n, body, foto=None):
    return f'''<div class="s"><img class="bg" src="{p['bgsrc']}"><div class="ov"></div>
<div class="top"><div class="tag">{body['tag']}</div><div class="lg"><img src="{LOGO}"><span>{i}/{n}</span></div></div>
<div class="c">{body['html']}</div>{foto or ''}<div class="foot">{p['foot']}</div></div>'''

def cards(lst, white=False):
    return '<div class="cards">' + ''.join(
        f'<div class="card{" w" if white else ""}"><div class="ic">{ic}</div><div><h3>{h}</h3><p>{t}</p></div></div>' for ic, h, t in lst) + '</div>'

IGCSS = """
.s{height:1350px}.top{top:48px;left:56px;right:56px}.tag{font-size:25px;padding:12px 26px}.lg img{width:170px}.lg span{font-size:32px}
.c{top:150px;left:56px;right:56px;bottom:100px}h1{font-size:84px}.sub{font-size:39px;margin-top:24px}
.btn{left:56px;bottom:96px;font-size:32px;padding:18px 34px}.cards{gap:20px;margin-top:34px}
.card{padding:28px 32px;gap:24px;border-radius:26px}.ic{font-size:46px;min-width:52px}.card h3{font-size:38px}.card p{font-size:32px;margin-top:6px}
.cta{margin-top:24px;padding:26px 32px;font-size:34px}.foot{left:56px;right:56px;bottom:36px;font-size:20px}
.dose{margin-top:32px;padding:26px 34px}.dose .k{font-size:24px}.dose .v{font-size:66px}.dose .n{font-size:30px}
"""
LOGO = b64(os.path.join(KIT, 'assets', 'logo_s4.png'))
dati = json.load(open(os.path.join(QUI, 'contenuti.json'), encoding='utf8'))
os.makedirs(os.path.join(QUI, 'html'), exist_ok=True)
for key, p in dati.items():
    p['bgsrc'] = b64(os.path.join(QUI, '..', '..', 'foto_originali', p['bg']))
    p['foot'] = FITO if p['fito'] else CONC
    prod = b64(os.path.join(KIT, 'assets', 'foto', key + '.png'))
    S = p['slide']; n = len(S); out = []
    for i, s in enumerate(S, 1):
        h = f'<h1>{s["titolo"]}</h1>'
        foto = None
        if s.get('sub'): h += f'<div class="sub">{s["sub"]}</div>'
        if s.get('dose'):
            d = s['dose']; h += f'<div class="dose"><div class="k">{d["k"]}</div><div class="v">{d["v"]}</div><div class="n">{d["n"]}</div></div>'
        if s.get('cards'): h += cards(s['cards'], s.get('white', False))
        if s.get('cta'): h += f'<div class="cta">{s["cta"]}</div>'
        if s.get('foto'):
            f = s['foto']
            t, hh = (f['top'] * 0.72 - 10, f['h'] * 0.72) if IG else (f['top'], f['h'])
            foto = f'<img class="prod" src="{prod}" style="top:{t}px;height:{hh}px">'
            if s.get('btn'): foto += f'<div class="btn">{s["btn"]}</div>'
        out.append(slide(p, i, n, {'tag': s['tag'], 'html': h}, foto))
    if IG: css_extra = IGCSS
    else: css_extra = ''
    css = css_extra and CSS + css_extra or CSS
    css = css.replace("@@F@@", 'file://' + os.path.abspath(os.path.join(KIT, 'fonts')))
    open(os.path.join(QUI, 'html', key + ('_ig' if IG else '') + '.html'), 'w', encoding='utf8').write(
        f'<!doctype html><html><head><meta charset="utf-8"><style>{css}</style></head><body>{"".join(out)}</body></html>')
    print(key, n, 'slide')
