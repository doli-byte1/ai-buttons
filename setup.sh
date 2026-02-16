#!/bin/sh
# Inicjalizacja środowiska Python dla AI Share Buttons Generator
# Uruchom w katalogu projektu: sh setup.sh

set -e
cd "$(dirname "$0")"

echo "AI Share Buttons – inicjalizacja venv..."

if [ ! -d .venv ]; then
    python3 -m venv .venv
else
    echo "Katalog .venv istnieje."
fi

.venv/bin/pip install -r requirements.txt -q

echo ""
echo "Gotowe."
echo ""
echo "Aby aktywować środowisko i uruchomić aplikację:"
echo "  source .venv/bin/activate"
echo "  streamlit run streamlit_app.py"
echo ""
echo "Albo CLI:"
echo "  source .venv/bin/activate"
echo "  python ai_buttons_gen.py generate -u https://example.com -o snippet.html"
echo ""
