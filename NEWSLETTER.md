# STUDIO 4 MEDIA — "Notizie dal campo" (la newsletter di Studio 4)

Decisa da Valerio il 15/11/2026. Manuale del **Redattore Newsletter** (agente separato dal Direttore Creativo: il Direttore Creativo NON prepara la newsletter e non tocca le sue uscite).

## Perché esiste
L'obiettivo di Valerio (bacheca `claude/00_STUDIO4_BACHECA.md`) ha quattro pilastri: commerciale, consigli che gli agricoltori non sanno, **newsletter**, sponsorizzare sempre Studio 4. La newsletter tiene aggiornati gli agricoltori di serra su cosa succede nell'agricoltura in Italia, in Europa e nel mondo, e spiega **cosa cambia per loro a Vittoria**. Chi la legge deve pensare: "queste cose me le dice Studio 4 prima degli altri". (Il "forum" è stato escluso da Valerio il 15/11.)

## Quando esce
- **Giovedì e domenica alle 20:00** (carosello) + storia di richiamo alle **20:05** (direttiva: ogni post ha la sua storia 5 minuti dopo).
- Nel calendario: id `<giorno>_2000` (es. `gio_2000`), storia `<giorno>_2000_storia`, `"rubrica": "newsletter"`.
- La prepara il Redattore Newsletter il giorno prima (mercoledì per il giovedì, sabato per la domenica, alle 14:23) e la manda a Valerio. Esce solo con il suo ok.

## Cosa ci va
3–4 notizie dei giorni precedenti (dall'ultima newsletter), scelte per importanza per chi coltiva pomodoro, melanzana, peperone, cetriolo, zucchina in serra in Sicilia. Temi:
- regole e norme (Italia, UE): fitofarmaci revocati, nuove autorizzazioni, scadenze, quaderno di campagna, patentino, etichette, biologico;
- mercati: prezzi all'origine e andamento delle ortive (Vittoria, Italia, concorrenza estera), import/export;
- bandi, contributi, PAC, crediti, calamità ed emergenze;
- difesa: nuove emergenze fitosanitarie, virus, insetti in arrivo;
- ricerca e innovazione utile in serra; clima e meteo che pesa sulla campagna.
Niente politica di parte, niente opinioni su partiti o persone: solo fatti e cosa cambiano per l'agricoltore.

## Fonti (solo ufficiali o autorevoli, lette per intero)
Ministero dell'Agricoltura (masaf.gov.it), Ministero della Salute (banca dati fitosanitari, revoche), Commissione europea DG AGRI ed EFSA, Gazzetta Ufficiale / G.U. UE, Regione Siciliana (assessorato agricoltura, servizio fitosanitario), ISMEA (prezzi e mercati), CREA, università, servizi fitosanitari regionali, agenzie di stampa (ANSA) e stampa agricola nazionale (es. Agronotizie, Informatore Agrario, L'Informatore) solo come segnale, da riscontrare su una fonte ufficiale quando la notizia è una norma o un dato.
- Ogni notizia: data, fonte e link nel campo `fonte_dato` della specifica (archivio interno). **Nei post e nelle didascalie le fonti NON si scrivono** (regola di Valerio).
- Se una notizia non si riesce a verificare, non esce. Meglio 3 notizie vere che 4 con un dubbio.
- Mai copiare testi: solo parole tue; nessuna citazione lunga.

## Fonti Instagram con Apify (decisione di Valerio, 17/11/2026)
Valerio vuole che la ricerca parta anche dalle pagine Instagram italiane che parlano di agronomia, agricoltura digitale e mercati, a livello nazionale, con un occhio all'Università di Catania (Di3A), che fa spesso prove e studi utili per le serre del Ragusano.
- Strumento: connettore Apify, Actor `apify/instagram-scraper`, input: `directUrls` = profili qui sotto, `resultsType: "posts"`, `resultsLimit: 5`, `onlyPostsNewerThan: "4 days"`, `addParentData: true`; `callOptions.maxTotalChargeUsd: 1`. Leggere con get-dataset-items solo i campi `ownerUsername,url,timestamp,likesCount,caption`. Costo: pochi centesimi a giro.
- Profili verificati il 17/11/2026:
  - Stampa agricola: `agronotizie` (AgroNotizie, ~30.000 follower, norme e aiuti).
  - Istituzioni: `masafsocial` (Ministero dell'Agricoltura), `ismeaofficial` (ISMEA, mercati e rapporti), `crearicerca` (CREA, ricerca e agricoltura digitale), `regionesiciliana`.
  - Università e professione: `di3aunict` (Di3A Università di Catania: studi, prove, giornate tecniche), `odaf_catania` (Ordine Agronomi Catania).
  - Organizzazioni agricole: `coldiretti`, `coldiretti_sicilia`, `confagricoltura`, `cia_agricoltori`.
  - Estero (in inglese): `freshplaza` (pubblica poco su Instagram).
  - Non trovati su Instagram (si cercano sul web): Informatore Agrario, Terra e Vita / Edagricole, Italiafruit News, FreshPlaza Italia, EFSA.
- Il post Instagram è solo il SEGNALE: la notizia si verifica sempre sulla fonte ufficiale o sull'articolo completo (link in bio / sito) prima di usarla. Scartare eventi, auguri, campagne d'immagine e politica: tenere norme, aiuti, mercati, emergenze fitosanitarie, ricerca applicabile in serra.
- Salva il raccolto del giro in `newsletter/raccolta_<AAAA-MM-GG>.md` (archivio interno, con link).

## Struttura del carosello (4–6 slide, kit `kit/s4kit.py`)
1. **Copertina** che aggancia: "📰 Notizie dal campo" + la notizia più forte come titolo + data ("Giovedì 19 novembre").
2. **Una slide per notizia** (tipo `schede` o `grande`): cosa è successo in 2 righe + riquadro **"Cosa cambia per te"** (concreto, per chi lavora in serra a Vittoria).
3. **"Lo sapevi?"** legato a una delle notizie (dato tecnico o di contesto).
4. **Chiusura Studio 4**: "Hai dubbi su cosa cambia per la tua azienda? Passa al banco: ne parliamo." (+ orari/WhatsApp se utile). Qui si sponsorizza il magazzino e la rivendita, senza prezzi né promozioni.

## Didascalia
Riga-gancio con 📰 · le notizie in punti brevi ("• Titolo — cosa cambia per te") · "💡 Lo sapevi?" · chiusura "Ti aggiorniamo ogni Giovedì e domenica alle 20. Hai dubbi? Passa al banco." · hashtag (6–8: #notiziedalcampo #agricoltura #serra #vittoria #studio4srl …). Il kit aggiunge da solo la frase obbligatoria.

## Regole fisse (valgono tutte quelle di DIREZIONE_CREATIVA.md §3)
Mai nomi dei produttori; niente prezzi, sconti o promozioni di Studio 4 (i prezzi di mercato all'origine sono notizie e si possono dare, con la data); niente parole assolute; niente dosi (la newsletter non dà dosi); logo e stile del kit senza modifiche.

## Procedura (Redattore Newsletter)
1. Leggi la bacheca, questo manuale, `DIREZIONE_CREATIVA.md` §3–5 e §7 (formato spec), le ultime 3 newsletter nei calendari (per non ripetere).
2. Lancia il giro Apify sui profili Instagram (sezione "Fonti Instagram con Apify") e leggi `newsletter/raccolta_*.md` degli ultimi giorni; poi ricerca web sulle fonti ufficiali. Verifica, scegli 3–4 notizie.
3. Aggiungi l'uscita `<giorno>_2000` in `settimane/<lunedì>/spec.json` (tipo carosello, ora "20:00", `rubrica: "newsletter"`, storia di richiamo, `tema` = "newsletter-AAAA-MM-GG"), poi `python3 kit/costruisci.py <lunedì> --solo <giorno>_2000`. Non toccare le altre uscite.
4. Guarda le immagini, correggi testi fitti o tagliati. Commit e push.
5. Manda a Valerio l'anteprima (le slide) e le notizie con le fonti; aspetta il suo ok. Con l'ok: `approvato: true` sul post e sulla storia, commit e push. Senza ok entro le 20:00 non esce.
6. Scrivi una riga nel DIARIO della bacheca.
