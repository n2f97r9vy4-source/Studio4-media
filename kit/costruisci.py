#!/usr/bin/env python3
"""Costruisce una settimana dalla specifica.
Uso:  python3 kit/costruisci.py 2026-11-16            (tutte le uscite della specifica non ancora pubblicate)
      python3 kit/costruisci.py 2026-11-16 --solo mar_0700,mar_1930
Legge settimane/<lunedì>/spec.json, controlla i testi (filtro), crea immagini e didascalie,
aggiorna calendario.json (approvato=false) e scrive rapporto.md. Un'uscita con errori NON entra nel calendario.
"""
import sys, json, datetime
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import s4kit as K

GIORNI = ["lun", "mar", "mer", "gio", "ven", "sab", "dom"]
ORE_POST = ["07:00", "13:00", "19:30"]

def piu5(h):
    H, M = map(int, h.split(":")); t = H * 60 + M + 5
    return f"{t//60:02d}:{t%60:02d}"

def main():
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(2)
    lun = sys.argv[1]
    solo = set(sys.argv[sys.argv.index("--solo") + 1].split(",")) if "--solo" in sys.argv else None
    d_lun = datetime.date.fromisoformat(lun)
    assert d_lun.weekday() == 0, "la settimana si indica con la data del lunedì"
    W = K.REPO / "settimane" / lun
    (W / "img").mkdir(parents=True, exist_ok=True); (W / "didascalie").mkdir(exist_ok=True)
    spec = json.loads((W / "spec.json").read_text(encoding="utf-8"))
    prodotti = json.loads((K.KIT / "prodotti.json").read_text(encoding="utf-8"))
    calf = W / "calendario.json"
    cal = json.loads(calf.read_text(encoding="utf-8")) if calf.exists() else {
        "settimana": lun, "fuso": "Europe/Rome", "account_instagram": "17841427890713085",
        "base_url": f"https://raw.githubusercontent.com/n2f97r9vy4-source/studio4-media/main/settimane/{lun}/",
        "approvazione": "in attesa", "uscite": []}
    cal.setdefault("regola_storie", "Ogni post ha una storia di richiamo 5 minuti dopo (campo dopo_post): la pubblica la stessa esecuzione del post, solo se il post è uscito.")
    per_id = {u["id"]: u for u in cal["uscite"]}
    registro = K.uscite_registrate()
    giorni_ok = {(d_lun + datetime.timedelta(days=i)).isoformat() for i in range(7)}

    rapporto, lavori, piani = [], [], []
    ids = set()
    for u in spec["uscite"]:
        if solo and u["id"] not in solo:
            continue
        err, avv = [], []
        if u["id"] in ids: err.append("id ripetuto nella specifica")
        ids.add(u["id"])
        if per_id.get(u["id"], {}).get("pubblicato"):
            rapporto.append((u["id"], ["GIÀ PUBBLICATA: non si tocca"], [])); continue
        if u.get("data") not in giorni_ok: err.append(f"data {u.get('data')} fuori dalla settimana")
        if u["tipo"] == "carosello" and u.get("ora") not in ORE_POST: err.append("i post escono alle 07:00, 13:00 o 19:30")
        if u["tipo"] == "curiosita" and u.get("ora") != "18:00": err.append("la curiosità esce alle 18:00")
        if u["tipo"] == "sondaggio" and u.get("ora") != "08:30": err.append("la storia con adesivo esce alle 08:30")
        if u["tipo"] == "sera" and u.get("ora") != "21:45": err.append("la storia tecnica della sera esce alle 21:45")
        if u["tipo"] == "sera":
            err += [f"campo '{k}' mancante: ogni uscita dichiara tema, dato tecnico e da dove viene" for k in ("tema", "dato", "fonte_dato") if not str(u.get(k, "")).strip()]
        try:
            e, a = K.controlla_testi(u, prodotti); err += e; avv += a
            e, a = K.controlla_duplicati(u, lun, registro); err += e; avv += a
            jobs = []
            if u["tipo"] == "carosello":
                files = [f"img/{u['id']}_{i+1}.jpg" for i in range(len(u["slide"]))]
                jobs.append({"kind": "post", "html": K.html_carosello(u), "out": [str(W / f) for f in files]})
                st = dict(u["storia"]); st.setdefault("colore", u["colore"])
                jobs.append({"kind": "storia", "html": K.html_storia(st, "richiamo"), "out": [str(W / f"img/{u['id']}_storia.jpg")]})
            elif u["tipo"] == "sera":
                st = dict(u); st.setdefault("piede", "Ogni sera una cosa da professionisti 🌙")
                jobs.append({"kind": "storia", "html": K.html_storia(st, "curiosita"), "out": [str(W / f"img/{u['id']}.jpg")]})
            else:
                jobs.append({"kind": "storia", "html": K.html_storia(u, u["tipo"]), "out": [str(W / f"img/{u['id']}.jpg")]})
        except Exception as ex:
            err.append(f"specifica non valida: {ex}"); jobs = []
        piani.append((u, err, avv, len(lavori), len(jobs))); lavori += jobs

    esiti = K.rendi(lavori) if lavori else []
    for u, err, avv, i0, n in piani:
        for prob in esiti[i0:i0 + n]:
            for p in prob:
                (avv if p.startswith("AVVISO") else err).append(p)
        rapporto.append((u["id"], err, avv))
        if err:
            for k in [u["id"], u["id"] + "_storia"]:
                if k in per_id and not per_id[k].get("pubblicato"): cal["uscite"].remove(per_id[k]); per_id.pop(k)
            continue
        base = {"data": u["data"], "approvato": False, "attesa_foto": False, "pubblicato": False}
        nuove = []
        if u["tipo"] == "carosello":
            (W / f"didascalie/{u['id']}.txt").write_text(K.didascalia_finale(u["didascalia"]), encoding="utf-8")
            nuove.append({"id": u["id"], "tipo": "carosello", "ora": u["ora"], "titolo": u["titolo"], "tema": u["tema"], "prodotti": u.get("prodotti", []),
                          "files": [f"img/{u['id']}_{i+1}.jpg" for i in range(len(u["slide"]))], "didascalia": f"didascalie/{u['id']}.txt", **base})
            nuove.append({"id": u["id"] + "_storia", "tipo": "storia", "ora": piu5(u["ora"]), "titolo": "Richiamo: " + u["titolo"],
                          "files": [f"img/{u['id']}_storia.jpg"], "automatica": True, "dopo_post": u["id"], **base})
        elif u["tipo"] == "curiosita":
            nuove.append({"id": u["id"], "tipo": "storia", "ora": "18:00", "titolo": "Curiosità: " + u["titolo_breve"], "tema": u["tema"],
                          "files": [f"img/{u['id']}.jpg"], "automatica": True, **base})
        elif u["tipo"] == "sera":
            nuove.append({"id": u["id"], "tipo": "storia", "ora": "21:45", "titolo": "Sera: " + u["titolo_breve"], "tema": u["tema"],
                          "files": [f"img/{u['id']}.jpg"], "automatica": True, **base})
        else:
            nuove.append({"id": u["id"], "tipo": "storia", "ora": "08:30", "titolo": u["titolo_breve"] + f" (adesivo {u.get('adesivo', 'sondaggio')})", "tema": u["tema"],
                          "files": [f"img/{u['id']}.jpg"], "automatica": False, "adesivo": u.get("adesivo", "sondaggio"), "risposte": u.get("risposte", []), **base})
        for nu in nuove:
            if nu["id"] in per_id: cal["uscite"].remove(per_id[nu["id"]])
            cal["uscite"].append(nu); per_id[nu["id"]] = nu

    cal["uscite"].sort(key=lambda x: (x["data"], x["ora"]))
    calf.write_text(json.dumps(cal, ensure_ascii=False, indent=2), encoding="utf-8")

    # copertura della settimana
    buchi = []
    for i in range(7):
        d = (d_lun + datetime.timedelta(days=i)).isoformat(); du = [x for x in cal["uscite"] if x["data"] == d]
        for h in ORE_POST:
            p = [x for x in du if x["ora"] == h and x["tipo"] != "storia"]
            if not p: buchi.append(f"{GIORNI[i]} {h}: manca il post")
            elif not any(x.get("dopo_post") == p[0]["id"] for x in du): buchi.append(f"{GIORNI[i]} {piu5(h)}: manca la storia di richiamo di {p[0]['id']}")
        if not any(x["ora"] == "08:30" for x in du): buchi.append(f"{GIORNI[i]} 08:30: manca la storia con adesivo")
        if not any(x["ora"] == "18:00" for x in du): buchi.append(f"{GIORNI[i]} 18:00: manca la curiosità")
        if not any(x["ora"] == "21:45" for x in du): buchi.append(f"{GIORNI[i]} 21:45: manca la storia tecnica della sera")

    righe = [f"# Rapporto di costruzione — settimana {lun}", ""]
    n_err = 0
    for i, err, avv in rapporto:
        stato = "BLOCCATA" if err else "ok"; n_err += bool(err)
        righe.append(f"- **{i}**: {stato}")
        righe += [f"  - ERRORE: {e}" for e in err] + [f"  - avviso: {a}" for a in avv]
    righe += ["", "## Copertura (3 post + richiami + adesivo 8:30 + curiosità 18:00 + tecnica 21:45 ogni giorno)"]
    righe += [f"- {b}" for b in buchi] or ["- completa"]
    (W / "rapporto.md").write_text("\n".join(righe) + "\n", encoding="utf-8")
    print("\n".join(righe))
    sys.exit(1 if n_err else 0)

if __name__ == "__main__":
    main()
