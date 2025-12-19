# Mondoffice – Simulatore Strategia Google Ads

Una dashboard **static‑HTML/JS** che permette di bilanciare le campagne tra **Revenue** e **New Customer Acquisition** tramite uno slider interattivo.

## Come usarla

1. Apri l’URL pubblicato (es. `https://gabriele81benedetti.github.io/mondoffice-simulatore/mondoffice_simulator.html`).
2. Muovi lo slider per impostare la percentuale di revenue da proteggere.
3. Vedi in tempo reale:
   - Investimento per bucket (Revenue / New)
   - ROAS, CPA, Costi, Numero di campagne
   - **Score** (ROAS × (1‑%NewB2B)) con spiegazione integrata

## Aggiornare i dati

```bash
# 1. Aggiorna il CSV con le nuove conversioni
# 2. Rigenera il file JS
python3 convert_csv_to_js.py   # genera nuovamente mondoffice_data.js

# 3. Commit & push
git add mondoffice_data.js
git commit -m "Aggiornati dati di gennaio‑novembre 2025"
git push
```