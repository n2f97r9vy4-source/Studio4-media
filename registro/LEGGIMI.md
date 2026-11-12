# Registro duplicati (controllo 7 del filtro)
Il registro è calcolato: tutte le uscite con campo `tema` nei `settimane/*/calendario.json` più `registro/manuali.json` (cose pubblicate a mano da Valerio, es. Reel).
`kit/costruisci.py` blocca un'uscita il cui `tema` è già stato usato nei 30 giorni prima o dopo, e avvisa se lo stesso prodotto è protagonista di due caroselli entro 10 giorni.
Quando Valerio pubblica qualcosa a mano, aggiungilo a `manuali.json`.
