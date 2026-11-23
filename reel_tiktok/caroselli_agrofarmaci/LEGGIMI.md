# Caroselli TikTok agrofarmaci — 23/11/2026 (BOZZA, da approvare da Valerio)

Tre caroselli per TikTok @studio4srl, 5 slide ciascuno, nello stesso stile dei video già sul profilo (QZyme, Razormin, Cidely, Turbo Root): slide del kit 1080×1350 (`kit/s4kit.py`, logo STUDIO 4 in alto a destra, senza cornice bianca) al centro di un fondo 9:16 fatto dalla stessa slide sfocata. Video: `../topas_tiktok.mp4`, `../oikos_tiktok.mp4`, `../pergado_tiktok.mp4` (scorrimento a sinistra, audio muto: la musica la mette Valerio dall'app).
Versione 2 (23/11 12:30): la prima versione aveva il logo a sinistra in una cornice bianca; Valerio ha fatto notare che sul profilo è il contrario.

| Carosello | Slide | Didascalia |
|---|---|---|
| Topas 10 EC | `topas/s1–s5.png` | `topas_didascalia.txt` |
| Oikos | `oikos/s1–s5.png` | `oikos_didascalia.txt` |
| Pergado SC | `pergado/s1–s5.png` | `pergado_didascalia.txt` |

Rigenerare: modificare `caroselli_kit.json`, poi `NODE_PATH=$(npm root -g) python3 genera_kit.py` (serve Playwright per Node e ffmpeg).

## Regole rispettate
- Nessuna dose, nessun prezzo, nessun nome del produttore nei testi (controllato con le liste di `kit/s4kit.py`); niente parole assolute; 5 hashtag con #studio4srl; avvertenza fitosanitari su slide e didascalia.
- Testo lontano dalla fascia bassa (ultimi ~360 px) coperta dall'interfaccia di TikTok.

## Fonti dei dati
- **Topas 10 EC** (reg. 6945, scad. autorizzazione 15/02/2029): fronte dell'etichetta nella foto (`foto_originali/topas-10-ec_2026-11-23.jpg`): fungicida sistemico preventivo, curativo e bloccante contro l'oidio di melo, pero, pesco, vite, tabacco, orticole, ornamentali, fragola, mora, lampone, ribes; penconazolo, FRAC 3; EC. Catalogo del Ministero (Supabase `catalogo_fitofarmaci`).
- **Oikos** (reg. 10305, scad. 31/01/2027): fronte nella foto: nematocida-insetticida sistemico per fertirrigazione e fogliare, nematodi e insetti della parte aerea, gruppo UN, EC. Sostanza attiva azadiractina dal catalogo del Ministero. Meccanismo (blocco della muta, azione disappetente e repellente, contatto e ingestione), consigli d'uso (presto, ore fresche e poco luminose, bagnatura uniforme senza gocciolamento, niente vento/mezzi aerei) e selettività sugli insetti utili: **etichetta del 2 luglio 2019** letta online.
- **Pergado SC** (reg. 13382, scad. 30/06/2029): fronte nella foto: fungicida per vite, patata e colture orticole, mandipropamid FRAC 40, SC. Fissazione alle cere, translaminare, resistenza al dilavamento: **volantino tecnico del produttore 2009**.

## IPOTESI da verificare prima di pubblicare
1. **Oikos, parassiti per coltura:** presi dall'etichetta 2019; in Supabase c'è l'etichetta del 08/09/2026 (PDF `10305_etichettaCLP_08092026.pdf`) ancora da leggere. I nematodi non comparivano nell'etichetta 2019: sono scritti sulla bottiglia attuale.
2. **Pergado, "una volta asciutto resiste meglio al dilavamento" e "si lega alle cere":** dal volantino 2009 del produttore, non dall'etichetta.
3. **Peronospora e oidio:** nozioni generali di patologia, non dall'etichetta.
4. **"Bloccante"** spiegato come azione sulle macchie già visibili che frena la formazione di spore: è il significato comune del termine, l'etichetta usa solo la parola.
5. **Oikos in biologico:** NON scritto (il bollino verde sulla bottiglia non è leggibile nella foto).
6. Sulla bottiglia di Oikos nella foto è stampato "31/03/2026": se è la scadenza del lotto, meglio rifare la foto con una confezione più recente.
