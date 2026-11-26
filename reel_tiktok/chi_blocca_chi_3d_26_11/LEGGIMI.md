# Serie "Chi blocca chi" in 3D (antagonismi tra nutrienti), 26/11/2026

Sei video da circa 16 secondi, uno per antagonismo: fosforo, potassio, ammonio, calcio, magnesio, zolfo.
Valerio aveva trovato la prima versione 2D (`../antagonismi_26_11/`) "troppo disegnata": questa è in vero 3D.

Schema di ogni video (correzione di Valerio sulla prima bozza 3D):
1. chi blocca si presenta e basta ("Sono il fosforo. Hai esagerato con me!"), senza elencare chi blocca;
2. ogni elemento bloccato dice "il fosforo mi blocca" e cosa succede nella pianta (il sintomo è colorato nei sottotitoli);
3. chiusura: "Prima di concimare, passa al banco di Studio 4."

Come è fatta, senza applicazioni a pagamento:
- scena 3D con three.js r170 (materiali PBR, ombre, occlusione ambientale, bloom), calcolata nel Chromium del container senza scheda grafica (SwiftShader);
- voci sintetiche italiane Kokoro NON alterate (Valerio le voleva "più naturali": niente cambio di tono): im_nicola per chi blocca, if_sara per il primo bloccato e la chiusura, misto im_nicola + em_alex per il secondo. Nessuna voce clonata;
- cornice Studio 4 (sfondo chiaro sfumato del kit, logo, titolo, sottotitoli) in HTML, unita al 3D con ffmpeg.
Nessuna musica: la aggiunge Valerio dall'app.

File:
- `videos.json`: testi dei 6 video (chi parla e cosa dice)
- `tts4.py`: voci, crea `aud/<id>.wav` e `aud/<id>.json` (tempi e movimento della bocca)
- `util.js`, `chars.js`, `stage.js`: geometrie, personaggi, scena e animazione
- `scene.html`: cornice Studio 4 + scena
- `render.js`, `compose.sh`, `one.sh`: fotogrammi e montaggio
- `out/`: video finali e didascalie

Rifarlo:
1. `pip install kokoro-onnx`; dalla release model-files-v1.0 di github.com/thewh1teagle/kokoro-onnx scaricare `kokoro-v1.0.onnx` (salvarlo come `kokoro-fp32.onnx`) e `voices-v1.0.bin` (come `voices.bin`), poi `python3 tts4.py <cartella modelli>`
2. copiare qui `build/three.module.js` e la cartella `examples/jsm` (come `jsm/`) dal pacchetto npm `three@0.170.0`, più `kit/assets/logo_s4.png`, `kit/fonts/Poppins-Bold.ttf` e `Poppins-Medium.ttf`
3. `bash one.sh 1_fosforo` (e così per gli altri): circa 11 minuti a video su 4 core senza scheda grafica; due video insieme vanno poco più veloci

Per cambiare una battuta: modificare `videos.json`, rifare il punto 1 e il punto 3 solo per quel video.
Prova veloce di un fotogramma: `MODE=stage node still.js 1_fosforo 2.0`.
