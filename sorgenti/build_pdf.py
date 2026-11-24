# -*- coding: utf-8 -*-
# Genera studio-valutazione.pdf (lettura approfondita) con gli stessi dati della pagina.
# Richiede Google Chrome o Chromium, pypdf, reportlab, poppler (pdftotext).
import html, io, os, re, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from disc_data import DISC
import competenze as C
from atlante_testi import GIA, PASSO

ROOT = os.path.abspath(os.path.join(HERE, ".."))
OUT = os.path.join(ROOT, "studio-valutazione.pdf")
TMP = os.path.join(HERE, "_pdf")
os.makedirs(TMP, exist_ok=True)
e = html.escape

DIMS = ["Comunicazione", "Partecipazione", "Lavoro di squadra", "Cittadinanza e rispetto delle regole",
        "Impegno scolastico", "Ricerca di soluzioni (creatività)", "Gestione delle emozioni"]
ORE = {"ita": 6, "itas": 6, "mat": 6, "ing": 3, "sto": 2, "geo": 2, "spa": 2, "tec": 2, "art": 2, "mus": 2, "irc": 1}
ORDINE = ["comp", "ita", "itas", "mat", "ing", "sto", "geo", "spa", "tec", "art", "mus", "irc"]
comp = dict(key="comp", nome="Competenze trasversali", sotto="Valutazione globale",
            nuclei=[dict(nome=DIMS[i], orig=list(r[1:]), griglia=[(DIMS[i], C.GRIGLIA[i])], rubrica=C.RUBRICA[i])
                    for i, r in enumerate(C.ORIG)])
AREAS = sorted([comp] + DISC, key=lambda a: ORDINE.index(a["key"]))
RUBL = ["Iniziale", "Base", "Intermedio", "Avanzato"]
CLS = ["d", "c", "b", "a"]

PIN = '<svg viewBox="0 0 28 28" width="22" height="22"><path d="M14 27C6 18 4 13 4 10a10 10 0 0 1 20 0c0 3-2 8-10 17Z" fill="#123E90"/><circle cx="14" cy="10" r="4" fill="#fff"/></svg>'
OK = '<svg viewBox="0 0 22 22" width="16" height="16"><circle cx="11" cy="11" r="9.5" fill="#dbefd6" stroke="#2e7d4f" stroke-width="2"/><path d="m6.5 11.5 3 3 6-6.5" fill="none" stroke="#2e7d4f" stroke-width="2.2" stroke-linecap="round"/></svg>'
GO = '<svg viewBox="0 0 22 22" width="16" height="16"><circle cx="11" cy="11" r="9.5" fill="#e8f0fc" stroke="#2F62C0" stroke-width="2"/><path d="M6.5 11h8m-3.2-3.4 3.4 3.4-3.4 3.4" fill="none" stroke="#2F62C0" stroke-width="2.2" stroke-linecap="round"/></svg>'

MAP = open(os.path.join(HERE, "template.html"), encoding="utf-8").read()
MAP = MAP.split('<div class="map"')[1].split("<svg", 1)[1].split("</svg>")[0]
MAP = '<svg class="mapsvg"' + MAP.replace(' id="pin"', '') + "</svg>"
MAP = MAP.replace("var(--D)", "#fde3cf").replace("var(--C)", "#fff0c7").replace("var(--B)", "#dbefd6").replace("var(--A)", "#d4ebfb") \
         .replace("var(--Dk)", "#b8612a").replace("var(--Ck)", "#a8721c").replace("var(--Bk)", "#2e7d4f").replace("var(--Ak)", "#1f87c9") \
         .replace("var(--gold)", "#c9a227").replace("var(--blu2)", "#2F62C0").replace("var(--blu)", "#123E90")

def rail(lv):
    return '<div class="rail">' + "".join(f'<span class="r{CLS[i]}">{RUBL[i]}</span>' for i in range(4)) + \
           f'<div class="mk" style="left:{(lv + .5) * 25}%">{PIN}</div></div>'

def scheda(a):
    ore = ORE.get(a["key"])
    meta = "" if ore else "Valutazione globale"
    h = f'<section class="wide scheda"><div class="shead"><h2 id="s-{a["key"]}">{e(a["nome"])}</h2><span class="meta">{meta}</span></div>'
    if a.get("sotto") and a["key"] != "comp":
        h += f'<p class="sotto">{e(a["sotto"])}</p>'
    h += '<div class="gp"><div><h4>Cosa c\'è già</h4><ul>' + "".join(f"<li>{OK}<span>{e(t)}</span></li>" for t in GIA[a["key"]]) + \
         '</ul></div><div><h4>Il passo in più</h4><ul>' + "".join(f"<li>{GO}<span>{e(t)}</span></li>" for t in PASSO[a["key"]]) + "</ul></div></div>"
    for n in a["nuclei"]:
        o = n["orig"]
        orig = [o[4] + " / " + o[3], o[2], o[1], o[0]] if len(o) == 5 else list(reversed(o))
        h += f'<table class="nt"><thead><tr><th class="first">{e(n["nome"])}</th>' + "".join(f'<th class="h{CLS[i]}">{RUBL[i]}</th>' for i in range(4)) + "</tr></thead><tbody>"
        h += '<tr><td class="first">La nostra tabella</td>' + "".join(f'<td class="old">{e(t)}</td>' for t in orig) + "</tr>"
        h += '<tr><td class="first">Griglia per la prova<br><span class="pt">1 · 2 · 3 · 4 punti</span></td>' + "".join(
            "<td>" + "<br>".join(f'<b>{e(g[0].replace("*", ""))}</b>: {e(g[1][3 - i])}' for g in n["griglia"]) + "</td>" for i in range(4)) + "</tr>"
        h += '<tr class="rub"><td class="first">Rubrica per l\'Atlante</td>' + "".join(f"<td>{e(n['rubrica'][3 - i])}</td>" for i in range(4)) + "</tr>"
        h += "</tbody></table>"
    if a["key"] == "irc":
        h += '<p class="note">Per religione la tappa raggiunta si traduce nel giudizio sintetico: Iniziale → Sufficiente, Base → Buono, Intermedio → Distinto, Avanzato → Ottimo. Nella colonna Iniziale della nostra tabella sono riportati insieme i livelli Non sufficiente e Sufficiente.</p>'
    if a["key"] == "itas":
        h += '<p class="note">Le soglie degli errori si riferiscono a un testo di circa una pagina e vanno concordate in dipartimento.</p>'
    if a["key"] == "comp":
        h += '<p class="note">Nella nostra tabella i livelli sono indicati con le lettere D, C, B, A: qui sono riportati con i nomi della certificazione delle competenze.</p>'
    return h + "</section>"

# esempio della prova
ita = next(a for a in DISC if a["key"] == "itas")
crit = [(ni, g) for ni, n in enumerate(ita["nuclei"]) for g in n["griglia"]]
score = [4, 3, 3, 2, 2, 3]
prova_rows = "".join(f'<tr><td>{e(g[0].replace("*", ""))}</td><td class="c">{score[i]}</td><td class="note2">{e(g[1][4 - score[i]])}</td></tr>' for i, (ni, g) in enumerate(crit))
prova_atl = ""
for ni, n in enumerate(ita["nuclei"]):
    s = [score[i] for i, (k, _) in enumerate(crit) if k == ni]
    lv = int(sum(s) / len(s)) - 1
    nx = f"<b>Prossima tappa:</b> {e(n['rubrica'][2 - lv])}" if lv < 3 else "<b>Ultima tappa raggiunta.</b>"
    prova_atl += f'<div class="mini"><h4>{e(n["nome"])}</h4>{rail(lv)}<p class="next">{nx}</p></div>'
voto = round(4 + (sum(score) / len(score) - 1) * 2)

T = [[0, 2, 3], [1, 1, 2], [0, 2, 2]]
tempo = '<div class="tempo">' + "".join(
    f'<div class="tcol"><h4>{m}</h4>' + "".join(f'<p class="tn">{e(n["nome"])}</p>{rail(T[i][k])}' for i, n in enumerate(ita["nuclei"])) + "</div>"
    for k, m in enumerate(["Inizio anno", "Fine primo quadrimestre", "Fine anno"])) + "</div>"
def proposta(k):
    if k == 0:
        return "<b>Punto di partenza</b><br>Nessuna proposta di voto: si osserva da dove comincia il cammino."
    lv = [t[k] for t in T]; m = sum(x + 1 for x in lv) / 3; raw = 4 + (m - 1) * 2
    low = lv.index(min(lv)); n = ita["nuclei"][low]
    return (f"<b>Proposta di voto: {round(raw)}</b><br><span class='note'>media delle tappe {m:.2f} su 4 → {raw:.1f}</span>".replace(".", ",")
            + f"<br><b>Prossimo passo</b> ({e(n['nome'].lower())}): {e(n['rubrica'][2 - lv[low]])}")
tempo = tempo.replace('<div class="tcol">', '<div class="tcol">', 1)
tempo = '<div class="tempo">' + "".join(
    f'<div class="tcol"><h4>{m}</h4>' + "".join(f'<p class="tn">{e(n["nome"])}</p>{rail(T[i][k])}' for i, n in enumerate(ita["nuclei"])) + f'<p class="next">{proposta(k)}</p></div>'
    for k, m in enumerate(["Inizio anno", "Fine primo quadrimestre", "Fine anno"])) + "</div>"

io_rows = "".join(f'<tr><td class="first">{e(DIMS[i])}</td>' + "".join(f"<td>{e(C.IO[i][3 - k])}</td>" for k in range(4)) + '<td class="box"></td></tr>' for i in range(7))

PL = [2, 1, 2, 1, 2, 2, 1]
YR = "".join(f'<div class="yq"><b>{q}</b><div class="yt"><span class="tk"></span><span class="tk"></span><span class="st p">pagellino</span><span class="tk"></span><span class="tk"></span><span class="st s">{e2}</span></div><div class="yl"><span>verifiche in itinere</span><span>metà quadrimestre</span><span>fine quadrimestre</span></div></div>' for q, e2 in [("Primo quadrimestre", "scrutinio"), ("Secondo quadrimestre", "scrutinio finale")])
PAG = "".join(f'<div class="prow"><span>{e(n["nome"])}</span>{rail(PL[i])}</div>' for i, n in enumerate(comp["nuclei"])) + f'<p class="next"><b>Partecipazione · tappa Base.</b> {e(comp["nuclei"][1]["rubrica"][2])}<br><b>Prossima tappa:</b> {e(comp["nuclei"][1]["rubrica"][1])}</p>'
TOC = [("atlante", "L'Atlante dello studente"), ("tappe", "Un livello si capisce meglio se è una tappa"), ("foto", "La griglia scatta la foto, la rubrica è la mappa"), ("anno", "Un anno con l'Atlante"),
       ("tabelle", "Le nostre tabelle, un passo più in là"), ("leggere", "Come leggere le schede")] + \
      [("s-" + a["key"], "    " + a["nome"]) for a in AREAS] + \
      [("prova", "Una prova, due letture"), ("tempo", "Dal cammino alla pagella"), ("perche", "Che cosa ci guadagniamo"),
       ("rif", "Siamo già in buona compagnia"), ("io", "Appendice · Come lavoro? Scheda di autovalutazione")]

CSS = """
@page{size:A4;margin:20mm 18mm 20mm 18mm}
@page wide{size:A4 landscape;margin:14mm 14mm 18mm 14mm}
@page cover{size:A4;margin:0}
.wide{page:wide;break-before:page}
.cover{page:cover}
*{box-sizing:border-box}
body{margin:0;font-family:"Red Hat Text","Inter","Liberation Sans",sans-serif;font-size:10.8pt;line-height:1.55;color:#1d2b45;-webkit-print-color-adjust:exact;print-color-adjust:exact}
h1,h2,h3,h4{font-family:"Red Hat Display","Inter","Liberation Sans",sans-serif;color:#123E90;letter-spacing:-.01em;margin:0}
h1{font-size:30pt;line-height:1.08;font-weight:800}
h2{font-size:18pt;line-height:1.15;font-weight:800;margin:0 0 8pt;break-after:avoid}
h3{font-size:12.5pt;margin:12pt 0 4pt;break-after:avoid}
h4{font-size:10.5pt;margin:0 0 5pt}
p{margin:0 0 8pt;text-align:left}
.lede{font-size:12pt;color:#5d6a80}
.cover{height:297mm;padding:26mm 22mm 20mm;display:flex;flex-direction:column;background:linear-gradient(#ffffff,#f5f8fc)}
.cover .k{font-size:10pt;color:#5d6a80;margin-bottom:10pt}
.cover .lede{font-size:13pt;max-width:150mm;margin-top:10pt}
.mapsvg{width:100%;height:auto;margin:16mm 0 auto}
.mapsvg text{font-family:"Red Hat Display","Inter",sans-serif;font-weight:700;font-size:21px;fill:#1d2b45}
.mapsvg .lbl{paint-order:stroke;stroke:#fff;stroke-width:5px}
.cover .foot{font-size:10pt;color:#5d6a80;border-top:1px solid #e1e7f0;padding-top:8pt}
.toc{break-before:page}
.toc ol{list-style:none;padding:0;margin:10pt 0 0}
.toc li{display:flex;gap:6pt;padding:4pt 0;border-bottom:1px solid #eef2f8;font-size:11pt}
.toc li.sub{padding-left:14pt;font-size:10pt;color:#5d6a80;border:0;padding-block:1.5pt}
.toc .dots{flex:1}
.toc .pg{font-variant-numeric:tabular-nums}
.legend{margin-top:18pt;border:1px solid #e1e7f0;border-radius:10pt;padding:12pt 14pt;background:#fff}
.sec{break-before:page}
.three{display:grid;grid-template-columns:repeat(3,1fr);gap:10pt;margin-top:10pt}
.three div{border-top:2.5pt solid #e1e7f0;padding-top:6pt;font-size:10pt}
.three b{display:block;color:#123E90;font-size:11pt}
.bike{width:100%;border-collapse:separate;border-spacing:4pt;margin:8pt 0;font-size:10pt}
.bike th{font-weight:500;color:#5d6a80;font-size:9pt;text-align:center}
.bike td{border-radius:7pt;padding:7pt 8pt;vertical-align:middle}
.bike td.h{font-weight:700;color:#123E90;width:22%;padding-left:0}
.bike .adj td:not(.h){border:1px dashed #c9d3e3;color:#5d6a80}
.d,.rd,.hd{background:#fde3cf}.c,.rc,.hc{background:#fff0c7}.b,.rb,.hb{background:#dbefd6}.a,.ra,.ha{background:#d4ebfb}
.cards{display:grid;grid-template-columns:1fr 1fr;gap:12pt;margin-top:10pt}
.card{border:1px solid #e1e7f0;border-radius:10pt;padding:12pt 14pt;background:#fff;break-inside:avoid}
.card ul{margin:5pt 0 0;padding-left:14pt}
.join{margin-top:12pt;background:#e8f0fc;border-radius:10pt;padding:10pt 14pt;color:#123E90;font-weight:500}
table.cmp{width:100%;border-collapse:collapse;margin-top:10pt;font-size:10pt}
table.cmp th,table.cmp td{border-bottom:1px solid #e1e7f0;padding:5pt 6pt;text-align:left;vertical-align:top}
table.cmp thead th{border-bottom:1.5pt solid #1d2b45;font-family:"Red Hat Display","Inter",sans-serif}
.scheda .shead{display:flex;justify-content:space-between;align-items:baseline;border-bottom:2pt solid #123E90;padding-bottom:3pt;margin-bottom:6pt}
.scheda .meta{font-size:10pt;color:#5d6a80}
.sotto{font-size:9.5pt;color:#5d6a80;margin:-2pt 0 6pt}
.gp{display:grid;grid-template-columns:1fr 1fr;gap:12pt;margin-bottom:8pt}
.gp ul{list-style:none;margin:0;padding:0}
.gp li{display:grid;grid-template-columns:18pt 1fr;font-size:9.6pt;line-height:1.4;margin-bottom:3pt}
table.nt{width:100%;border-collapse:collapse;font-size:8.3pt;line-height:1.33;margin:6pt 0 8pt;break-inside:avoid}
table.nt th,table.nt td{border:0.6pt solid #dbe2ec;padding:3.5pt 5pt;vertical-align:top;text-align:left}
table.nt thead th{font-family:"Red Hat Display","Inter",sans-serif;font-size:9pt;color:#1d2b45}
table.nt th.first{background:#123E90;color:#fff;width:15%}
table.nt td.first{font-weight:700;color:#123E90;width:15%;background:#f5f8fc}
table.nt td.old{color:#5d6a80}
table.nt tr.rub td:not(.first){background:#fbfdff;color:#1d2b45}
table.nt b{font-weight:600;color:#5d6a80}
.pt{font-weight:400;color:#5d6a80;font-size:7.5pt}
.note{font-size:8.8pt;color:#5d6a80}
.prova{display:grid;grid-template-columns:1fr 1.15fr;gap:14pt;margin-top:10pt}
.prova table{width:100%;border-collapse:collapse;font-size:9.6pt}
.prova td,.prova th{border-bottom:1px solid #e1e7f0;padding:4pt 5pt;vertical-align:top;text-align:left}
.prova td.c{text-align:center;font-weight:800;color:#123E90;font-size:11pt}
.note2{color:#5d6a80;font-size:9pt}
.rail{position:relative;display:grid;grid-template-columns:repeat(4,1fr);gap:3pt;margin-top:16pt}
.rail span{border-radius:6pt;text-align:center;font-size:8pt;font-weight:700;padding:3pt 0;color:#3b475c}
.mk{position:absolute;top:-19pt;margin-left:-11px}
.mini{margin-bottom:9pt;break-inside:avoid}
.next{font-size:9.2pt;background:#f5f8fc;border-radius:7pt;padding:6pt 8pt;margin-top:5pt}
.voto{border-top:1px solid #e1e7f0;padding-top:6pt;font-size:10pt;color:#5d6a80}
.voto b{font-size:18pt;color:#1d2b45;font-family:"Red Hat Display","Inter",sans-serif;margin-left:6pt}
.tempo{display:grid;grid-template-columns:repeat(3,1fr);gap:12pt;margin-top:8pt}
.tcol{border:1px solid #e1e7f0;border-radius:10pt;padding:10pt}
.tn{font-size:8.8pt;font-weight:700;margin:8pt 0 0}
table.io{width:100%;border-collapse:collapse;font-size:8.6pt;line-height:1.35}
table.io th,table.io td{border:0.6pt solid #dbe2ec;padding:4pt 5pt;vertical-align:top;text-align:left}
table.io td.first{font-weight:700;color:#123E90;width:14%}
table.io td.box{width:9%}
table.io tr{height:16mm}
.yr{display:grid;grid-template-columns:1fr 1fr;gap:10pt;margin:8pt 0 6pt}
.yq{border:1px solid #e1e7f0;border-radius:10pt;padding:9pt 11pt;font-size:10pt}
.yq b{color:#123E90}
.yt{position:relative;display:flex;justify-content:space-between;align-items:center;margin:9pt 4pt 3pt;height:22pt}
.yt::before{content:"";position:absolute;left:0;right:0;top:10pt;height:2pt;background:#e1e7f0}
.tk{position:relative;width:8pt;height:8pt;border-radius:50%;background:#fff;border:2pt solid #a8721c}
.st{position:relative;border-radius:10pt;padding:2pt 7pt;font-size:8pt;font-weight:700;border:1.5pt solid}
.st.p{background:#dbefd6;border-color:#2e7d4f;color:#2e7d4f}.st.s{background:#e8f0fc;border-color:#123E90;color:#123E90}
.yl{display:flex;justify-content:space-between;font-size:7.8pt;color:#5d6a80}
.docpag{border:1px solid #e1e7f0;border-radius:10pt;padding:10pt 12pt;margin-top:6pt}
.docpag .dh{display:flex;justify-content:space-between;border-bottom:1.5pt solid #123E90;padding-bottom:4pt;font-size:9pt;color:#5d6a80}
.docpag .dh b{color:#123E90;font-size:10.5pt}
.prow{display:grid;grid-template-columns:38% 1fr;gap:8pt;align-items:end;font-size:10pt;font-weight:600;margin-bottom:10pt}
.prow .rail{margin-top:22pt}
ul.refs{font-size:9.8pt;padding-left:14pt}
"""

YEAR_T = """<section class="sec"><h2 id="anno">Un anno con l'Atlante: ogni momento ha il suo strumento</h2>
<p class="lede">L'anno è diviso in due quadrimestri. In ciascuno ci sono le verifiche, il pagellino a metà periodo e lo scrutinio. Cambia poco nei tempi che conosciamo; cambia molto ciò che lo studente e la famiglia possono leggere.</p>
<div class="yr">__YR__</div>
<table class="cmp"><thead><tr><th>Momento</th><th>Strumento</th><th>Che cosa produce</th></tr></thead><tbody>
<tr><td><b>Durante il quadrimestre</b><br>verifiche in itinere</td><td>Griglia, con criteri presi dalla rubrica della disciplina</td><td>Il voto della prova, sul registro elettronico come oggi, e una posizione sulla mappa</td></tr>
<tr><td><b>A metà quadrimestre</b><br>pagellino interquadrimestrale</td><td>Rubrica delle competenze trasversali</td><td>Per la famiglia, senza voti: dove si trova lo studente e qual è la prossima tappa</td></tr>
<tr><td><b>A fine quadrimestre</b><br>scrutinio</td><td>Rubriche delle discipline</td><td>Dal profilo di tappe del periodo, il voto in pagella e il giudizio</td></tr>
<tr><td><b>Fine della terza</b></td><td>Rubriche e osservazioni del triennio</td><td>La certificazione delle competenze, con gli stessi quattro livelli</td></tr>
</tbody></table>
<h3 style="break-before:page;margin-top:0">Il pagellino diventa la prima pagina dell'Atlante</h3>
<p>È il documento che già consegniamo alle famiglie a metà quadrimestre. Con la rubrica non dice solo un giudizio: mostra la tappa raggiunta in ogni competenza e la strada per la prossima.</p>
<div class="docpag"><div class="dh"><b>Pagellino di metà quadrimestre</b><span>Studente di esempio · competenze trasversali</span></div>__PAG__</div>
</section>
"""
def page(toc_pages=None):
    tp = toc_pages or {}
    YEAR_HTML = YEAR_T.replace("__YR__", YR).replace("__PAG__", PAG)
    toc = "".join(f'<li class="{"sub" if t.startswith("    ") else ""}"><span>{e(t.strip())}</span><span class="dots"></span><span class="pg">{tp.get(k, "00")}</span></li>' for k, t in TOC)
    body = f"""
<section class="cover">
<div class="k">Studio sulla valutazione · Scuola secondaria di primo grado</div>
<h1>L'Atlante dello studente:<br>dalla tabella alla mappa</h1>
<p class="lede">Le nostre tabelle di valutazione descrivono già quattro livelli. Con un passo in più possono diventare una mappa che dice a ogni studente dove si trova e qual è la prossima tappa.</p>
{MAP}
<div class="foot">Scuola Sacra Famiglia · Orzinuovi (BS) · novembre 2026<br>Andrea Cerioli, Animatore Digitale</div>
</section>

<section class="toc"><h2>Indice</h2><ol>{toc}</ol>
<div class="legend"><h4>Come sono costruite le pagine</h4>
<p style="margin:0">Le tappe vanno sempre da sinistra a destra, dalla prima all'ultima:
<span class="d" style="padding:1pt 5pt;border-radius:4pt">Iniziale</span> <span class="c" style="padding:1pt 5pt;border-radius:4pt">Base</span> <span class="b" style="padding:1pt 5pt;border-radius:4pt">Intermedio</span> <span class="a" style="padding:1pt 5pt;border-radius:4pt">Avanzato</span>.
Il verde dell'Intermedio è la fascia che accoglie più studenti; l'azzurro dell'Avanzato è il cielo verso cui si cammina.</p></div>
</section>

<section class="sec"><h2 id="atlante">L'Atlante dello studente</h2>
<p class="lede">L'Atlante è la mappa del percorso di ogni studente: dove si trova oggi e dove sta andando. Per costruirlo ci serve un linguaggio di valutazione che descriva tappe, non soltanto gradi.</p>
<div class="three" style="grid-template-columns:repeat(2,1fr)"><div><b>Dove sei</b>il livello raggiunto, descritto con ciò che lo studente sa fare</div><div><b>Dove vai</b>la tappa successiva, scritta in modo che si capisca cosa provare</div><div><b>Come ci arrivi</b>il supporto che oggi serve e che domani non servirà più</div><div><b>Il voto resta</b>le verifiche hanno il loro voto, sul registro elettronico come oggi; la mappa lo rende leggibile</div></div>
<p style="margin-top:12pt">Questo studio parte dalla rubrica delle competenze trasversali, su cui si fonda la valutazione globale, e prosegue con le tabelle delle discipline per la valutazione in itinere, in ordine di ore settimanali. Per ciascun documento raccoglie ciò che c'è già e propone il passo in più: una griglia per le singole prove e una rubrica per l'Atlante.</p>

<h2 id="tappe" style="margin-top:22pt">Un livello si capisce meglio se è una tappa, non un aggettivo</h2>
<p>Pensiamo a come descriveremmo un ragazzo che impara ad andare in bicicletta. Tutte e due le righe sono vere, ma solo la seconda gli dice che cosa provare domani.</p>
<table class="bike"><thead><tr><th></th><th>Iniziale</th><th>Base</th><th>Intermedio</th><th>Avanzato</th></tr></thead><tbody>
<tr class="adj"><td class="h">Con un aggettivo</td><td>Pedala in modo approssimativo</td><td>Pedala in modo essenziale</td><td>Pedala in modo corretto</td><td>Pedala in modo sicuro e consapevole</td></tr>
<tr><td class="h">Con una tappa</td><td class="d">Pedala con le rotelle, con un adulto accanto</td><td class="c">Pedala senza rotelle nel cortile</td><td class="b">Va su strada, anche in curva e in salita</td><td class="a">Va in gruppo, rispettando le regole del traffico</td></tr>
</tbody></table>
<p>È lo stesso passaggio che proponiamo per le nostre tabelle: dalla qualità espressa con un aggettivo alla situazione in cui lo studente riesce e al supporto di cui ha bisogno. Una tappa ben scritta risponde a tre domande: che cosa fa lo studente, in quale situazione (nota o nuova, semplice o complessa), con quale aiuto (con la guida, con un modello, in autonomia).</p>
</section>

<section class="sec"><h2 id="foto">La griglia scatta la foto, la rubrica è la mappa</h2>
<p class="lede">Non si tratta di scegliere uno strumento contro l'altro: servono a due momenti diversi e lavorano insieme.</p>
<div class="cards">
<div class="card"><h3 style="margin-top:0">Griglia: la foto della singola prova</h3><p>Per una verifica in itinere scegliamo pochi criteri e diamo un punteggio. Ci restituisce il voto della prova, in modo rapido e uguale per tutti.</p><ul><li>serve al docente</li><li>fotografa un momento</li><li>produce il voto</li></ul></div>
<div class="card"><h3 style="margin-top:0">Rubrica: la mappa dell'Atlante</h3><p>Descrive le tappe di ogni nucleo con ciò che lo studente sa fare. Colloca ogni foto sul percorso e mostra la prossima tappa.</p><ul><li>serve allo studente e al docente</li><li>racconta un percorso</li><li>indica il passo successivo</li></ul></div>
</div>
<p class="join">La rubrica accompagna tutto l'anno; la griglia ogni singola verifica. I criteri della griglia sono presi dalla rubrica: così ogni voto si può leggere anche come una posizione sulla mappa.</p>
<table class="cmp"><thead><tr><th></th><th>Griglia</th><th>Rubrica</th></tr></thead><tbody>
<tr><td><b>A che cosa serve</b></td><td>Misurare una prova</td><td>Descrivere il percorso in un nucleo</td></tr>
<tr><td><b>Come è scritta</b></td><td>Criteri e ancore brevi, anche numeriche («2–3 errori»)</td><td>Tappe con azioni, situazioni e supporti</td></tr>
<tr><td><b>Chi la usa</b></td><td>Il docente, durante la correzione</td><td>Docente e studente, anche prima del compito</td></tr>
<tr><td><b>Che cosa restituisce</b></td><td>Il voto della prova</td><td>La tappa raggiunta e la prossima</td></tr>
<tr><td><b>Quando</b></td><td>Verifiche in itinere</td><td>Osservazione durante l'anno, compiti di realtà, autovalutazione, colloqui</td></tr>
</tbody></table>

</section>

{YEAR_HTML}<section class="wide"><h2 id="tabelle">Le nostre tabelle, un passo più in là</h2>
<p class="lede">Si parte dalla rubrica delle competenze trasversali, che sostiene la valutazione globale, e si prosegue con le discipline in ordine di ore settimanali: Italiano, Matematica, Inglese, Storia, Geografia, Spagnolo, Tecnologia, Arte e immagine, Musica, Religione cattolica.</p>
<div class="cards" style="grid-template-columns:repeat(4,1fr)">
{"".join(f'<div class="card" style="padding:8pt 10pt"><b style="color:#123E90">{e(a["nome"])}</b><br><span class="note">{"Valutazione globale · " if a["key"] == "comp" else ""}{len(a["nuclei"])} {"dimensioni" if a["key"] == "comp" else "nuclei"}</span></div>' for a in AREAS)}
</div>
<h2 id="leggere" style="margin-top:14pt">Come leggere le schede</h2>
<p>Per ogni documento la scheda si apre con due elenchi: <b>Cosa c'è già</b>, cioè ciò che le nostre tabelle fanno bene e che conserviamo, e <b>Il passo in più</b>, cioè la direzione verso l'Atlante. Seguono i nuclei. Per ciascun nucleo tre righe, con le tappe in fila da Iniziale ad Avanzato:</p>
<ul><li><b>La nostra tabella</b>: il testo in uso oggi, riportato fedelmente.</li><li><b>Griglia per la prova</b>: due criteri con ancore brevi, da cui il docente sceglie quelli utili a ogni verifica (1 punto a Iniziale, 4 ad Avanzato).</li><li><b>Rubrica per l'Atlante</b>: la stessa tappa descritta con ciò che lo studente sa fare, in quale situazione e con quale aiuto.</li></ul>
<p class="note">Le griglie e le rubriche sono proposte di lavoro: il loro posto naturale è il confronto nei dipartimenti, che le correggerà e le completerà.</p>
</section>
{"".join(scheda(a) for a in AREAS)}

<section class="wide"><h2 id="prova">Una prova, due letture: il voto e la posizione sull'Atlante</h2>
<p class="lede">Un esempio con un tema di italiano. Il docente usa la griglia; lo studente vede su quale tappa si trova per ogni nucleo e che cosa provare la volta successiva.</p>
<div class="prova">
<div><h4>La griglia della prova</h4><table><thead><tr><th>Criterio</th><th>Punti</th><th>Ancora</th></tr></thead><tbody>{prova_rows}</tbody></table>
<p class="voto">Voto della prova<b>{voto}</b></p>
<p class="note">Media dei punteggi {str(round(sum(score)/len(score), 2)).replace(".", ",")} su 4, riportata sulla scala da 4 a 10. Esempio dimostrativo.</p></div>
<div><h4>Nell'Atlante</h4>{prova_atl}</div>
</div></section>

<section class="sec"><h2 id="tempo">Dal cammino alla pagella</h2>
<p class="lede">Raccolte nel quadrimestre, le posizioni diventano un profilo. Allo scrutinio il voto nasce da dove lo studente è arrivato, non solo dalla media delle verifiche: chi è partito da lontano e ha camminato si vede.</p>
{tempo}
<p class="note" style="margin-top:6pt">Studente di esempio, Italiano scritto. Regola di esempio, da decidere in Collegio: Iniziale 1, Base 2, Intermedio 3, Avanzato 4; la media è riportata sulla scala da 4 a 10 e il consiglio di classe la conferma o la motiva.</p>

<h2 id="perche" style="break-before:page">Che cosa ci guadagniamo</h2>
<div class="three" style="gap:14pt">
<div><b>Lo studente</b>Sa dove si trova e che cosa provare dopo. Può autovalutarsi con le stesse parole che usiamo noi.</div>
<div><b>Noi docenti</b>Parliamo la stessa lingua tra discipline e tra colleghi, e le osservazioni dell'anno portano naturalmente alla certificazione delle competenze.</div>
<div><b>Le famiglie</b>Nei colloqui il discorso diventa concreto: che cosa sa fare oggi il ragazzo e qual è il prossimo passo da sostenere insieme.</div>
</div>

<h2 id="rif" style="margin-top:22pt">Siamo già in buona compagnia</h2>
<div class="cards" style="grid-template-columns:repeat(3,1fr)">
<div class="card"><h4>Certificazione delle competenze</h4><p class="note" style="color:#1d2b45">Il modello nazionale (DM 14/2024) usa già quattro livelli: A Avanzato, B Intermedio, C Base, D Iniziale. Il livello Iniziale descrive chi, guidato, svolge compiti semplici in situazioni note: un punto di partenza.</p></div>
<div class="card"><h4>Nuove Indicazioni nazionali</h4><p class="note" style="color:#1d2b45">In vigore dal 2026/27 a partire dalle classi prime (DM 221/2025), chiedono di rivedere il curricolo: l'occasione per rivedere insieme anche il modo di descrivere i livelli.</p></div>
<div class="card"><h4>Il voto resta</h4><p class="note" style="color:#1d2b45">Le discipline continuano a esprimersi in decimi, il comportamento in decimi, la religione con il giudizio sintetico. L'Atlante non cambia questi esiti: li rende leggibili.</p></div>
</div>
<h4 style="margin-top:12pt">Riferimenti</h4>
<ul class="refs">
<li>D.Lgs. 13 aprile 2017, n. 62 – valutazione e certificazione delle competenze nel primo ciclo.</li>
<li>Legge 1 ottobre 2024, n. 150 – valutazione del comportamento nella secondaria di primo grado.</li>
<li>D.M. 30 gennaio 2024, n. 14 – modelli nazionali di certificazione delle competenze.</li>
<li>D.M. 9 dicembre 2025, n. 221 e nota MIM 1312 del 12 marzo 2026 – nuove Indicazioni nazionali per il curricolo.</li>
</ul>
</section>

<section class="wide"><h2 id="io">Appendice · Come lavoro? Scheda di autovalutazione</h2>
<p style="margin-bottom:5pt">Nome ______________________ &nbsp; Classe ______ &nbsp; Data __________ &nbsp; <span class="note">Leggi le quattro frasi di ogni riga e scrivi la tappa in cui ti riconosci. Sul retro, per una riga, scrivi un esempio e che cosa farai per arrivare alla tappa successiva.</span></p>
<table class="io"><thead><tr><th>Che cosa valuto</th>{"".join(f'<th class="h{CLS[i]}">{RUBL[i]}</th>' for i in range(4))}<th>La mia tappa</th></tr></thead><tbody>{io_rows}</tbody></table>
</section>
"""
    return f'<!DOCTYPE html><html lang="it"><head><meta charset="utf-8"><title>L\'Atlante dello studente</title><style>{CSS}</style></head><body>{body}</body></html>'

def render(html_s, pdf):
    p = os.path.join(TMP, "studio.html")
    open(p, "w", encoding="utf-8").write(html_s)
    chrome = next(c for c in ["google-chrome", "chromium", "chromium-browser"] if subprocess.run(["which", c], capture_output=True).returncode == 0)
    subprocess.run([chrome, "--headless=new", "--no-sandbox", "--disable-gpu", "--no-pdf-header-footer", f"--print-to-pdf={pdf}", "file://" + p],
                   capture_output=True, check=True)

def find_pages(pdf):
    from pypdf import PdfReader
    n = len(PdfReader(pdf).pages)
    pages = [re.sub(r"\s+", " ", subprocess.run(["pdftotext", "-f", str(i), "-l", str(i), pdf, "-"], capture_output=True, text=True).stdout).strip()
             for i in range(1, n + 1)]
    res, cur = {}, 2
    for k, t in TOC:
        key = re.sub(r"\s+", " ", t.strip())
        sub = t.startswith("    ")
        for i in range(cur, n):
            txt = pages[i]
            hit = txt.startswith(key) if sub else (key in txt)
            if hit:
                res[k] = i + 1; cur = i if not sub else i + 1
                break
    return res

raw = os.path.join(TMP, "raw.pdf")
render(page(), raw)
render(page(find_pages(raw)), raw)

from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
r = PdfReader(raw); w = PdfWriter(); n = len(r.pages)
for i, pg in enumerate(r.pages):
    if i > 0:
        W, H = float(pg.mediabox.width), float(pg.mediabox.height)
        b = io.BytesIO(); c = canvas.Canvas(b, pagesize=(W, H)); c.setFont("Helvetica", 7.5); c.setFillColorRGB(.36, .42, .5)
        c.drawString(40, 22, "L'Atlante dello studente · Studio sulla valutazione · Scuola Sacra Famiglia, Orzinuovi")
        c.drawRightString(W - 40, 22, f"{i + 1} / {n}")
        c.setStrokeColorRGB(.88, .91, .94); c.setLineWidth(.6); c.line(40, 32, W - 40, 32); c.save()
        pg.merge_page(PdfReader(b).pages[0])
    w.add_page(pg)
w.add_metadata({"/Title": "L'Atlante dello studente: dalla tabella alla mappa", "/Author": "Andrea Cerioli, Animatore Digitale"})
with open(OUT, "wb") as f:
    w.write(f)
print("ok", OUT, n, "pagine")
