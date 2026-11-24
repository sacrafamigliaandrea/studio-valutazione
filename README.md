# Studio sulla valutazione: griglia o rubrica?

Studio per il Collegio docenti della Scuola secondaria di primo grado Sacra Famiglia, Orzinuovi (BS).
Analizza i 12 strumenti di valutazione in uso (la rubrica delle competenze trasversali e le 11 tabelle disciplinari per la valutazione in itinere) e propone per ciascuno due evoluzioni: una **griglia** per misurare le prove e una **rubrica** per descrivere i livelli e indicare il passo successivo.

## Contenuto

- `index.html` – la pagina da presentare: un unico file, senza dipendenze oltre ai font Google. Si apre direttamente nel browser o si pubblica con GitHub Pages.
- `sorgenti/` – dati e script che generano la pagina.
  - `disc_data.py` – trascrizioni dei documenti disciplinari, griglie e rubriche riscritte, diagnosi.
  - `competenze.py` – rubrica delle competenze trasversali: originale, griglia, rubrica, versione per studenti.
  - `analisi.py` – calcola gli indicatori (somiglianza tra livelli, parole di grado, formulazione del livello più basso) e scrive `metrics.json`.
  - `template.html` – struttura, stile e interazioni della pagina.
  - `build.py` – unisce dati e template e rigenera `index.html`.
- `materiali/` – il file Excel con griglia e rubrica delle competenze trasversali e lo studio PDF sulla sola rubrica delle competenze.

## Rigenerare la pagina

```bash
python3 sorgenti/analisi.py
python3 sorgenti/build.py
```

Per modificare un descrittore si cambia `disc_data.py` o `competenze.py` e si rilanciano i due comandi: gli indicatori vengono ricalcolati.

## Pubblicare con GitHub Pages

Settings → Pages → Deploy from a branch → `main`, cartella `/ (root)`.

---
Andrea Cerioli, Animatore Digitale
