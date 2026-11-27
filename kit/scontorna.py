#!/usr/bin/env python3
"""STUDIO 4 MEDIA — scontorno pulito di una foto prodotto fatta al banco (flaconi, taniche, sacchi).

Parte SEMPRE dalla foto originale (foto_originali/...) e scrive kit/assets/foto/<nome>.png, pronto per kit/s4kit.py.
Non usa rettangoli né maschere a mano: il contorno lo trova il modello ISNet (lo stesso di rembg), poi qui si rifinisce:
  1. riquadro attorno al prodotto (esclude banco, scaffali, altri prodotti);
  2. se richiesto, raddrizza il prodotto (solo rotazione, mai deformazioni);
  3. maschera ISNet (media tra immagine normale e specchiata);
  4. bordo netto e liscio: contorno ricalcolato a 4x, stretto di una frazione di pixel, antialias vero;
  5. colore del bordo ripulito: i pixel di bordo prendono il colore del prodotto, non quello dello sfondo della foto
     (niente aloni scuri o chiari quando il ritaglio va su un altro fondo);
  6. ritocchi facoltativi di piccoli segni (polvere, graffi) che cadono proprio sul bordo;
  7. buchi facoltativi (--buco): il vuoto della maniglia di una tanica, dove si vede il magazzino dietro. Sulla foto
     intera il modello lo lascia pieno; guardando solo la maniglia lo riconosce, e lì il ritaglio diventa trasparente.

Serve solo Pillow, numpy e onnxruntime (già presenti nel container). Il modello (circa 170 MB) si scarica da solo
la prima volta in ~/.cache/studio4/ e NON va messo nel repository.

Uso:
  python3 kit/scontorna.py foto_originali/juvinal-gold_2026-11-25.jpg juvinal \\
      --riquadro 330,760,1140,2470 --raddrizza --ritocco 952,1132,974,1166 --anteprima /tmp/anteprima

  --riquadro x0,y0,x1,y1   riquadro attorno al prodotto, in pixel della foto originale, con almeno 40 px di margine
  --raddrizza              raddrizza il prodotto sull'asse verticale (per flaconi e taniche simmetrici)
  --angolo G               oppure rotazione scelta a mano, in gradi (positivo = senso antiorario)
  --ritocco x0,y0,x1,y1    riquadro (pixel della foto originale) dove togliere un segno scuro sul bordo; ripetibile
  --buco x0,y0,x1,y1       riquadro (pixel della foto originale) attorno al vuoto di una maniglia, con un po' di plastica
                           su tutti i lati: il vuoto diventa trasparente; ripetibile
  --stringi PX             di quanto stringere il contorno, in pixel (predefinito 0.75)
  --anteprima PREFISSO     salva anche PREFISSO_chiaro.png, _nero.png, _magenta.png per controllare gli orli
"""
import argparse
import math
import urllib.request
from pathlib import Path

import numpy as np
import onnxruntime as ort
from PIL import Image, ImageFilter, ImageOps

KIT = Path(__file__).resolve().parent
REPO = KIT.parent
MODELLO_URL = "https://github.com/danielgatis/rembg/releases/download/v0.0.0/isnet-general-use.onnx"
MODELLO = Path.home() / ".cache" / "studio4" / "isnet-general-use.onnx"
S = 4  # sovracampionamento per il contorno


def sessione(percorso):
    percorso = Path(percorso)
    if not percorso.exists():
        percorso.parent.mkdir(parents=True, exist_ok=True)
        print("scarico il modello ISNet (circa 170 MB)...")
        urllib.request.urlretrieve(MODELLO_URL, percorso)
    return ort.InferenceSession(str(percorso), providers=["CPUExecutionProvider"])


def maschera_isnet(sess, img):
    """Maschera 0..1 (float32) grande come img: media tra immagine normale e specchiata."""
    nome = sess.get_inputs()[0].name

    def una(im):
        a = np.asarray(im.resize((1024, 1024), Image.Resampling.LANCZOS)).astype(np.float32)
        a = a / max(float(a.max()), 1e-6) - 0.5
        return sess.run(None, {nome: a.transpose(2, 0, 1)[None]})[0][0, 0]

    o = (una(img) + una(ImageOps.mirror(img))[:, ::-1]) / 2
    o = (o - o.min()) / max(float(o.max() - o.min()), 1e-6)
    m = Image.fromarray((o * 255).astype(np.uint8), "L").resize(img.size, Image.Resampling.BICUBIC)
    return np.asarray(m).astype(np.float32) / 255


def solo_il_prodotto(m):
    """Tiene solo la macchia più grande della maschera (toglie eventuali isole dello sfondo)."""
    b = m >= 0.5
    H, W = b.shape
    etich = np.zeros((H, W), np.int32)
    n = 0
    aree = {}
    for y0, x0 in zip(*np.nonzero(b[::8, ::8])):  # semi su griglia rada: basta per trovare le macchie grandi
        y0, x0 = int(y0) * 8, int(x0) * 8
        if etich[y0, x0]:
            continue
        n += 1
        pila = [(y0, x0)]
        etich[y0, x0] = n
        area = 0
        while pila:
            y, x = pila.pop()
            area += 1
            for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                yy, xx = y + dy, x + dx
                if 0 <= yy < H and 0 <= xx < W and b[yy, xx] and not etich[yy, xx]:
                    etich[yy, xx] = n
                    pila.append((yy, xx))
        aree[n] = area
    if not aree:
        raise SystemExit("il modello non ha trovato nessun prodotto nel riquadro")
    grande = Image.fromarray((etich == max(aree, key=aree.get)).astype(np.uint8) * 255, "L")
    vicino = np.asarray(grande.filter(ImageFilter.MaxFilter(17))) > 0   # tiene anche la sfumatura del bordo
    return np.where(vicino, m, 0.0).astype(np.float32)


def buco_maniglia(sess, ritaglio, zona, allarga=2):
    """Maschera booleana (grande come il ritaglio) del vuoto di una maniglia dentro 'zona' (booleana).
    Sul solo riquadro della maniglia il modello segna come soggetto proprio il vuoto: si tiene la macchia che
    contiene il centro del riquadro e la si allarga di 'allarga' pixel, così non resta un filo di sfondo sul bordo."""
    ys, xs = np.nonzero(zona)
    x0, x1, y0, y1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
    d = maschera_isnet(sess, ritaglio.crop((x0, y0, x1, y1)))
    b = d >= 0.5
    cy, cx = (y1 - y0) // 2, (x1 - x0) // 2
    if not b[cy, cx]:
        raise SystemExit("--buco: al centro del riquadro il modello non vede un vuoto; controlla il riquadro")
    vista = np.zeros_like(b)
    pila = [(cy, cx)]
    vista[cy, cx] = True
    H, W = b.shape
    while pila:
        y, x = pila.pop()
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            yy, xx = y + dy, x + dx
            if 0 <= yy < H and 0 <= xx < W and b[yy, xx] and not vista[yy, xx]:
                vista[yy, xx] = True
                pila.append((yy, xx))
    if vista[0].any() or vista[-1].any() or vista[:, 0].any() or vista[:, -1].any():
        raise SystemExit("--buco: il vuoto trovato tocca il bordo del riquadro; allarga il riquadro sulla plastica")
    if allarga > 0:
        vista = np.asarray(Image.fromarray(vista.astype(np.uint8) * 255, "L").filter(ImageFilter.MaxFilter(2 * allarga + 1))) > 0
    out = np.zeros(zona.shape, bool)
    out[y0:y1, x0:x1] = vista
    return out


def asse(m):
    """Pendenza del prodotto (dx/dy): media delle pendenze dei due fianchi, misurate nel tratto dritto
    (dal 30% all'80% dell'altezza). Per flaconi e taniche con i fianchi verticali."""
    b = m >= 0.5
    righe = np.nonzero(b.any(1))[0]
    y0, h = righe[0], righe[-1] - righe[0]
    ys = np.arange(int(y0 + 0.30 * h), int(y0 + 0.80 * h))
    sx = b[ys].argmax(1)
    dx = b.shape[1] - 1 - b[ys, ::-1].argmax(1)
    return float(np.polyfit(ys, sx, 1)[0] + np.polyfit(ys, dx, 1)[0]) / 2


def erodi(b, r):
    """Erosione con disco di raggio r (pixel) su una matrice booleana."""
    if r <= 0:
        return b
    out = b.copy()
    R = int(math.ceil(r))
    H, W = b.shape
    for dy in range(-R, R + 1):
        for dx in range(-R, R + 1):
            if (dy or dx) and dy * dy + dx * dx <= r * r + 0.5:
                sh = np.zeros_like(b)
                sh[max(dy, 0):H + min(dy, 0), max(dx, 0):W + min(dx, 0)] = \
                    b[max(-dy, 0):H + min(-dy, 0), max(-dx, 0):W + min(-dx, 0)]
                out &= sh
    return out


def contorno_netto(m, stringi):
    """Dalla maschera morbida del modello a un'alfa con bordo liscio e netto (antialias di circa 1 px)."""
    H, W = m.shape
    su = Image.fromarray((m * 255).astype(np.uint8), "L").resize((W * S, H * S), Image.Resampling.BICUBIC)
    su = su.filter(ImageFilter.GaussianBlur(S * 0.9))            # liscia le seghettature del modello
    b = erodi(np.asarray(su) >= 128, stringi * S)                # stringe di 'stringi' pixel
    a = Image.fromarray(b.astype(np.uint8) * 255, "L").resize((W, H), Image.Resampling.BOX)
    a = a.filter(ImageFilter.GaussianBlur(0.55))                 # bordo morbido quanto la foto, non "a forbice"
    return np.asarray(a).astype(np.float32) / 255


def stendi_colore(rgb, noto, serve, giri=80):
    """Allarga i colori dei pixel 'noti' verso quelli ignoti (media dei vicini noti), un pixel a giro,
    finché tutti i pixel che servono (quelli visibili e i ritocchi) hanno un colore."""
    rgb = rgb.astype(np.float32).copy()
    noto = noto.copy()
    H, W = noto.shape
    for _ in range(giri):
        if noto[serve].all():
            break
        acc = np.zeros_like(rgb)
        cnt = np.zeros((H, W), np.float32)
        k = noto.astype(np.float32)
        pesato = rgb * k[..., None]
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                if not (dy or dx):
                    continue
                w = 1.0 if (dy == 0 or dx == 0) else 0.7
                ys, yd = slice(max(-dy, 0), H + min(-dy, 0)), slice(max(dy, 0), H + min(dy, 0))
                xs, xd = slice(max(-dx, 0), W + min(-dx, 0)), slice(max(dx, 0), W + min(dx, 0))
                acc[yd, xd] += w * pesato[ys, xs]
                cnt[yd, xd] += w * k[ys, xs]
        nuovi = (~noto) & (cnt > 0)
        rgb[nuovi] = acc[nuovi] / cnt[nuovi][:, None]
        noto |= nuovi
    return rgb, noto


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("foto")
    ap.add_argument("nome")
    ap.add_argument("--riquadro", required=True)
    ap.add_argument("--raddrizza", action="store_true")
    ap.add_argument("--angolo", type=float, default=None)
    ap.add_argument("--ritocco", action="append", default=[])
    ap.add_argument("--buco", action="append", default=[])
    ap.add_argument("--stringi", type=float, default=0.75)
    ap.add_argument("--anteprima", default=None)
    ap.add_argument("--modello", default=str(MODELLO))
    ap.add_argument("--uscita", default=None, help="file PNG di uscita (predefinito kit/assets/foto/<nome>.png)")
    a = ap.parse_args()

    x0, y0, x1, y1 = map(int, a.riquadro.split(","))
    foto = ImageOps.exif_transpose(Image.open(a.foto)).convert("RGB")
    sess = sessione(a.modello)

    # 1-2. riquadro ed eventuale raddrizzamento (rotazione attorno al centro del prodotto, sulla foto intera)
    angolo = a.angolo or 0.0
    centro = ((x0 + x1) / 2, (y0 + y1) / 2)
    if a.raddrizza and a.angolo is None:
        m0 = solo_il_prodotto(maschera_isnet(sess, foto.crop((x0, y0, x1, y1))))
        b0 = m0 >= 0.5
        ys, xs = np.nonzero(b0)
        centro = (x0 + (xs.min() + xs.max()) / 2, y0 + (ys.min() + ys.max()) / 2)
        # asse con pendenza p (il prodotto pende): per raddrizzarlo l'immagine ruota di -atan(p) (senso orario se p>0)
        angolo = -math.degrees(math.atan(asse(m0)))
    if abs(angolo) > 0.05:
        foto = foto.rotate(angolo, resample=Image.Resampling.BICUBIC, center=centro)
    ritaglio = foto.crop((x0, y0, x1, y1))
    rgb = np.asarray(ritaglio).astype(np.float32)
    H, W = rgb.shape[:2]

    # posizione di ogni pixel del ritaglio nella foto originale (inverso della rotazione di PIL)
    th = math.radians(angolo)
    yy, xx = np.mgrid[0:H, 0:W]
    dx, dy = xx + x0 - centro[0], yy + y0 - centro[1]
    ox = centro[0] + math.cos(th) * dx - math.sin(th) * dy
    oy = centro[1] + math.sin(th) * dx + math.cos(th) * dy

    def zona_di(r):
        rx0, ry0, rx1, ry1 = map(int, r.split(","))
        return (ox >= rx0) & (ox <= rx1) & (oy >= ry0) & (oy <= ry1)

    # 3-4. maschera e contorno (7: i vuoti delle maniglie escono dalla maschera prima di rifare il contorno)
    m = solo_il_prodotto(maschera_isnet(sess, ritaglio))
    for r in a.buco:
        m = np.where(buco_maniglia(sess, ritaglio, zona_di(r)), 0.0, m).astype(np.float32)
    alfa = contorno_netto(m, a.stringi)

    # 5-6. colore del bordo: noti = pixel sicuramente del prodotto (2 px dentro il contorno), meno i ritocchi
    noto = erodi(alfa >= 0.99, 1.0)
    for r in a.ritocco:
        zona = zona_di(r)
        lum = rgb @ np.array([0.299, 0.587, 0.114], np.float32)
        rif = np.median(lum[zona & noto]) if (zona & noto).any() else 255
        scuro = zona & (lum < rif - 9)
        # allarga di 1 px il segno, così si toglie anche la sua sfumatura
        sc = Image.fromarray(scuro.astype(np.uint8) * 255, "L").filter(ImageFilter.MaxFilter(3))
        noto &= ~(np.asarray(sc) > 0)
    visibile = Image.fromarray((alfa > 0).astype(np.uint8) * 255, "L").filter(ImageFilter.MaxFilter(7))
    pulito, steso = stendi_colore(rgb, noto, np.asarray(visibile) > 0)
    pulito[~steso] = 255
    out = np.dstack([np.clip(pulito, 0, 255), alfa * 255]).round().astype(np.uint8)
    # fuori dal prodotto: del tutto trasparente
    out[alfa <= 0.004, 3] = 0

    # ritaglio finale sul prodotto, con 6 px di aria
    ys, xs = np.nonzero(out[..., 3] > 0)
    bx0, by0 = max(xs.min() - 6, 0), max(ys.min() - 6, 0)
    bx1, by1 = min(xs.max() + 7, W), min(ys.max() + 7, H)
    png = Image.fromarray(out, "RGBA").crop((bx0, by0, bx1, by1))
    dst = Path(a.uscita) if a.uscita else KIT / "assets" / "foto" / f"{a.nome}.png"
    png.save(dst, optimize=True)
    print(f"{dst}  {png.size[0]}x{png.size[1]}  rotazione {angolo:+.2f} gradi")

    if a.anteprima:
        for nome, colore in (("chiaro", (250, 226, 222)), ("nero", (18, 18, 18)), ("magenta", (255, 0, 255))):
            bg = Image.new("RGB", png.size, colore)
            bg.paste(png, mask=png.getchannel("A"))
            bg.save(f"{a.anteprima}_{nome}.png")


if __name__ == "__main__":
    main()
