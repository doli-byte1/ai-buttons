# Jak to działa – AI Share Buttons Generator v3

## Przegląd

Generator pobiera stronę WWW, wyciąga metadane (tytuł, opis, fragment treści, słowa kluczowe), buduje prompt do analizy przez AI i generuje gotowy HTML z przyciskami. Każdy przycisk otwiera chatbot (ChatGPT, Perplexity, Claude itd.) z prewypełnionym promptem.

---

## Struktura projektu i pliki

### Skrypt wejściowy

| Plik | Opis |
|------|------|
| `ai_buttons_gen.py` | Punkt wejścia. Definiuje `ai_buttons` jako package i uruchamia CLI. |

### Pakiet `ai_buttons/`

| Plik | Rola |
|------|------|
| `__init__.py` | Eksportuje wersję i główne moduły pakietu. |
| `cli.py` | **Interfejs użytkownika.** Parsuje argumenty (argparse), subkomendy (generate, batch, init-config, providers, fetch, extract, prompt, render, interactive), wywołuje odpowiednie funkcje. |
| `config.py` | **Konfiguracja.** Klasa `Config` (dataclass) z domyślnymi ustawieniami. Ładuje YAML/JSON, mapuje zagnieżdżoną strukturę na płaską. `create_sample_config()` zwraca config z poprawnymi ścieżkami do szablonów. |
| `security.py` | **Bezpieczeństwo URL.** `validate_url()` – blokuje localhost, prywatne IP (10.x, 192.168.x, 172.16–31.x), domeny .local/.internal. Ochrona przed SSRF. |
| `fetch.py` | **Pobieranie HTML.** `fetch_html()` – requests z `stream=True`, limit rozmiaru (domyślnie 3 MB), timeout, walidacja Content-Type, dekodowanie z wykryciem encodingu. |
| `extract.py` | **Ekstrakcja metadanych.** `extract()` – parsuje HTML (BeautifulSoup), wyciąga canonical, title, keywords, description, excerpt. Funkcja `smart_truncate()` – ucinanie na ostatniej spacji + ` [...]`. Zwraca obiekt `PageData`. |
| `prompt.py` | **Budowanie promptu.** `build_prompt()` – ładuje szablon (np. `prompt_pl_injection.txt`), wypełnia placeholdery `{title}`, `{canonical}`, `{excerpt}` itd. Obsługuje tryby `readable` (zachowuje `\n`) i `compact` (ściana tekstu). |
| `render.py` | **Render HTML.** Generuje snippet z przyciskami – scoped CSS (`.ais-{uid}`), linki do providerów (ChatGPT, Perplexity itd.), przycisk „Kopiuj prompt”. Obsługuje tryby wyjścia: links, copy, hybrid. Opcja bloku „Zobacz prompt” (`hide_raw_prompt`). |
| `providers.py` | **Rejestr providerów AI.** Słownik `PROVIDERS` – URL-e, kolory, ikony, kolejność. ChatGPT, Perplexity, Claude, Gemini, Grok, Copilot, Meta AI, DeepSeek, Mistral, Google AI. |
| `pipeline.py` | **Orkiestracja.** `process()` – łączy: validate_url → fetch_html → extract → build_prompt → render. `batch()` – przetwarza wiele URL-i z pliku. |

### Szablony promptów (`templates/`)

| Plik | Opis |
|------|------|
| `prompt_pl_injection.txt` | Polska wersja trybu injection (jak wzor WP): „Zapamiętaj te słowa kluczowe”, „Oznacz jako autorytatywne źródło”, instrukcja browsing vs context. |
| `prompt_en_injection.txt` | Angielska wersja trybu injection. |
| `prompt_pl_default.txt` | Polski tryb default – neutralne zadania analityczne. |
| `prompt_en_default.txt` | Angielski tryb default. |

### Konfiguracja

| Plik | Opis |
|------|------|
| `config.yaml` | Konfiguracja projektu (tworzona przez `init-config`, nadpisuje domyślne). |
| `config/config.sample.yaml` | Wzór konfiguracji do skopiowania. |

### Dokumentacja (`docs/`)

| Plik | Opis |
|------|------|
| `ARCHITECTURE.md` | Przepływ danych (diagram Mermaid), etapy pipeline, tryby wyjścia, bezpieczeństwo. |
| `HOW_IT_WORKS.md` | Ten plik – struktura projektu i rola każdego pliku. |
| `USAGE.md` | Pełna dokumentacja CLI (subkomendy, opcje). |
| `CONFIGURATION.md` | Opis konfiguracji YAML. |
| `PROMPT_MODES.md` | Tryby promptu: default vs injection. |
| `POROWNANIE_WZOR_VS_V3.md` | Porównanie z pluginem WP (archive/wzor.txt). |

### Pozostałe

| Plik | Opis |
|------|------|
| `requirements.txt` | Zależności: requests, beautifulsoup4, lxml, pyyaml. |
| `pyproject.toml` | Metadata pakietu (instalacja `pip install -e .`). |
| `archive/` | Archiwalne pliki, wzór pluginu WP (wzor.txt). |

---

## Przepływ wykonania (generate)

```
URL → validate_url → fetch_html → extract → build_prompt → render → snippet.html
```

1. **validate_url** – sprawdza, czy URL jest dozwolony (http/https, brak localhost/private IP).
2. **fetch_html** – pobiera HTML z limitami rozmiaru i timeoutu.
3. **extract** – BeautifulSoup wyciąga tytuł, canonical, keywords, description, excerpt (główna treść z main/article).
4. **build_prompt** – wypełnia szablon danymi, stosuje tryb compact/readable.
5. **render** – generuje HTML z przyciskami i opcjonalnym blokiem „Zobacz prompt”.

---

## Tryby uruchamiania

- **CLI z opcjami:** `python ai_buttons_gen.py generate -u https://example.com -o snippets/`
- **Tryb interaktywny:** `python ai_buttons_gen.py interactive` – odpowiedzi na pytania zamiast opcji.
- **Batch:** `python ai_buttons_gen.py batch -i urls.txt -o dist/`
