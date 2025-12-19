#!/bin/bash

# Vai nella cartella corretta
cd /Users/gabriele/Desktop/TEMP/BTA/gabriele/mondoffice-simulatore

echo "=================================================="
echo "🚀 AGGIORNAMENTO DATI MONDOFFICE"
echo "📅 Periodo: dal 26 Settembre a Ieri"
echo "=================================================="
echo ""

# 1. Scarica i dati da Google Ads
echo "🔄 Passo 1/2: Scarico dati da Google Ads..."
# Cerchiamo di usare uv dal path o assumiamo che sia nel path standard
if command -v uv &> /dev/null; then
    uv run python complete_classification.py
else
    # Fallback se uv non è nel path standard, proviamo path comuni
    if [ -f "$HOME/.cargo/bin/uv" ]; then
        "$HOME/.cargo/bin/uv" run python complete_classification.py
    elif [ -f "$HOME/.local/bin/uv" ]; then
        "$HOME/.local/bin/uv" run python complete_classification.py
    else
        echo "⚠️  Comando 'uv' non trovato. Provo con python3 diretto..."
        python3 complete_classification.py
    fi
fi

# Controlla se il primo script ha avuto successo
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Dati scaricati con successo."
    echo ""
    
    # 2. Converti in JS per il simulatore
    echo "🔄 Passo 2/2: Aggiorno il simulatore..."
    python3 convert_csv_to_js.py
    
    echo ""
    echo "🎉 OPERAZIONE COMPLETATA!"
    echo "Ora puoi ricaricare la pagina del simulatore nel browser."
else
    echo ""
    echo "❌ ERRORE: Qualcosa è andato storto durante il download dei dati."
    echo "Controlla i messaggi di errore sopra."
fi

echo ""
read -p "Premi INVIO per chiudere questa finestra..."
