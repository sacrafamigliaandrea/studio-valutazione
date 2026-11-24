# -*- coding: utf-8 -*-
import re, json, sys
import os
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from disc_data import DISC

from competenze import ORIG as ORIG_COMP, RUBRICA as RUB_COMP


STOP = set("""il lo la i gli le un uno una di a da in con su per tra fra e ed o od anche ne ci si non che è sono
del della dei delle degli al allo alla ai agli alle dal dalla dai dalle nel nella nei nelle sul sulla sui sulle col
l alunno alunna studente lo suo sua suoi sue loro proprio propria propri proprie modo maniera ad se come più
quando cui quale quali questo questa ogni""".split())

# modificatori: aggettivi/avverbi di grado (radici)
MODS = ["complet", "approfondit", "esaurient", "esaustiv", "consapevol", "sicur", "adeguat", "appropriat",
        "corrett", "essenzial", "semplic", "parzial", "superficial", "frammentari", "generic", "incomplet",
        "lacunos", "soddisfacent", "efficac", "precis", "chiar", "ricc", "articolat", "autonom", "global",
        "sommari", "imprecis", "incert", "approssimativ", "puntual", "attent", "buon", "pien", "scorrevol",
        "personal", "critic", "accettabil", "sufficient", "limitat", "spiccat", "integral", "ampi", "vari",
        "inadeguat", "caren", "dettagliat", "immediat", "elaborat", "coerent", "disinvolt", "confus"]
DEFICIT = ["fatic", "difficolt", "non ", "incert", "caren", "inadeguat", "frammentari", "lacunos", "superficial",
           "impreci", "confus", "scorrett", "approssimativ", "si distrae", "poco "]
SUPPORT = ["guidat", "guida", "sollecitat", "supporto", "aiuto", "modello", "schema fornit", "scaletta",
           "esempi", "glossario", "domande", "passo passo", "dimostrazione", "istruzioni", "impostat", "lista di controllo", "scheda"]

def words(t):
    t = t.lower().replace("’", "'")
    toks = re.findall(r"[a-zàèéìòù]+", t)
    return [w for w in toks if w not in STOP and len(w) > 2]

def is_mod(w):
    return any(w.startswith(m) for m in MODS) or w.endswith("mente")

def content(t):
    return set(w for w in words(t) if not is_mod(w))

def jacc(a, b):
    A, B = content(a), content(b)
    return len(A & B) / len(A | B) if A | B else 0

def overlap(levels):
    pairs = [jacc(levels[i], levels[i + 1]) for i in range(len(levels) - 1)]
    return sum(pairs) / len(pairs), pairs

def has(t, lex):
    t = t.lower()
    return any(k in t for k in lex)

def mods_in(t):
    return [w for w in words(t) if is_mod(w)]

res = {"disc": [], "mods": {}, "totals": {}}
all_o, all_r = [], []
low_def_o = low_def_r = low_sup_o = low_sup_r = n_low = 0
inmodo_o = inmodo_r = n_desc_o = n_desc_r = 0
mod_count = {}
words_o, words_r = [], []
pairs_high = 0; pairs_tot = 0; pairs_high_r = 0; pairs_tot_r = 0

def add_group(nome, key, origs, rubs):
    global pairs_high_r, pairs_tot_r, low_def_o, low_def_r, low_sup_o, low_sup_r, n_low, inmodo_o, inmodo_r, n_desc_o, n_desc_r, pairs_high, pairs_tot
    ov_o = []; ov_r = []
    for o, r in zip(origs, rubs):
        a, pr = overlap(o); b, prr = overlap(r)
        pairs_tot_r += len(prr); pairs_high_r += sum(1 for p in prr if p >= 0.5)
        ov_o.append(a); ov_r.append(b)
        pairs_tot += len(pr); pairs_high += sum(1 for p in pr if p >= 0.5)
        n_low += 1
        low_def_o += has(o[-1], DEFICIT); low_def_r += has(r[-1], DEFICIT)
        low_sup_o += has(o[-1], SUPPORT); low_sup_r += has(r[-1], SUPPORT)
        for t in o:
            n_desc_o += 1; inmodo_o += bool(re.search(r"in (modo|maniera)", t.lower()))
            words_o.append(len(t.split()))
            for m in mods_in(t):
                for root in MODS:
                    if m.startswith(root):
                        mod_count[root] = mod_count.get(root, 0) + 1; break
        for t in r:
            n_desc_r += 1; inmodo_r += bool(re.search(r"in (modo|maniera)", t.lower()))
            words_r.append(len(t.split()))
    mo = sum(ov_o) / len(ov_o); mr = sum(ov_r) / len(ov_r)
    all_o.extend(ov_o); all_r.extend(ov_r)
    res["disc"].append(dict(key=key, nome=nome, ov_o=round(mo, 3), ov_r=round(mr, 3),
                            nuclei=[round(x, 3) for x in ov_o], nuclei_r=[round(x, 3) for x in ov_r],
                            w_o=round(sum(len(t.split()) for o in origs for t in o) / sum(len(o) for o in origs), 1),
                            w_r=round(sum(len(t.split()) for r in rubs for t in r) / sum(len(r) for r in rubs), 1)))

add_group("Competenze trasversali", "comp", [list(r[1:]) for r in ORIG_COMP], RUB_COMP)
for d in DISC:
    add_group(d["nome"], d["key"], [n["orig"] for n in d["nuclei"]], [n["rubrica"] for n in d["nuclei"]])

res["totals"] = dict(
    documenti=1 + len(DISC), gruppi=len(all_o),
    descrittori_o=n_desc_o, descrittori_r=n_desc_r,
    ov_o=round(sum(all_o) / len(all_o), 3), ov_r=round(sum(all_r) / len(all_r), 3),
    pairs_high=pairs_high, pairs_tot=pairs_tot, pairs_high_r=pairs_high_r, pairs_tot_r=pairs_tot_r,
    inmodo_o=inmodo_o, inmodo_r=inmodo_r,
    low_def_o=low_def_o, low_def_r=low_def_r, low_sup_o=low_sup_o, low_sup_r=low_sup_r, n_low=n_low,
    words_o=round(sum(words_o) / len(words_o), 1), words_r=round(sum(words_r) / len(words_r), 1),
)
res["mods"] = dict(sorted(mod_count.items(), key=lambda x: -x[1])[:14])
json.dump(res, open(os.path.join(HERE, "metrics.json"), "w"), ensure_ascii=False, indent=1)
print(json.dumps(res["totals"], indent=1)); print(res["mods"])
for d in res["disc"]: print(d["nome"], d["ov_o"], d["ov_r"], d["nuclei"], d["w_o"], d["w_r"])
