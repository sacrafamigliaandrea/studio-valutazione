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
        h += '<tr class="nowr"><td class="first">Come valutiamo oggi</td>' + "".join(f'<td class="old">{e(t)}</td>' for t in orig) + "</tr>"
        h += '<tr class="rub"><td class="first">Con l\'Atlante</td>' + "".join(
            "<td>" + e(n['rubrica'][3 - i]) + '<div class="inv"><b>Nella verifica · ' + str(i + 1) + (' punti' if i else ' punto') + '</b>' + '<br>'.join(e(g[0].replace('*', '')) + ': ' + e(g[1][3 - i]) for g in n['griglia']) + '</div></td>' for i in range(4)) + '</tr>'
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

TL = [[1, 2, 2, 2], [1, 1, 2, 2], [2, 2, 2, 3], [1, 1, 1, 2], [1, 2, 2, 3], [1, 1, 2, 2], [0, 1, 1, 2]]
PL = [x[0] for x in TL]
YR = "".join(f'<div class="yq"><b>{q}</b><div class="yt"><span class="tk"></span><span class="tk"></span><span class="st p">pagellino · {mm}</span><span class="tk"></span><span class="tk"></span><span class="st p">{e2}</span></div><div class="yl"><span>verifiche · rubrica disciplinare</span><span>1ª misura</span><span>2ª misura</span></div></div>' for q, e2, mm in [("Primo quadrimestre", "scrutinio", "novembre"), ("Secondo quadrimestre", "scrutinio finale", "aprile")])
PAG_NOW = '<div class="docpag now"><div class="dh"><b>Pagellino di novembre</b><span class="pill now">Come valutiamo oggi</span></div>' + "".join(f'<div class="prow2"><b>{e(n["nome"])}</b><span class="lt">{["D","C","B","A"][PL[i]]} · {["5-4","7-6","9-8","10"][PL[i]]}</span><span>{e(n["orig"][3 - PL[i]])}</span></div>' for i, n in enumerate(comp["nuclei"])) + '</div>'
PAG = "".join(f'<div class="prow"><span>{e(n["nome"])}</span>{rail(PL[i])}</div>' for i, n in enumerate(comp["nuclei"])) + f'<p class="next"><b>Gestione delle emozioni · tappa Iniziale.</b> {e(comp["nuclei"][6]["rubrica"][3])}<br><b>Prossima tappa:</b> {e(comp["nuclei"][6]["rubrica"][2])}</p>'
TOC = [("atlante", "L'Atlante dello studente"), ("c1", "§Tappa 1 · Il nostro anno"), ("anno", "    Il nostro anno, oggi e con l'Atlante"), ("c2", "§Tappa 2 · Come si scrive una tappa"), ("tappe", "    Un livello si capisce meglio se è una tappa"), ("foto", "    Nella verifica il voto resta; con l'Atlante si aggiunge la mappa"), ("c3", "§Tappa 3 · Le nostre rubriche"),
       ("tabelle", "    Le nostre tabelle, un passo più in là"), ("leggere", "    Come leggere le schede")] + \
      [("s-" + a["key"], "        " + a["nome"]) for a in AREAS] + \
      [("prova", "    Una verifica, oggi e con l'Atlante"), ("c4", "§Tappa 4 · Il cammino dello studente"), ("pagellino", "    Il pagellino diventa la prima pagina dell'Atlante"), ("tempo", "    Due misure a quadrimestre, un cammino nell'anno"), ("perche", "    Che cosa ci guadagniamo"),
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
.toc li{display:flex;gap:6pt;padding:3pt 0;border-bottom:1px solid #eef2f8;font-size:11pt}
.toc li.sub{padding-left:16pt;font-size:10.5pt;border-bottom:1px solid #eef2f8}
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
.prow{display:grid;grid-template-columns:34% 1fr;gap:8pt;align-items:end;font-size:9pt;font-weight:600;margin-bottom:3pt}
.prow .rail{margin-top:17pt}
.heat{width:100%;border-collapse:separate;border-spacing:3pt;font-size:9.5pt;margin-top:8pt}
.heat th{font-weight:600;font-size:9pt;text-align:center;color:#1d2b45}
.heat td{text-align:center;border-radius:6pt;padding:6pt 4pt;font-weight:600;color:#3b475c}
.heat td.first{text-align:left;color:#123E90;background:none;font-weight:700}
.heat b{color:#123E90}
.divider{break-before:page;display:flex;flex-direction:column;padding-top:40mm}
.divider .dlh{margin-top:16pt;font-size:10pt;color:#5d6a80;margin-bottom:0}
.divider .dtag{font-size:11pt;color:#5d6a80;margin-bottom:8pt}
.divider svg.route{width:70mm;margin-bottom:14pt}
.divider h1{font-size:34pt;margin-bottom:10pt}
.divider .lede{font-size:14pt;max-width:140mm}
.divider ul.dl{margin-top:14pt;padding-left:16pt;font-size:12pt}
.divider .dbar{position:absolute;left:-18mm;right:-18mm;bottom:-20mm;height:42mm;border-top:3pt solid}
.routebox{margin-top:8pt}.routebox svg{width:100%}
.rlab{display:grid;grid-template-columns:repeat(4,1fr);gap:6pt;text-align:center;font-size:9.4pt;margin-top:4pt}
.rlab b{display:block;font-size:10.5pt}.rlab span{color:#5d6a80}
.toc li.ch{font-weight:700;color:#123E90;border-bottom:0;padding-top:9pt}
.toc li.ch i{width:10pt;height:10pt;border-radius:50%;border:2pt solid;display:inline-block;margin-top:3pt}
.toc li.sub2{padding-left:30pt;font-size:9.5pt;color:#5d6a80;border:0;padding-block:1pt}
.tlwrap{border:1px solid #e1e7f0;border-radius:9pt;padding:7pt 8pt;margin:6pt 0 2pt}
.tl{display:grid;grid-template-columns:22mm repeat(10,1fr);column-gap:3pt;row-gap:4pt;align-items:stretch}
.mon{text-align:center;font-size:8pt;color:#5d6a80;border-bottom:0.6pt solid #e1e7f0;padding-bottom:2pt}
.quad{border-radius:6pt;text-align:center;font-weight:700;font-size:8.8pt;padding:2pt;color:#123E90;background:#e8f0fc}
.q1{grid-column:2/7}.q2{grid-column:7/12}
.lane-h{grid-column:1;grid-row:span 2;display:flex;align-items:center;font-weight:800;font-size:10pt;border-radius:7pt;padding:5pt;margin-top:5pt}
.lane-h.now{background:#eef1f5;color:#4a5568}.lane-h.new{background:#dbefd6;color:#2e7d4f}
.flow{grid-column:2/12;border-radius:20pt;padding:3pt 9pt;font-size:8.6pt;margin-top:5pt}
.flow.now{background:#eef1f5;color:#4a5568}.flow.new{background:#fff3d6;color:#7a5413;border:1pt solid #e9c97f}
.ev{font-size:8.2pt;line-height:1.3;border-radius:7pt;padding:4pt 6pt;align-self:start}
.ev b{display:block;font-size:8.6pt}
.ev.now{background:#f4f6f9;border:0.8pt dashed #c3cbd8;color:#4a5568}
.ev.new{background:#dbefd6;border:1pt solid #2e7d4f;color:#1f3b2b}.ev.new b{color:#2e7d4f}
.tl-h{display:none}
table.cmp.sm{font-size:8.6pt;margin-top:4pt}table.cmp.sm td,table.cmp.sm th{padding:2.5pt 5pt}
.pill{display:inline-block;border-radius:20pt;padding:1.5pt 8pt;font-weight:700;font-size:9pt;white-space:nowrap}
.pill.now{background:#eef1f5;color:#4a5568;border:1pt dashed #b9c3d1}
.pill.new{background:#dbefd6;color:#2e7d4f;border:1pt solid #2e7d4f}
.card.now{background:#f7f9fb;border:1pt dashed #c3cbd8}.card.new{border:1pt solid #2e7d4f}
table.nt tr.nowr td:not(.first){background:#f7f9fb}
table.nt .inv{margin-top:4pt;border-top:0.6pt dashed #dbe2ec;padding-top:3pt;color:#5d6a80;font-size:7.6pt}
table.nt .inv b{display:block;color:#1d2b45;font-weight:600}
.pg2{display:grid;grid-template-columns:1fr 1fr;gap:12pt}
.prow2{display:grid;grid-template-columns:30% 14% 1fr;gap:6pt;font-size:8.6pt;padding:4pt 0;border-bottom:0.6pt solid #e1e7f0}
.prow2 .lt{font-weight:800;text-align:center;background:#eef1f5;border-radius:5pt;color:#4a5568;height:fit-content}
.docpag.now{background:#f7f9fb;border:1pt dashed #c3cbd8}
ul.refs{font-size:9.8pt;padding-left:14pt}
"""

YEAR_T = """<section class="wide"><h2 id="anno">Il nostro anno, oggi e con l'Atlante</h2>
<p class="lede">Due quadrimestri, il pagellino a novembre e ad aprile, lo scrutinio a fine periodo. Sopra, come lavoriamo oggi; sotto, la proposta: stessi tempi, strumenti che dicono allo studente dove si trova e dove sta andando.</p>
<div class="tlwrap">
<div class="tl" role="table" aria-label="L'anno scolastico, oggi e con l'Atlante">
<div class="tl-h"></div>
<div class="mon" style="grid-column:2">set</div><div class="mon" style="grid-column:3">ott</div><div class="mon" style="grid-column:4">nov</div><div class="mon" style="grid-column:5">dic</div><div class="mon" style="grid-column:6">gen</div><div class="mon" style="grid-column:7">feb</div><div class="mon" style="grid-column:8">mar</div><div class="mon" style="grid-column:9">apr</div><div class="mon" style="grid-column:10">mag</div><div class="mon" style="grid-column:11">giu</div>
<div class="tl-h"></div><div class="quad q1">Primo quadrimestre</div><div class="quad q2">Secondo quadrimestre</div>

<div class="lane-h now">Oggi</div>
<div class="flow now">Verifiche con voto sul registro elettronico · tabelle disciplinari per la valutazione in itinere</div>
<div class="tl-h"></div>
<div class="ev now" style="grid-column:3/5"><b>Pagellino di novembre</b>competenze trasversali: livelli A–D legati a fasce di voto, frasi per il giudizio</div>
<div class="ev now" style="grid-column:5/7"><b>Scrutinio</b>voti in pagella e giudizio</div>
<div class="ev now" style="grid-column:8/10"><b>Pagellino di aprile</b>come a novembre</div>
<div class="ev now" style="grid-column:10/12"><b>Scrutinio finale</b>voti in pagella e giudizio</div>

<div class="lane-h new">Con l'Atlante</div>
<div class="flow new">Verifiche: si corregge con i criteri della rubrica della disciplina · il voto va sul registro, come oggi · la rubrica dice la tappa raggiunta e la prossima</div>
<div class="tl-h"></div>
<div class="ev new" style="grid-column:3/5"><b>Pagellino di novembre · 1ª misura</b>mappa delle competenze trasversali: tappa raggiunta e prossima tappa, senza voti</div>
<div class="ev new" style="grid-column:5/7"><b>Scrutinio · 2ª misura</b>la stessa mappa mostra il cammino; voti dalle verifiche, come oggi</div>
<div class="ev new" style="grid-column:8/10"><b>Pagellino di aprile · 3ª misura</b>nuova posizione sulla mappa e prossima tappa</div>
<div class="ev new" style="grid-column:10/12"><b>Scrutinio finale · 4ª misura</b>il cammino dell'anno; voti dalle verifiche; in terza, base della certificazione</div>
</div>
</div>
<p class="note" style="margin:4pt 0 8pt">I tempi non cambiano. Cambia ciò che ogni momento restituisce allo studente e alla famiglia.</p>
<table class="cmp sm"><thead><tr><th>Momento</th><th>Strumento</th><th>Che cosa produce</th></tr></thead><tbody>
<tr><td><b>Durante il quadrimestre</b><br>verifiche e lavoro in classe</td><td>La rubrica della disciplina: con i suoi criteri si dà il voto, con le sue tappe lo si spiega</td><td>Il voto sul registro elettronico e, per lo studente, la tappa raggiunta nella disciplina e la prossima</td></tr>
<tr><td><b>Novembre e aprile</b><br>pagellino interquadrimestrale</td><td>Rubrica delle competenze trasversali</td><td>La prima misura: per la famiglia, senza voti, dove si trova lo studente e qual è la prossima tappa</td></tr>
<tr><td><b>A fine quadrimestre</b><br>scrutinio</td><td>La stessa rubrica delle competenze trasversali</td><td>La seconda misura, che mostra il cammino fatto dal pagellino; accanto, i voti delle discipline, che vengono dalle verifiche come oggi</td></tr>
<tr><td><b>Fine della terza</b></td><td>Le misure dei tre anni</td><td>La base della certificazione delle competenze, con gli stessi quattro livelli</td></tr>
</tbody></table>
</section>
"""
PAG_T = """<section class="wide"><h2 id="pagellino">Il pagellino diventa la prima pagina dell'Atlante</h2>
<p>È il documento che già consegniamo alle famiglie a novembre e ad aprile. Con la rubrica non dice solo un giudizio: mostra la tappa raggiunta in ogni competenza e la strada per la prossima. A fine quadrimestre la stessa pagina viene compilata di nuovo.</p>
<div class="pg2">__PAGNOW__<div class="docpag"><div class="dh"><b>Pagellino di novembre</b><span class="pill new">Con l'Atlante</span></div>__PAG__</div></div>
</section>"""
MOMS = ["Novembre<br><span class='note'>pagellino</span>", "Fine 1° quadrimestre<br><span class='note'>scrutinio</span>", "Aprile<br><span class='note'>pagellino</span>", "Fine anno<br><span class='note'>scrutinio finale</span>"]
def cammino():
    h = '<table class="heat"><thead><tr><th>Competenza</th>' + "".join(f"<th>{m}</th>" for m in MOMS) + "</tr></thead><tbody>"
    for i, n in enumerate(comp["nuclei"]):
        h += f'<tr><td class="first">{e(n["nome"])}</td>'
        for k in range(4):
            lv = TL[i][k]; up = k > 0 and lv > TL[i][k - 1]
            h += f'<td class="{CLS[lv]}">{RUBL[lv]}{" <b>↑</b>" if up else ""}</td>'
        h += "</tr>"
    low = min(range(7), key=lambda i: TL[i][3]); n = comp["nuclei"][low]; lv = TL[low][3]
    return h + f'</tbody></table><p class="next"><b>A fine anno, prossima tappa in {e(n["nome"].lower())}:</b> {e(n["rubrica"][2 - lv])}</p>'
CH = [("c1", "Il nostro anno", "Due quadrimestri, tre momenti, uno strumento per ciascuno.", "#fde3cf", "#b8612a"),
      ("c2", "Come si scrive una tappa", "Dalla qualità detta con un aggettivo alla situazione in cui lo studente riesce: oggi e con l'Atlante.", "#fff0c7", "#a8721c"),
      ("c3", "Le nostre rubriche", "Ogni tabella e ogni verifica, oggi e con l'Atlante.", "#dbefd6", "#2e7d4f"),
      ("c4", "Il cammino dello studente", "Il pagellino e lo scrutinio: due misure che, messe in fila, raccontano il percorso.", "#d4ebfb", "#1f87c9")]
def route(cur=None, big=False):
    w, r = (520, 30) if big else (300, 13)
    xs = [r + 4 + i * (w - 2 * r - 8) / 3 for i in range(4)]
    h = f'<svg viewBox="0 0 {w} {2*r+8}" class="route{"big" if big else ""}"><path d="M{xs[0]} {r+4} H{xs[3]}" stroke="#c9d6ea" stroke-width="{4 if big else 2.5}" stroke-dasharray="{"8 8" if big else "4 5"}"/>'
    for i, c in enumerate(CH):
        on = cur is None or cur == i
        rr = r if (big or cur == i) else r * .62
        h += f'<circle cx="{xs[i]}" cy="{r+4}" r="{rr}" fill="{c[3] if on else "#eef2f8"}" stroke="{c[4] if on else "#c9d6ea"}" stroke-width="{4 if big else 2.5}"/>'
        if big:
            h += f'<text x="{xs[i]}" y="{r+13}" text-anchor="middle" font-size="26" font-weight="800" fill="{c[4]}" font-family="Red Hat Display, Inter, sans-serif">{i+1}</text>'
    return h + "</svg>"
def divider(i, items):
    c = CH[i]
    return (f'<section class="divider"><div class="dtag">Tappa {i+1} di 4</div>{route(i)}<h1 id="{c[0]}" style="color:{c[4]}">{e(c[1])}</h1>'
            f'<p class="lede">{e(c[2])}</p><p class="dlh">In questa tappa</p><ul class="dl">' + "".join(f"<li>{e(x)}</li>" for x in items) + '</ul></section>')
def page(toc_pages=None):
    tp = toc_pages or {}
    CAMMINO = cammino()
    PAG_HTML = PAG_T.replace("__PAG__", PAG).replace("__PAGNOW__", PAG_NOW)
    YEAR_HTML = YEAR_T.replace("__YR__", YR).replace("__PAG__", PAG)
    ROUTE = '<div class="routebox">' + route(None, True) + '<div class="rlab">' + "".join(f'<div><b style="color:{c[4]}">{e(c[1])}</b><span>{e(c[2])}</span></div>' for c in CH) + '</div></div>'
    def tocli(k, t):
        if t.startswith("§"):
            c = CH[int(k[1]) - 1]
            return f'<li class="ch"><i style="background:{c[3]};border-color:{c[4]}"></i><span>{e(t[1:])}</span><span class="dots"></span><span class="pg">{tp.get(k, "00")}</span></li>'
        cls = "sub2" if t.startswith("        ") else ("sub" if t.startswith("    ") else "")
        return f'<li class="{cls}"><span>{e(t.strip())}</span><span class="dots"></span><span class="pg">{tp.get(k, "00")}</span></li>'
    toc = "".join(tocli(k, t) for k, t in TOC)
    body = f"""
<section class="cover">
<div class="k">Studio sulla valutazione · Scuola secondaria di primo grado</div>
<h1>L'Atlante dello studente:<br>dalla tabella alla mappa</h1>
<p class="lede">Le nostre tabelle di valutazione descrivono già quattro livelli. Con un passo in più possono diventare una mappa che dice a ogni studente dove si trova e qual è la prossima tappa.</p>
{MAP}
<div class="foot">Scuola Sacra Famiglia · Orzinuovi (BS) · novembre 2026<br>Andrea Cerioli, Animatore Digitale</div>
</section>

<section class="toc"><h2>Indice</h2><ol>{toc}</ol>

</section>

<section class="sec"><h2 id="atlante">L'Atlante dello studente</h2>
<p class="lede">L'Atlante è la mappa del percorso di ogni studente: dove si trova oggi e dove sta andando. Per costruirlo ci serve un linguaggio di valutazione che descriva tappe, non soltanto gradi.</p>
<div class="three" style="grid-template-columns:repeat(2,1fr)"><div><b>Dove sei</b>il livello raggiunto, descritto con ciò che lo studente sa fare</div><div><b>Dove vai</b>la tappa successiva, scritta in modo che si capisca cosa provare</div><div><b>Come ci arrivi</b>il supporto che oggi serve e che domani non servirà più</div><div><b>Il voto resta</b>le verifiche e la pagella mantengono i loro voti, come oggi; la rubrica li spiega</div></div>
<p style="margin-top:12pt">Questo studio parte dalla rubrica delle competenze trasversali, su cui si fonda la valutazione globale, e prosegue con le tabelle delle discipline per la valutazione in itinere, in ordine di ore settimanali. Per ciascun documento mette a confronto come valutiamo oggi e come si valuta con l'Atlante.</p>

<h2 style="margin-top:20pt">Il percorso di questo studio</h2><p>Quattro tappe, come quelle dello studente: si parte da ciò che facciamo già e si arriva al cammino che l'Atlante rende visibile.</p>{ROUTE}<div class="legend" style="margin-top:12pt"><h4>Come sono costruite le pagine</h4>
<p style="margin:0">Le tappe vanno sempre da sinistra a destra, dalla prima all'ultima:
<span class="d" style="padding:1pt 5pt;border-radius:4pt">Iniziale</span> <span class="c" style="padding:1pt 5pt;border-radius:4pt">Base</span> <span class="b" style="padding:1pt 5pt;border-radius:4pt">Intermedio</span> <span class="a" style="padding:1pt 5pt;border-radius:4pt">Avanzato</span>.
Il verde dell'Intermedio è la fascia che accoglie più studenti; l'azzurro dell'Avanzato è il cielo verso cui si cammina.</p></div></section>
{divider(0, ["Il nostro anno, oggi e con l'Atlante", "Quale strumento in ogni momento"])}
{YEAR_HTML}
{divider(1, ["Un livello si capisce meglio se è una tappa", "Nella verifica il voto resta; con l'Atlante si aggiunge la mappa"])}
<section class="sec"><h2 id="tappe" style="margin-top:22pt">Un livello si capisce meglio se è una tappa, non un aggettivo</h2>
<p>Pensiamo a come descriveremmo un ragazzo che impara ad andare in bicicletta. Oggi diremmo quanto bene pedala; con l'Atlante diciamo dove riesce a pedalare e con quale aiuto. Tutte e due le righe sono vere, ma solo la seconda gli dice che cosa provare domani.</p>
<table class="bike"><thead><tr><th></th><th>Iniziale</th><th>Base</th><th>Intermedio</th><th>Avanzato</th></tr></thead><tbody>
<tr class="adj"><td class="h"><span class="pill now">Come descriviamo oggi</span></td><td>Pedala in modo approssimativo</td><td>Pedala in modo essenziale</td><td>Pedala in modo corretto</td><td>Pedala in modo sicuro e consapevole</td></tr>
<tr><td class="h"><span class="pill new">Con l'Atlante</span></td><td class="d">Pedala con le rotelle, con un adulto accanto</td><td class="c">Pedala senza rotelle nel cortile</td><td class="b">Va su strada, anche in curva e in salita</td><td class="a">Va in gruppo, rispettando le regole del traffico</td></tr>
</tbody></table>
<p>È lo stesso passaggio che proponiamo per le nostre tabelle: dalla qualità espressa con un aggettivo alla situazione in cui lo studente riesce e al supporto di cui ha bisogno. Una tappa ben scritta risponde a tre domande: che cosa fa lo studente, in quale situazione (nota o nuova, semplice o complessa), con quale aiuto (con la guida, con un modello, in autonomia).</p>
</section>
<section class="sec"><h2 id="foto">Nella verifica il voto resta; con l'Atlante si aggiunge la mappa</h2>
<p class="lede">Il voto è la foto della verifica. Oggi la foto resta da sola; con l'Atlante viene collocata sulla mappa della disciplina, e lo studente vede dove si trova e dove andare.</p>
<div class="cards">
<div class="card now"><span class="pill now">Come valutiamo oggi</span><h3 style="margin-top:6pt">La verifica produce un voto</h3><p>La tabella della disciplina descrive il livello con parole come completo, corretto, essenziale.</p><ul><li>il voto va sul registro elettronico</li><li>il livello è detto con un aggettivo</li><li>lo studente sa quanto, ma non sempre che cosa fare dopo</li></ul></div>
<div class="card new"><span class="pill new">Con l'Atlante</span><h3 style="margin-top:6pt">La verifica produce lo stesso voto e una posizione sulla mappa</h3><p>I criteri con cui si corregge sono presi dalla rubrica della disciplina, che colloca il risultato su una tappa e indica la prossima.</p><ul><li>il voto va sul registro elettronico, come oggi</li><li>il livello è una tappa: che cosa fa lo studente, dove, con quale aiuto</li><li>lo studente sa dove si trova e che cosa provare</li></ul></div>
</div>
<p class="join">Non sono due strumenti tra cui scegliere: con l'Atlante correggere e orientare diventano un unico gesto.</p>
<table class="cmp"><thead><tr><th></th><th><span class="pill now">Come valutiamo oggi</span></th><th><span class="pill new">Con l'Atlante</span></th></tr></thead><tbody>
<tr><td><b>Nella verifica</b></td><td>Un voto</td><td>Lo stesso voto, con criteri presi dalla rubrica</td></tr>
<tr><td><b>Come è descritto il livello</b></td><td>Con aggettivi: completo, corretto, essenziale</td><td>Con una tappa: azione, situazione, supporto</td></tr>
<tr><td><b>Che cosa riceve lo studente</b></td><td>Il voto</td><td>Il voto, la tappa raggiunta e la prossima</td></tr>
<tr><td><b>Al pagellino</b></td><td>Lettere A–D legate a fasce di voto e frasi</td><td>La mappa delle competenze trasversali, senza voti</td></tr>
<tr><td><b>Allo scrutinio</b></td><td>Voti e giudizio</td><td>Voti dalle verifiche, come oggi, e la stessa mappa che mostra il cammino</td></tr>
</tbody></table>
</section>
{divider(2, ["Le nostre tabelle, un passo più in là: dalle competenze trasversali alle discipline", "Una verifica, oggi e con l'Atlante"])}
<section class="wide"><h2 id="tabelle">Le nostre tabelle, un passo più in là</h2>
<p class="lede">Si parte dalla rubrica delle competenze trasversali, che sostiene la valutazione globale, e si prosegue con le discipline in ordine di ore settimanali: Italiano, Matematica, Inglese, Storia, Geografia, Spagnolo, Tecnologia, Arte e immagine, Musica, Religione cattolica.</p>
<div class="cards" style="grid-template-columns:repeat(4,1fr)">
{"".join(f'<div class="card" style="padding:8pt 10pt"><b style="color:#123E90">{e(a["nome"])}</b><br><span class="note">{"Valutazione globale · " if a["key"] == "comp" else ""}{len(a["nuclei"])} {"dimensioni" if a["key"] == "comp" else "nuclei"}</span></div>' for a in AREAS)}
</div>
<h2 id="leggere" style="margin-top:14pt">Come leggere le schede</h2>
<p>Per ogni documento la scheda si apre con due elenchi: <b>Cosa c'è già</b>, cioè ciò che le nostre tabelle fanno bene e che conserviamo, e <b>Il passo in più</b>, cioè la direzione verso l'Atlante. Seguono i nuclei, ciascuno con due righe e le tappe in fila da Iniziale ad Avanzato:</p>
<ul><li><span class="pill now">Come valutiamo oggi</span> il testo della tabella in uso, riportato fedelmente.</li><li><span class="pill new">Con l'Atlante</span> la stessa tappa descritta con ciò che lo studente sa fare, in quale situazione e con quale aiuto; sotto, «Nella verifica», i criteri con cui la tappa si riconosce in una prova e diventa punteggio (1 punto a Iniziale, 4 ad Avanzato).</li></ul>
<p class="note">Le descrizioni con l'Atlante sono proposte di lavoro: il loro posto naturale è il confronto nei dipartimenti, che le correggerà e le completerà.</p>
</section>
{"".join(scheda(a) for a in AREAS)}

<section class="wide"><h2 id="prova">Una verifica, oggi e con l'Atlante</h2>
<p class="lede">Un esempio con un tema di italiano. Il docente corregge con i criteri della rubrica e assegna il voto. Oggi lo studente riceve il voto; con l'Atlante riceve lo stesso voto e, per ogni nucleo, la tappa raggiunta e che cosa provare la volta successiva.</p>
<div class="prova">
<div><h4>I criteri della verifica</h4><table><thead><tr><th>Criterio</th><th>Punti</th><th>Ancora</th></tr></thead><tbody>{prova_rows}</tbody></table>
<p class="voto"><span class="pill now">Come valutiamo oggi</span> lo studente riceve il voto<b>{voto}</b></p>
<p class="note">Media dei punteggi {str(round(sum(score)/len(score), 2)).replace(".", ",")} su 4, riportata sulla scala da 4 a 10. Esempio dimostrativo.</p></div>
<div><p style="margin:0 0 4pt"><span class="pill new">Con l'Atlante</span> lo stesso voto, {voto}, e la mappa</p>{prova_atl}</div>
</div></section>

{divider(3, ["Il pagellino diventa la prima pagina dell'Atlante", "Due misure a quadrimestre, un cammino nell'anno", "Che cosa ci guadagniamo"])}
{PAG_HTML}
<section class="sec"><h2 id="tempo">Due misure a quadrimestre, un cammino nell'anno</h2>
<p class="lede">Il pagellino e lo scrutinio usano la stessa rubrica. Messe in fila, le quattro misure dell'anno raccontano il cammino dello studente: dove è partito, dove è salito, dove c'è ancora strada da fare.</p>
{CAMMINO}
<p class="note" style="margin-top:6pt">Studente di esempio, competenze trasversali. La freccia segna la competenza in cui lo studente è salito di tappa rispetto alla misura precedente.</p>
</section>
<section class="sec"><h2 id="perche" style="break-before:page">Che cosa ci guadagniamo</h2>
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
        key = re.sub(r"\s+", " ", t.strip().lstrip("§"))
        if t.startswith("§"): key = "Tappa " + key.split("Tappa ")[1].split(" ·")[0] + " di 4"
        sub = t.startswith("        ")
        for i in range(cur, n):
            txt = pages[i]
            if not t.startswith("§") and re.match(r"Tappa \d di 4", txt):
                continue
            hit = txt.startswith(key) if sub else (key in txt)
            if hit:
                res[k] = i + 1; cur = i if not sub else i + 1
                break
    return res

raw = os.path.join(TMP, "raw.pdf")
render(page(), raw)
FP = find_pages(raw)
render(page(FP), raw)
FP = find_pages(raw)
CHSTART = [(FP.get(c[0], 999), c) for c in CH]

from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
r = PdfReader(raw); w = PdfWriter(); n = len(r.pages)
for i, pg in enumerate(r.pages):
    if i > 0:
        W, H = float(pg.mediabox.width), float(pg.mediabox.height)
        b = io.BytesIO(); c = canvas.Canvas(b, pagesize=(W, H)); c.setFont("Helvetica", 7.5); c.setFillColorRGB(.36, .42, .5)
        cur = [cc for (pg0, cc) in CHSTART if pg0 <= i + 1 and (i + 1) < FP.get("rif", 999)]
        if cur:
            cc = cur[-1]; k = CH.index(cc)
            col = tuple(int(cc[4][j:j + 2], 16) / 255 for j in (1, 3, 5)); fill = tuple(int(cc[3][j:j + 2], 16) / 255 for j in (1, 3, 5))
            c.setFillColorRGB(*fill); c.setStrokeColorRGB(*col); c.setLineWidth(1.2); c.circle(44, 24.5, 3.6, stroke=1, fill=1)
            c.setFillColorRGB(.36, .42, .5); c.drawString(53, 22, f"Tappa {k + 1} di 4 · {cc[1]}")
        else:
            c.drawString(40, 22, "L'Atlante dello studente · Studio sulla valutazione · Scuola Sacra Famiglia, Orzinuovi")
        c.drawRightString(W - 40, 22, f"{i + 1} / {n}")
        c.setStrokeColorRGB(.88, .91, .94); c.setLineWidth(.6); c.line(40, 32, W - 40, 32); c.save()
        pg.merge_page(PdfReader(b).pages[0])
    w.add_page(pg)
w.add_metadata({"/Title": "L'Atlante dello studente: dalla tabella alla mappa", "/Author": "Andrea Cerioli, Animatore Digitale"})
with open(OUT, "wb") as f:
    w.write(f)
print("ok", OUT, n, "pagine")
