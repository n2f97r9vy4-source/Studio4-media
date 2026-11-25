#!/usr/bin/env python3
"""Caroselli TikTok nello stile dei video già pubblicati (QZyme, Razormin, Cidely, Turbo Root):
slide del kit 1080x1350 (kit/s4kit.py: logo in alto a destra, senza cornice) al centro di un fondo 1080x1920
fatto dalla stessa slide sfocata. Uscite: <prodotto>/s1..sN.png (9:16) e, se "video": true, <prodotto>_tiktok.mp4.
Uso: NODE_PATH=$(npm root -g) python3 genera_kit.py
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

DISC_FITO = k.DISC
IG = QUI / "instagram_kit"; IG.mkdir(exist_ok=True)
jsf = QUI / ".js_fit.txt"; jsf.write_text(k.JS_FIT)
for c in json.loads((QUI / "caroselli_kit.json").read_text(encoding="utf-8")):
    k.DISC = c.get("disc") or (DISC_FITO if c.get("fito", True) else "Prima dell'uso leggere sempre l'etichetta del prodotto.")
    out = QUI / ("kit_" + c["id"]); out.mkdir(exist_ok=True)
    for f in out.glob("*.png"): f.unlink()
    html = QUI / f".{c['id']}.html"; html.write_text(k.html_carosello(c), encoding="utf-8")
    r = subprocess.run(["node", str(QUI / "rendi_kit.js"), str(html), str(jsf), str(out)], capture_output=True, text=True)
    print(c["id"], r.stdout.strip(), r.stderr.strip()[-300:]); html.unlink()
    for i in range(len(c["slide"])):
        kp = out / f"k{i+1}.png"; nove_sedicesimi(kp, out / f"s{i+1}.png")
        Image.open(kp).convert("RGB").save(IG / f"{c['id']}_s{i+1}.jpg", quality=92); kp.unlink()
    if c.get("video"):
        subprocess.run([str(QUI / "video.sh"), str(out), str(QUI / f"{c['id']}_tiktok.mp4")], check=True)
jsf.unlink()
