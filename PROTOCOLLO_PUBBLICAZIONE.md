# STUDIO 4 MEDIA – Protocollo di pubblicazione automatica (Agente 2)

Account Instagram: studio4.srl (id 17841427890713085), via connettore Windsor.ai for Social Media.
Calendario della settimana: `settimane/<lunedì>/calendario.json`. Immagini: `img/`, didascalie: `didascalie/`.
Link pubblici: `base_url` + percorso del file (raw.githubusercontent.com).

## Regole (dal progetto e dal filtro di conformità)
1. Si pubblica SOLO un'uscita con `"approvato": true` (ok di Valerio). Se è false: non pubblicare, avvisa.
2. Se `"attesa_foto": true`: non pubblicare, avvisa che manca la foto reale.
3. Se `"pubblicato": true`: non ripubblicare.
4. Storie con `"automatica": false` (adesivi sondaggio/domanda): NON pubblicare; manda a Valerio il link dell'immagine da caricare a mano dall'app.
5. Prima di pubblicare un post ricontrolla la didascalia: deve contenere la frase obbligatoria
   "Usare i prodotti fitosanitari con precauzione. Prima dell'uso leggere sempre l'etichetta e le informazioni sul prodotto. Vendita ai possessori di patentino."
   e non deve contenere: elimina*, 100%, senza rischi, garantit*, definitiv*, innocu*, non tossic*, ecologic*, miracolos*, infallibil*, per sempre, zero residui/rischi, il migliore, imbattibil*, sconto, offerta, promo, prezzo, €. Niente nomi dei produttori. Se il controllo fallisce: non pubblicare, avvisa.
6. Controlla che ogni immagine risponda 200 con content-type image/jpeg.
7. Pubblica: carosello → `create_carousel_post` (image_urls in ordine, caption); immagine singola → `create_image_post`; storia → `create_story` (image_url).
8. Dopo la pubblicazione: imposta `"pubblicato": true` e `"media_id"` nel calendario, commit e push.
9. Finestra: pubblica le uscite di oggi con orario tra 20 minuti prima e 3 ore dopo l'ora di esecuzione. Mai uscite di altri giorni.
10. Ogni esecuzione termina con un messaggio breve: cosa è uscito, cosa no e perché.


## Direttiva di Valerio (12/11/2026): storia di richiamo dopo OGNI post
- Ogni post (7:00, 13:00, 19:30) ha SEMPRE una storia che lo riprende, 5 minuti dopo (07:05, 13:05, 19:35). Nel calendario è un'uscita "storia" con il campo "dopo_post" = id del post.
- Stile: come la storia Basfoliar Kelp — titolo del post, foto del prodotto grande, riquadro con un dato tecnico utile, in fondo "Il post completo è sul profilo →".
- La pubblica la stessa esecuzione del post: dopo il post riuscito aspetta 5 minuti (sleep 300) e pubblica la storia con create_story. Se il post non è uscito, la storia non esce.
- Chi prepara il calendario deve creare la storia di richiamo insieme a ogni post: un post senza storia di richiamo non è completo.
