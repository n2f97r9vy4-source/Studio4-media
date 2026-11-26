# Video "Chi blocca chi" (antagonismi tra nutrienti), 26/11/2026

Rifatto in italiano da un video TikTok in spagnolo mandato da Valerio. Personaggi ridisegnati da zero (SVG), sfondo e logo del kit Studio 4.
Voce sintetica italiana Kokoro (im_nicola, if_sara) con tono alzato per i personaggi: nessuna clonazione della voce originale.

Rifarlo:
1. `python3 tts.py <cartella con kokoro.onnx e voices.bin>` (modelli: github.com/thewh1teagle/kokoro-onnx, release model-files-v1.0; `pip install kokoro-onnx`)
2. `python3 timeline.py` (unisce le voci, velocità 1,08, crea timeline.json e voce.wav)
3. copiare qui `kit/assets/logo_s4.png`, `kit/fonts/Poppins-Bold.ttf`, `Poppins-Medium.ttf`, poi `node frames.js` (Playwright, 30 fps, ~2,5 min) → video.mp4
Trascrizione dell'originale: faster-whisper small (pacchetti npm @skillninja/shortmovie-telop-model-p0..p3, perché Hugging Face è bloccato dal container).
