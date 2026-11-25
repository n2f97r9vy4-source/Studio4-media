#!/usr/bin/env python3
"""Protocollo insetti orticole (distillato di legno + Praesidium + Sap-One K+): TikTok 9:16 e Instagram 3:4, stile kit Studio 4."""
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

KIT = Path("/home/user/studio4-media/kit")
HERE = Path(__file__).resolve().parent
FOTO = (HERE / "distillato_pulito.png").as_uri()
LOGO = (KIT / "assets/logo_s4.png").as_uri()
FONT = "".join(
    f"@font-face{{font-family:P;src:url({(KIT/'fonts'/f).as_uri()});font-weight:{w}}}"
    for f, w in [("Poppins-Regular.ttf", 400), ("Poppins-Medium.ttf", 500), ("Poppins-Bold.ttf", 700)])

ACC, DARK, BG1, BG2, OR = "#1B9A4B", "#0E3B22", "#F2F8F3", "#D6EBDC", "#DF502E"

def html(fmt):
    tt = fmt == "tiktok"
    H = 1920 if tt else 1440
    s = 0.88 if tt else 0.72          # scala dei testi
    def px(v): return f"{v*s:.0f}px"
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{FONT}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{width:1080px;height:{H}px;overflow:hidden}}
.s{{width:1080px;height:{H}px;position:relative;overflow:hidden;font-family:P,'Noto Color Emoji',sans-serif;color:{DARK};
 background:linear-gradient(160deg,{BG1} 0%,{BG2} 100%)}}
.tag{{position:absolute;top:{px(70)};left:70px;font-size:{px(25)};font-weight:700;letter-spacing:3px;color:{ACC};text-transform:uppercase}}
.dot{{display:inline-block;width:14px;height:14px;border-radius:50%;background:{ACC};margin-right:14px}}
.logo{{position:absolute;right:70px;top:{px(58)};width:{px(180)}}}
.w{{position:absolute;left:70px;right:70px;top:{px(140)};bottom:{px(46)};display:flex;flex-direction:column;gap:{px(22)}}}
h1{{font-size:{px(96)};line-height:.98;font-weight:700;letter-spacing:-3px}}
h1 em{{font-style:normal;color:{OR}}}
.sub{{font-size:{px(38)};font-weight:500;line-height:1.25;margin-top:{px(12)}}}
.sub b{{color:{ACC}}}
.bugs{{display:flex;gap:{px(14)};flex-wrap:wrap}}
.bug{{background:{OR};color:#fff;border-radius:999px;padding:{px(12)} {px(26)};font-size:{px(32)};font-weight:700;display:flex;align-items:center;gap:10px;
 box-shadow:0 10px 24px rgba(223,80,46,.25)}}
.tl{{position:relative;display:flex;flex-direction:column;gap:{px(20)};padding-left:{px(92)}}}
.tl:before{{content:"";position:absolute;left:{px(34)};top:{px(30)};bottom:{px(60)};width:8px;border-radius:4px;
 background:linear-gradient({ACC} 0 30%,{OR} 30% 72%,{ACC} 72%)}}
.ph{{position:relative;background:#fff;border-radius:30px;padding:{px(26)} {px(32)};box-shadow:0 14px 40px rgba(0,0,0,.09)}}
.n{{position:absolute;left:{px(-92)};top:{px(18)};width:{px(76)};height:{px(76)};border-radius:50%;background:{ACC};color:#fff;
 font-size:{px(40)};font-weight:700;display:flex;align-items:center;justify-content:center;border:6px solid {BG1}}}
.k{{font-size:{px(23)};font-weight:700;letter-spacing:2.5px;text-transform:uppercase;color:{ACC}}}
.p{{font-size:{px(44)};font-weight:700;line-height:1.1;margin-top:{px(6)}}}
.d{{font-size:{px(32)};font-weight:500;line-height:1.3;margin-top:{px(6)}}}
.d b{{color:{ACC}}}
.ph1{{padding-right:{px(260)}}}
.ph1 img{{position:absolute;right:{px(14)};bottom:{px(14)};height:{px(300)};filter:drop-shadow(0 22px 22px rgba(0,0,0,.28))}}
.ph2{{background:{DARK};color:#fff}}
.ph2 .n{{background:{OR}}}
.ph2 .k{{color:#FFB49F}}
.ph2 .d b{{color:#8EE0AC}}
.giorni{{display:flex;gap:{px(14)};margin-top:{px(18)}}}
.g{{flex:1;border-radius:20px;background:rgba(255,255,255,.09);padding:{px(14)} {px(16)};font-size:{px(25)};font-weight:500;line-height:1.25}}
.g .gg{{font-size:{px(22)};font-weight:700;letter-spacing:2px;color:#FFB49F;display:block}}
.g i{{font-style:normal;color:#8EE0AC;font-weight:700}}
.row{{display:flex;gap:{px(18)}}}
.box{{flex:1;background:#fff;border-radius:26px;padding:{px(20)} {px(26)};box-shadow:0 14px 40px rgba(0,0,0,.07);font-size:{px(28)};font-weight:500;line-height:1.3}}
.box .k{{font-size:{px(21)};margin-bottom:{px(6)}}}
.box b{{font-weight:700}}
.lo{{background:{ACC};color:#fff;border-radius:30px;padding:{px(24)} {px(32)};font-size:{px(29)};line-height:1.33;font-weight:500}}
.lo b{{font-size:{px(34)};font-weight:700;display:block;margin-bottom:{px(6)}}}
.cta{{font-size:{px(30)};font-weight:700;line-height:1.3;color:{ACC}}}
.cta span{{color:{DARK};font-weight:500}}
.sp{{flex:1}}
.disc{{font-size:{px(20)};line-height:1.4;font-weight:500;opacity:.72;border-top:2px solid rgba(0,0,0,.15);padding-top:{px(14)}}}
</style></head><body><div class="s">
<div class="tag"><span class="dot"></span>Orticole · difesa</div>
<img class="logo" src="{LOGO}">
<div class="w">
 <div>
  <h1>Insetti sulla coltura?<br><em>Lo schema in 3 fasi.</em></h1>
  <div class="sub">Prevenire, allontanare, ripartire: <b>dal trapianto alla raccolta</b>.</div>
 </div>
 <div class="bugs"><div class="bug">Afidi</div><div class="bug">Acari</div><div class="bug">Cocciniglie</div><div class="bug">Lepidotteri</div></div>
 <div class="tl">
  <div class="ph ph1"><div class="n">1</div>
   <div class="k">Prevenzione · sempre</div>
   <div class="p">Distillato di legno</div>
   <div class="d"><b>250 ml/hl</b> ogni <b>5–7 giorni</b>, dal trapianto alla raccolta: la coltura diventa meno gradita agli insetti.</div>
   <img src="{FOTO}">
  </div>
  <div class="ph ph2"><div class="n">2</div>
   <div class="k">Allontanamento · insetto già presente</div>
   <div class="p">Praesidium <span style="font-weight:500">+ Sap-One K+</span></div>
   <div class="d">Praesidium <b>600 ml/hl</b>, 2–3 interventi, <b>uno ogni 3 giorni</b>.</div>
   <div class="giorni">
    <div class="g"><span class="gg">GIORNO 0</span>Praesidium</div>
    <div class="g"><span class="gg">GIORNO 3</span>Praesidium <i>+ Sap-One K+ 400 ml/hl</i></div>
    <div class="g"><span class="gg">GIORNO 6</span>Praesidium <i>+ Sap-One K+</i> se serve</div>
   </div>
  </div>
  <div class="ph"><div class="n">3</div>
   <div class="k">Ripresa</div>
   <div class="p">Si torna al distillato</div>
   <div class="d"><b>250 ml/hl</b> ogni <b>5–7 giorni</b>, fino alla raccolta.</div>
  </div>
 </div>
 <div class="row">
  <div class="box"><div class="k">Prima di tutto</div>Bagnetto radici al trapianto: distillato <b>300 ml/hl</b>. In fertirrigazione <b>5 L/ha ogni 14 giorni</b>.</div>
  <div class="box"><div class="k" style="color:{OR}">Attenzione</div>Sap-One K+ <b>non</b> con insetti ausiliari in serra. Interventi nelle ore più calde.</div>
 </div>
 <div class="lo"><b>Lo sapevi? Il sapone lavora solo finché è bagnato.</b>Il sapone di potassio agisce per contatto: quando la goccia asciuga ha finito. Con acqua dura, calcio e magnesio ne bloccano una parte. Bagna bene la pagina sotto della foglia, dove stanno afidi e acari.</div>
 <div class="cta">Per lo schema sulla tua coltura passa al banco di Studio 4, a Vittoria. <span>Corroboranti e sapone: allontanano, non sono insetticidi.</span></div>
 <div class="sp"></div>
 <div class="disc">Usare i prodotti fitosanitari con precauzione. Prima dell'uso leggere sempre l'etichetta e le informazioni sul prodotto. Vendita ai possessori di patentino.</div>
</div></div></body></html>"""

def main():
    out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path="/opt/pw-browsers/chromium-1243/chrome-linux64/chrome")
        for fmt, H, name in [("tiktok", 1920, "protocollo_insetti_tiktok_9x16.png"), ("instagram", 1440, "protocollo_insetti_instagram_3x4.png")]:
            f = HERE / f"_{fmt}.html"; f.write_text(html(fmt), encoding="utf-8")
            pg = b.new_page(viewport={"width": 1080, "height": H}, device_scale_factor=2)
            pg.goto(f.as_uri()); pg.wait_for_timeout(400)
            ov = pg.evaluate("(()=>{const w=document.querySelector('.w');return w.scrollHeight-w.clientHeight})()")
            print(fmt, "overflow px:", ov)
            pg.screenshot(path=str(out / name)); pg.close()
        b.close()

main()
