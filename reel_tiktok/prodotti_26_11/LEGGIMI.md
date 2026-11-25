# Caroselli e video prodotto 26/11 (gruppo 1: 8 prodotti mandati da Valerio il 25/11 sera)

Richiesta di Valerio (25/11 23:13): per ogni prodotto video TikTok + carosello Instagram + didascalia, come gli altri, massimo 5 slide; copertina col problema risolto, "Lo sapevi?" davvero tecnico.
Fatti 4 slide ciascuno (copertina, come lavora, dose, Lo sapevi?), stile kit (`kit/s4kit.py`), TikTok = slide del kit su fondo sfocato. Generatore: `NODE_PATH=$(npm root -g) python3 genera_kit.py`.
Scontorni nuovi in `kit/assets/foto/` (altacor, kanemite, magnumfe, nemathorin, sivanto, teldor, xtreem) fatti con un modello di scontorno (ISNet) in locale.

## Autorizzazioni (catalogo Ministero in Supabase, agg. 18/11; Prontuario del banco)
- Teldor Plus 13084: autorizzato fino al 31/12/2031.
- Altacor 14137: fino al 31/05/2027.
- Sivanto Prime 16273: fino al 09/06/2029.
- xTreem Prime 12066: fino al 30/06/2039 (etichetta valida dal 18/09/2026).
- Kanemite 14100: nel catalogo scadenza 15/11/2026 (stato "Ri-registrato"). La sostanza acequinocil è stata prorogata dall'UE al 15/01/2029 (Reg. di esecuzione UE 2026/2348 del 23/10/2026): ricontrollare la proroga del prodotto sul sito del Ministero prima di pubblicare.
- Nemathorin 150 EC 14336: scade il 31/01/2027 (fostiazate non nella proroga UE 2026/2348).
- **Intrepid 15130: REVOCATO dal 01/04/2026 (metossifenozide non rinnovata), vendita consentita fino al 30/09/2026 (finita), uso fino al 31/03/2027. NESSUN POST fatto.**
- Magnum Fe: concime, non fitosanitario.

## Dosi (tutte da etichetta, tranne Magnum Fe)
Teldor Plus et. 08/09/2026; Altacor et. valida dal 08/07/2026; Sivanto Prime et. 08/09/2026; Kanemite et. 12/06/2026; Nemathorin et. 17/07/2021; xTreem Prime et. 18/09/2026 (Supabase id 33).
Magnum Fe: nessuna dose (non è nel Prontuario; dalla foto si vede solo il fronte). Composizione (N organico 5,5%, C organico 20%, aminoacidi levogiri 10%, sangue fluido + alghe brune, betaine, vitamine, ferro organico) e uso in fertirrigazione/fogliare presi dalla scheda di un rivenditore online: DA CONFERMARE con il retro della tanica. Non scritto "biologico".

## Fonti dei "Lo sapevi?" (archivio interno, non nei post)
- Teldor: Walker et al. 2011 Phytopathology (B. pseudocinerea, poco sensibile alla fenexamide); Fillinger et al. 2008 AEM (mutazioni erg27, es. F412S); Debieu et al. 2001 (fenexamide su tubetto germinativo/micelio).
- Altacor: Roditakis et al. 2017 Insect Biochem Mol Biol (Tuta, mutazioni RyR G4903E, I4746M, Italia e Grecia); finestra d'impiego e ciclo <50 gg dall'etichetta.
- Sivanto: Tosi & Nieh 2019 Proc R Soc B (sinergia flupyradifurone + triazolo sulle api); Nauen et al. 2015 Pest Manag Sci (non metabolizzato da CYP6CM1); IRAC MoA (rotazione tra sottogruppi solo senza alternative).
- Kanemite: Van Leeuwen et al. 2008 PNAS (mutazioni cyt b, eredità materna); Van Nieuwenhuyse et al. 2009 Pest Manag Sci (resistenza incrociata bifenazate-acequinocil; attivazione per deacetilazione).
- Nemathorin: azione nematostatica dei fosforganici alle dosi di campo (Opperman & Chang 1990; Wright 1981); ingresso J2 vicino all'apice radicale.
- xTreem: Cry1C del ceppo aizawai attiva su Spodoptera; solubilizzazione dei cristalli a pH alcalino; degradazione UV.
- Magnum Fe: aminoacidi D tossici (Erikson et al. 2004 Nat Biotechnol); assorbimento diretto degli aminoacidi (Näsholm et al. 2009 New Phytol); glicina betaina osmoprotettore.
