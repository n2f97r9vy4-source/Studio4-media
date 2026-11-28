#!/usr/bin/env python3
"""Ritaglio di un flacone singolo. Uso: python3 kit/ritaglia.py foto.jpg nome [x0,y0,x1,y1]
Salva kit/assets/foto/<nome>.png e /tmp/ref/<nome>_chk.png (controllo su fondo scuro)."""
import sys
from PIL import Image
import numpy as np
from rembg import new_session, remove
from scipy import ndimage as ndi
src = Image.open(sys.argv[1]).convert("RGB")
if len(sys.argv) > 3: src = src.crop(tuple(int(v) for v in sys.argv[3].split(",")))
s = new_session("isnet-general-use")
o = remove(src, session=s, alpha_matting=True, alpha_matting_foreground_threshold=240, alpha_matting_background_threshold=15, alpha_matting_erode_size=6)
a = np.array(o)[:, :, 3]
lab, n = ndi.label(a > 20); sz = ndi.sum(a > 20, lab, range(1, n + 1)); m = ndi.binary_fill_holes(lab == 1 + int(np.argmax(sz)))
arr = np.array(o); arr[:, :, 3] = np.where(m, a, 0); o = Image.fromarray(arr)
bb = o.getbbox(); o = o.crop((max(bb[0]-6, 0), max(bb[1]-6, 0), bb[2]+6, bb[3]+6))
o.save(f"kit/assets/foto/{sys.argv[2]}.png")
bg = Image.new("RGBA", o.size, (35, 35, 35, 255)); bg.alpha_composite(o); bg.convert("RGB").resize((o.width//2, o.height//2)).save(f"/tmp/ref/{sys.argv[2]}_chk.png")
print(o.size)
