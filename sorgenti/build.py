# -*- coding: utf-8 -*-
import json, sys
import os
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from disc_data import DISC, DIAG

M = json.load(open(os.path.join(HERE, "metrics.json"), encoding="utf-8"))
OV = {d["key"]: d for d in M["disc"]}

# ---- competenze trasversali ----
import competenze as C
ORIG_COMP = C.ORIG
ns = {"GRIGLIA": C.GRIGLIA, "RUBRICA": C.RUBRICA}
DIMS = ["Comunicazione", "Partecipazione", "Lavoro di squadra", "Cittadinanza e rispetto delle regole",
        "Impegno scolastico", "Ricerca di soluzioni (creatività)", "Gestione delle emozioni"]
comp = dict(key="comp", nome="Competenze trasversali", sotto="Rubrica d'istituto · base del giudizio e del comportamento",
            livelli=["A · 10", "B · 9-8", "C · 7-6", "D · 5-4"], nuclei=[])
for i, r in enumerate(ORIG_COMP):
    comp["nuclei"].append(dict(nome=DIMS[i], orig=list(r[1:]),
                               griglia=[(DIMS[i], ns["GRIGLIA"][i])], rubrica=ns["RUBRICA"][i]))
DIAG["comp"] = [
 ("criticita", "In «Creatività» ed «Emozioni» i livelli misurano qualità diverse: A parla di decidere, B di originalità; A di benessere altrui, B di controllo."),
 ("criticita", "In «Cittadinanza» il livello C («deve ancora essere richiamato») è più grave del D («deve maturare un approccio più responsabile»): ordine invertito."),
 ("criticita", "Frasi da completare («Si richiede maggior impegno in…»): lo strumento funziona come frasario per il giudizio, non come rubrica."),
 ("criticita", "D corrisponde a 5-4: se la tabella alimenta il comportamento, porta in automatico verso la non ammissione."),
 ("forza", "«Partecipazione» è la riga modello: la stessa qualità cresce per gradi osservabili, da «evita il coinvolgimento» a «contributo personale»."),
]
ov_c = OV["comp"]
comp["ovo"], comp["ovr"] = ov_c["nuclei"], ov_c["nuclei_r"]

areas = [comp]
for d in DISC:
    o = OV[d["key"]]
    areas.append(dict(key=d["key"], nome=d["nome"], sotto=d["sotto"], livelli=d["livelli"],
                      nuclei=[dict(nome=n["nome"], orig=n["orig"], griglia=n["griglia"], rubrica=n["rubrica"]) for n in d["nuclei"]],
                      ovo=o["nuclei"], ovr=o["nuclei_r"]))
for a in areas:
    a["diag"] = DIAG[a["key"]]
    a["ov"] = [OV[a["key"]]["ov_o"], OV[a["key"]]["ov_r"]]

data = dict(areas=areas, totals=M["totals"], mods=M["mods"])
js = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
html = open(os.path.join(HERE, "template.html"), encoding="utf-8").read().replace("__DATA__", js)
open(os.path.join(HERE, "..", "index.html"), "w", encoding="utf-8").write(html)
print("ok", len(html))
