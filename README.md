# Studio sulla valutazione: griglia o rubrica?

Studio per il Collegio docenti della Scuola secondaria di primo grado Sacra Famiglia, Orzinuovi (BS).
Accompagna il passaggio della valutazione verso un'ottica da rubrica, al servizio dell'**Atlante dello studente**: la mappa di dove lo studente si trova e di dove sta andando. Parte dalla rubrica delle competenze trasversali (valutazione globale) e prosegue con le 11 tabelle disciplinari per la valutazione in itinere, in ordine di ore settimanali; per ciascuna mostra la tabella attuale, una **griglia** per le singole prove e una **rubrica** per l'Atlante.

## Contenuto

- `studio-valutazione.pdf` – lo studio completo per una lettura approfondita, scaricabile dalla pagina.
- `index.html` – la pagina da presentare: un unico file, senza dipendenze oltre ai font Google. Si apre direttamente nel browser o si pubblica con GitHub Pages.
- `sorgenti/` – dati e script che generano la pagina.
  - `disc_data.py` – trascrizioni dei documenti disciplinari, griglie e rubriche riscritte, diagnosi.
  - `competenze.py` – rubrica delle competenze trasversali: originale, griglia, rubrica, versione per studenti.
  - `atlante_testi.py` – per ogni documento, che cosa c'è già e il passo in più.
  - `analisi.py` – indicatori di lavoro sui descrittori (non mostrati nella pagina), scrive `metrics.json`.
  - `template.html` – struttura, stile e interazioni della pagina.
  - `build.py` – unisce dati e template e rigenera `index.html`.
  - `build_pdf.py` – rigenera `studio-valutazione.pdf` dagli stessi dati (serve Chrome o Chromium).
- `materiali/` – il file Excel con griglia e rubrica delle competenze trasversali.

## Rigenerare la pagina

```bash
python3 sorgenti/build.py
python3 sorgenti/build_pdf.py
```

Per modificare un descrittore si cambia `disc_data.py` o `competenze.py`; per i commenti di ogni documento `atlante_testi.py`.

## Pubblicare con GitHub Pages

Settings → Pages → Deploy from a branch → `main`, cartella `/ (root)`.

---
Andrea Cerioli, Animatore Digitale
