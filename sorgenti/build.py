# -*- coding: utf-8 -*-
# Unisce dati e template e rigenera index.html.
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from disc_data import DISC
import competenze as C
from atlante_testi import GIA, PASSO

DIMS = ["Comunicazione", "Partecipazione", "Lavoro di squadra", "Cittadinanza e rispetto delle regole",
        "Impegno scolastico", "Ricerca di soluzioni (creatività)", "Gestione delle emozioni"]

comp = dict(key="comp", nome="Competenze trasversali", sotto="Rubrica d'istituto per le competenze trasversali",
            livelli=["Livello A", "Livello B", "Livello C", "Livello D"],
            nuclei=[dict(nome=DIMS[i], orig=list(r[1:]), griglia=[(DIMS[i], C.GRIGLIA[i])], rubrica=C.RUBRICA[i])
                    for i, r in enumerate(C.ORIG)])
areas = [comp] + [dict(key=d["key"], nome=d["nome"], sotto=d["sotto"], livelli=d["livelli"],
                       nuclei=[dict(nome=n["nome"], orig=n["orig"], griglia=n["griglia"], rubrica=n["rubrica"]) for n in d["nuclei"]])
                  for d in DISC]
# ordine: competenze trasversali, poi discipline per ore settimanali (quadro orario nazionale, DPR 89/2009)
ORE = {"ita": 6, "itas": 6, "mat": 6, "ing": 3, "sto": 2, "geo": 2, "spa": 2, "tec": 2, "art": 2, "mus": 2, "irc": 1}
ORDINE = ["comp", "ita", "itas", "mat", "ing", "sto", "geo", "spa", "tec", "art", "mus", "irc"]
areas.sort(key=lambda a: ORDINE.index(a["key"]))
for a in areas:
    a["gia"], a["passo"] = GIA[a["key"]], PASSO[a["key"]]
    a["ore"] = ORE.get(a["key"])

js = json.dumps(dict(areas=areas), ensure_ascii=False).replace("</", "<\\/")
import base64
IMG = "data:image/jpeg;base64," + base64.b64encode(open(os.path.join(HERE, "img", "scheda-scrutinio.jpg"), "rb").read()).decode()
html = open(os.path.join(HERE, "template.html"), encoding="utf-8").read().replace("__DATA__", js).replace("__SCHEDA__", IMG)
open(os.path.join(HERE, "..", "index.html"), "w", encoding="utf-8").write(html)
print("ok", len(html))
