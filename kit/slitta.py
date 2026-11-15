#!/usr/bin/env python3
"""Fa slittare in avanti tutte le uscite NON pubblicate (es. dopo un blocco dell'account).

Uso: python3 kit/slitta.py <giorni> <da AAAA-MM-GG> [--prova]
  Sposta di <giorni> ogni uscita non pubblicata con data >= <da>, mantenendo l'orario.
  Le uscite cambiano settimana se serve: immagini, didascalie, voci di spec.json e
  calendario.json vengono spostate nella cartella della settimana giusta e rinominate
  con il nuovo giorno (es. ven_0700 del 13 → lun_0700 del 16).
  Approvazioni, temi, prodotti restano invariati. Con --prova stampa solo il piano.
"""
import sys, json, datetime
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
G = ["lun", "mar", "mer", "gio", "ven", "sab", "dom"]


def lunedi(d):
    return (d - datetime.timedelta(days=d.weekday())).isoformat()


def nuovo_id(u, nd, post_ora=None):
    g = G[nd.weekday()]
    hhmm = u["ora"].replace(":", "")
    if u.get("dopo_post"):
        return f"{g}_{post_ora.replace(':', '')}_storia"
    if u["tipo"] == "storia" and u["ora"] == "18:00":
        return f"{g}_curiosita_1800"
    return f"{g}_{hhmm}"


def carica(lun):
    W = REPO / "settimane" / lun
    cf, sf = W / "calendario.json", W / "spec.json"
    cal = json.loads(cf.read_text(encoding="utf-8")) if cf.exists() else {
        "settimana": lun, "fuso": "Europe/Rome", "account_instagram": "17841427890713085",
        "base_url": f"https://raw.githubusercontent.com/n2f97r9vy4-source/studio4-media/main/settimane/{lun}/",
        "approvazione": "in attesa",
        "regola_storie": "Ogni post ha una storia di richiamo 5 minuti dopo (campo dopo_post): la pubblica la stessa esecuzione del post, solo se il post è uscito.",
        "uscite": []}
    spec = json.loads(sf.read_text(encoding="utf-8")) if sf.exists() else {"settimana": lun, "uscite": []}
    return cal, spec


def main():
    giorni, da = int(sys.argv[1]), datetime.date.fromisoformat(sys.argv[2])
    prova = "--prova" in sys.argv
    settimane = sorted(p.name for p in (REPO / "settimane").iterdir() if (p / "calendario.json").exists())
    cal, spec = {}, {}
    for s in settimane:
        cal[s], spec[s] = carica(s)

    # 1. piano: chi si sposta e dove
    mosse = []  # (sett_vecchia, uscita, sett_nuova, id_nuovo, data_nuova)
    for s in settimane:
        da_spostare = [u for u in cal[s]["uscite"] if not u.get("pubblicato") and datetime.date.fromisoformat(u["data"]) >= da]
        per_id = {u["id"]: u for u in cal[s]["uscite"]}
        # il richiamo di un post già uscito resta dov'è
        da_spostare = [u for u in da_spostare if not (u.get("dopo_post") and per_id.get(u["dopo_post"], {}).get("pubblicato"))]
        for u in da_spostare:
            nd = datetime.date.fromisoformat(u["data"]) + datetime.timedelta(days=giorni)
            post_ora = per_id[u["dopo_post"]]["ora"] if u.get("dopo_post") else None
            mosse.append((s, u, lunedi(nd), nuovo_id(u, nd, post_ora), nd.isoformat()))
    mappa = {(s, u["id"]): (ns, nid) for s, u, ns, nid, _ in mosse}
    nuovi = [(ns, nid) for _, _, ns, nid, _ in mosse]
    assert len(set(nuovi)) == len(nuovi), "id nuovi ripetuti"
    restano = {(s, u["id"]) for s in settimane for u in cal[s]["uscite"] if (s, u["id"]) not in mappa}
    for ns, nid in nuovi:
        assert (ns, nid) not in restano, f"conflitto con un'uscita che resta: {ns}/{nid}"

    for s, u, ns, nid, nd in mosse:
        print(f"{s}/{u['id']} ({u['data']} {u['ora']}) → {ns}/{nid} ({nd} {u['ora']})  {u['titolo'][:50]}")
    if prova:
        return

    # 2. leggo in memoria tutti i file da spostare
    dati = {}
    for s, u, ns, nid, nd in mosse:
        W = REPO / "settimane" / s
        dati[(s, u["id"])] = {
            "img": [(W / f).read_bytes() for f in u["files"]],
            "cap": (W / u["didascalia"]).read_text(encoding="utf-8") if u.get("didascalia") else None}

    # 3. tolgo dai calendari e dalle spec di origine (e cancello i vecchi file se nessuno li usa più)
    usati = {(s, f) for s in settimane for u in cal[s]["uscite"] if (s, u["id"]) not in mappa for f in u["files"] + ([u["didascalia"]] if u.get("didascalia") else [])}
    spec_mosse = []
    for s in settimane:
        for u in cal[s]["uscite"]:
            if (s, u["id"]) in mappa:
                for f in u["files"] + ([u["didascalia"]] if u.get("didascalia") else []):
                    if (s, f) not in usati and (REPO / "settimane" / s / f).exists():
                        (REPO / "settimane" / s / f).unlink()
        cal[s]["uscite"] = [u for u in cal[s]["uscite"] if (s, u["id"]) not in mappa]
        tieni = []
        for su in spec[s]["uscite"]:
            if (s, su["id"]) in mappa:
                spec_mosse.append((s, su))
            else:
                tieni.append(su)
        spec[s]["uscite"] = tieni

    # 4. scrivo nelle settimane di arrivo
    for s, u, ns, nid, nd in mosse:
        if ns not in cal:
            cal[ns], spec[ns] = carica(ns)
        W = REPO / "settimane" / ns
        (W / "img").mkdir(parents=True, exist_ok=True); (W / "didascalie").mkdir(exist_ok=True)
        d = dati[(s, u["id"])]
        n = len(d["img"])
        files = [f"img/{nid}_{i + 1}.jpg" for i in range(n)] if u["tipo"] in ("carosello", "immagine") else [f"img/{nid}.jpg"]
        for f, b in zip(files, d["img"]):
            (W / f).write_bytes(b)
        v = dict(u)
        v.setdefault("slittato_da", f"{u['data']} {u['ora']} ({s}/{u['id']})")
        v.update(id=nid, data=nd, files=files)
        if u.get("dopo_post"):
            v["dopo_post"] = mappa[(s, u["dopo_post"])][1]
        if d["cap"] is not None:
            v["didascalia"] = f"didascalie/{nid}.txt"
            (W / v["didascalia"]).write_text(d["cap"], encoding="utf-8")
        cal[ns]["uscite"].append(v)
    for s, su in spec_mosse:
        ns, nid = mappa[(s, su["id"])]
        nd = datetime.date.fromisoformat(su["data"]) + datetime.timedelta(days=giorni)
        v = dict(su); v.update(id=nid, data=nd.isoformat())
        spec[ns]["uscite"].append(v)

    # 5. salvo tutto, ordinato
    for s in cal:
        W = REPO / "settimane" / s
        W.mkdir(parents=True, exist_ok=True)
        cal[s]["uscite"].sort(key=lambda u: (u["data"], u["ora"]))
        (W / "calendario.json").write_text(json.dumps(cal[s], ensure_ascii=False, indent=2), encoding="utf-8")
        if spec[s]["uscite"] or (W / "spec.json").exists():
            spec[s]["uscite"].sort(key=lambda u: (u["data"], u["ora"]))
            (W / "spec.json").write_text(json.dumps(spec[s], ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Spostate {len(mosse)} uscite di {giorni} giorni.")


if __name__ == "__main__":
    main()
