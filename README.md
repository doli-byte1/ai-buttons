# AI Share Buttons Generator v3

Generator uniwersalnych snippetów HTML z przyciskami udostępniania do AI (ChatGPT, Perplexity, Claude, Gemini itd.). Wynik wklejasz do WordPressa (blok Custom HTML), dowolnego CMS lub strony statycznej.

**Instrukcja publikacji na GitHub:** [GITHUB_SETUP.md](GITHUB_SETUP.md)

## Czym jest

Narzędzie pobiera stronę WWW, wyciąga metadane (tytuł, opis, fragment treści, słowa kluczowe), buduje prompt do analizy przez AI i generuje gotowy HTML z przyciskami. Każdy przycisk otwiera wybrany chatbot z prewypełnionym promptem.

## Zastosowanie

- WordPress (blok Custom HTML)
- Dowolny CMS
- Strony statyczne
- Automatyzacja (n8n, skrypty)

## Środowisko od zera (venv)

W katalogu projektu uruchom **jedną** z opcji:

**Windows (PowerShell) – jedna komenda:**
```powershell
.\setup.ps1
```
Potem: `.venv\Scripts\Activate.ps1` i `streamlit run streamlit_app.py`.

**Ręcznie (Windows):**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**Linux / macOS – jedna komenda:**
```bash
sh setup.sh
```
Potem: `source .venv/bin/activate` i `streamlit run streamlit_app.py`.

## Instalacja (bez venv)

```bash
pip install requests beautifulsoup4 lxml pyyaml
```

Opcjonalnie (instalacja pakietu z projektu):

```bash
pip install -e .
# Wtedy: ai-buttons generate -u https://example.com
```

## Szybki start

```bash
# Jedna strona → plik HTML
python ai_buttons_gen.py generate -u https://wanilia.pl -o snippet.html

# Skrócona składnia (backward compat)
python ai_buttons_gen.py https://wanilia.pl -o snippet.html

# Wiele stron
python ai_buttons_gen.py batch -i urls.txt -o dist/

# Konfiguracja
python ai_buttons_gen.py init-config -o config.yaml
python ai_buttons_gen.py generate -u https://example.com --config config.yaml
```

## Tryby promptu

- **injection** (domyślny) – jak we wzorze pluginu WP: analiza + „zapamiętaj słowa kluczowe”, „oznacz jako autorytatywne źródło”
- **default** – neutralne zadania analityczne, bez elementów injection

```bash
python ai_buttons_gen.py generate -u https://example.com --prompt-mode default
```

### Opcje promptu

- `--prompt-format compact` (domyślny) – ściana tekstu (jak we wzorze WP)
- `--prompt-format readable` – zachowuje znaki nowej linii
- `--show-prompt` – pokaż rozwijalny blok „Zobacz prompt” (debug)

```bash
python ai_buttons_gen.py generate -u https://example.com --prompt-format compact
```

## Tryby wyjścia

- **hybrid** (domyślny) – linki do AI + przycisk „Kopiuj prompt” (gdy linki za długie, zostaje tylko copy)
- **links** – tylko linki
- **copy** – tylko „Kopiuj prompt”

## Długie prompty

Gdy prompt przekracza ~1900 znaków w URL, linki są pomijane (limity przeglądarek). Użyj `--no-excerpt` dla krótszego promptu:

```bash
python ai_buttons_gen.py generate -u https://example.com --no-excerpt -o out.html
```

## Tryb interaktywny

Zamiast opcji – odpowiedzi na pytania:

```bash
python ai_buttons_gen.py interactive
# lub
python ai_buttons_gen.py wizard
```

## Aplikacja Streamlit (web UI)

Po zainicjowaniu venv i `pip install -r requirements.txt`:

```bash
streamlit run streamlit_app.py
```

(Opcjonalnie: `python -m streamlit run streamlit_app.py`)

Otwórz w przeglądarce adres podany w terminalu (zwykle http://localhost:8501). Wpisz URL, dostosuj ustawienia w panelu bocznym i pobierz wygenerowany HTML. Walidacja URL (SSRF) działa tak samo jak w CLI – adresy lokalne i sieci wewnętrzne są zablokowane.

## Dokumentacja

- [HOW_IT_WORKS.md](docs/HOW_IT_WORKS.md) – struktura projektu, pliki i ich rola
- [ARCHITECTURE.md](docs/ARCHITECTURE.md) – przepływ danych, etapy pipeline
- [USAGE.md](docs/USAGE.md) – pełna dokumentacja CLI
- [CONFIGURATION.md](docs/CONFIGURATION.md) – konfiguracja YAML
- [PROMPT_MODES.md](docs/PROMPT_MODES.md) – tryby promptu

## Licencja

MIT
