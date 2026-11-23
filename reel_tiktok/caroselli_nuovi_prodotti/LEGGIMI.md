# Caroselli TikTok — 5 nuovi prodotti (23/11/2026, BOZZA da approvare da Valerio)

Stesso stile della versione finale di Topas/Oikos/Pergado: slide del kit con logo STUDIO 4 in alto a destra, senza cornice bianca, su fondo 9:16 fatto dalla stessa slide sfocata. **4 slide per prodotto**, l'ultima è "Lo sapevi?". La dose compare **una sola volta** (slide 2), mai nelle didascalie.

| Prodotto | Formato | File |
|---|---|---|
| Auxiger LG | video 9:16 muto, 15,8 s | `auxiger_tiktok.mp4`, slide `auxiger/s1–s4.png` |
| Fengib | video 9:16 muto, 15,8 s | `fengib_tiktok.mp4`, slide `fengib/s1–s4.png` |
| HiSense TRP | video 9:16 muto, 15,8 s | `hisense_tiktok.mp4`, slide `hisense/s1–s4.png` |
| Spray Dünger Global HD | carosello di foto 9:16 | `spraydunger/s1–s4.png` |
| Switch | carosello di foto 9:16 | `switch/s1–s4.png` |

Didascalie: `<prodotto>_didascalia.txt` (5 hashtag con #studio4srl; avvertenza fitosanitari tranne HiSense TRP, che non è un fitofarmaco).
Rigenerare: modificare `caroselli.json`, poi `NODE_PATH=$(npm root -g) python3 genera_kit.py` (Playwright per Node + ffmpeg). Video solo per le voci con `"video": true`.

## Dosi (controllate sul Prontuario `src/prodotti.jsonl.txt` e sulle etichette in `pdf/`)
- **Auxiger LG** (reg. 12114): 50–70 ml/hl fogliare a ogni fioritura, carenza 7 giorni, da solo — etichetta D.D. 16/09/2026.
- **Fengib** (reg. 14582): pomodoro 30–40 ml/hl solo sui grappoli fiorali a inizio fioritura, carenza 20 giorni — etichetta D.D. 25/05/2026. (Melanzana e peperone 30–50 ml/hl: non scritto per non mettere una seconda dose.)
- **HiSense TRP** (biostimolante, nessuna registrazione): 1–2 kg/ha al terreno prima del trapianto o in fertirrigazione — etichetta (foto del banco 07/11/2026, Rev 06.11.23).
- **Spray Dünger Global HD** (reg. 10439): pomodoro e melanzana 0,75–1 l/ha in manichetta, solo in serra, 2–3 applicazioni, carenza 14 giorni — etichetta valida dal 28/06/2026. (Fogliare 75–100 ml/hl una sola volta: citato senza numero.)
- **Switch** (reg. 9578): 60–80 g/hl, ogni 10–14 giorni, massimo 3, carenza 3 giorni — etichetta D.D. 07/05/2026.
Le tre dosi nuove sono state aggiunte in `kit/prodotti.json` (fengib, hisense, spraydunger) così il controllo di `kit/s4kit.py` le accetta; controllo passato su tutti e 5 (nessun produttore, niente parole assolute, niente prezzi).

## Cosa NON viene dall'etichetta (nozioni generali, da confermare)
1. Auxiger: "di solito il segnale per crescere lo danno i semi", "col freddo polline scarso e bombi lenti" (fisiologia generale). La partenocarpia invece è in etichetta.
2. Fengib: storia della gibberellina (malattia del riso in Giappone, fungo *Gibberella*), produzione per fermentazione: storia della botanica, non in etichetta.
3. HiSense TRP: "al trapianto le radici nuove si colonizzano prima" e tutta la slide "Lo sapevi?" (micorrize, fosforo, zuccheri): microbiologia del suolo generale.
4. Spray Dünger: i tre momenti sono in etichetta; le spiegazioni brevi di ogni momento e "col caldo la foglia chiude i pori" sono nozioni generali.
5. Switch: slide 3 "Da dove entra" (umidità, petali, ferite, aria ferma) e l'origine del fludioxonil (copiato da una sostanza naturale dei batteri del terreno, la pirrolnitrina) sono nozioni generali; "selettivo su insetti e acari utili" e "partire all'instaurarsi delle condizioni favorevoli" sono in etichetta.

## Da sapere
- Etichetta Spray Dünger 2026: indicazioni H360Df (può nuocere al feto) e "PERICOLO", mentre il catalogo del Ministero lo dà "esente da classificazione". Non scritto nel post.
- Composizione Fengib: in etichetta il secondo ormone si chiama "fenotiol" (nel catalogo del Ministero MCPA); scritto "un'auxina (fenotiol)".
- Foto: originali in `foto_originali/*_2026-11-23.jpg`; scontornate nuove `kit/assets/foto/fengib.png`, `hisense.png`, `spraydunger.png` (rembg + contorno a mano). Auxiger e Switch usano le scontornate già presenti nel kit.
