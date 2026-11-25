# Video TikTok Signum, Affirm, Nifert (25/11/2026) — BOZZE

Richiesta di Valerio (25/11 16:42): un video TikTok per ogni prodotto, stile Studio 4, con il problema che risolvono subito in primo piano. Foto in `foto_originali/*_2026-11-25_*.jpg`, scontorni in `kit/assets/foto/{signum,affirm,nifert}.png`.

Stile: 1080x1920, foto del prodotto sfocata a tutto schermo + prodotto scontornato, logo `kit/assets/logo_s4.png` (180 px) direttamente sullo sfondo con numero slide in verde, niente copertina. 4 slide, 15,8 s, muti.
Rigenerare: `python3 genera.py && node rendi.js signum affirm nifert && ./video.sh signum signum_tiktok.mp4` (testi in `contenuti.json`).

## Fonti (interne, non nei post)
- **Signum** (reg. 12869): etichetta nel Prontuario (26/11/2025; la banca dati ha un'etichetta del 22/06/2026, segnata "dosi invariate"). Pomodoro e peperone 100–150 g/hl (1–1,5 kg/ha), melanzana 150 g/hl, ogni 7–10 gg, max 3/anno su solanacee, carenza 3 gg; uso preventivo; sotto 1.000 l/ha si usa la dose a ettaro; max 3 l'anno con boscalid o strobilurine. Cucurbitacee assenti dagli impieghi. FRAC 7 (boscalid) e 11 (piraclostrobin): classificazione FRAC.
- **Affirm** (reg. 13389): etichetta in foto 25/11 + Prontuario. Orticole in serra e campo 150 g/hl (1,5 kg/ha), max 3/anno, carenza 3 gg, intervalli 7–14 gg (tuta 7–10); api: niente in fioritura, alveari rimossi o coperti per 24 ore. IRAC 6: classificazione IRAC. Catalogo Ministero 16/11: scadenza 15/11/2026 ma stato "Autorizzato" (etichetta nuova del 14/09/2026).
- **Nifert**: etichetta in foto 25/11 e Prontuario (foto banco 27/10). Orticole in serra 200–300 g/hl fogliare o 6,5–9 kg/ha in fertirrigazione ogni 10–15 gg; dopo stress dose alta entro 24–48 ore, ripetere a 8–10 gg; incompatibilità e conservazione 10–30 °C dall'etichetta.

Il video Affirm del 24/11 (`caroselli_ridomil_vertimec_affirm_24_11/`) partiva dalla sola Tuta absoluta: questo lo sostituisce con l'uso generale (tutti i lepidotteri).
