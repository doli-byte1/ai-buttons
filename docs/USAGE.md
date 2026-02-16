# Pełna dokumentacja CLI

## Uruchamianie bez n8n

### Tryb interaktywny (wizard)

Pytania zamiast opcji – odpowiedni dla użytkowników bez znajomości CLI:

```bash
python ai_buttons_gen.py interactive
# lub
python ai_buttons_gen.py wizard
```

Program zapyta o: URL, katalog wyjścia, język, tryb promptu, format promptu (compact/readable), blok „Zobacz prompt”, tryb wyjścia. Enter = wartość domyślna.

### Pojedyncza strona

```bash
# Podstawowe
python ai_buttons_gen.py generate -u https://example.com -o snippet.html

# Skrócona składnia (backward compat)
python ai_buttons_gen.py https://example.com -o snippet.html

# Z własnym configiem
python ai_buttons_gen.py generate -u https://example.com -c config.yaml -o dist/out.html

# Tryb copy-only (bez linków)
python ai_buttons_gen.py generate -u https://example.com --mode copy

# Bez fragmentu treści (krótszy prompt, linki się mieszczą)
python ai_buttons_gen.py generate -u https://example.com --no-excerpt
```

### Batch (wiele URL-i)

```bash
# urls.txt – jeden URL na linię, # komentarze
python ai_buttons_gen.py batch -i urls.txt -o dist/

# Z raportem
python ai_buttons_gen.py batch -i urls.txt -o dist/ --report dist/report.json
```

### JSON na stdout (dla n8n, pipe)

```bash
python ai_buttons_gen.py generate -u https://example.com --stdout
```

Format:

```json
{
  "ok": true,
  "url": "https://example.com",
  "uid": "12345678",
  "meta": { "title": "...", "canonical": "...", "keywords": "..." },
  "prompt": "...",
  "snippet_html": "...",
  "providers_included": ["chatgpt", "perplexity", "copy"],
  "providers_skipped": [{"name": "gemini", "reason": "url_too_long"}]
}
```

### Uruchamianie z n8n

1. Node: **Execute Command**
2. Komenda: `python /path/ai_buttons_gen.py generate -u "{{$json.url}}" -c /path/config.yaml --stdout`
3. Node **Set** / **Function**: wyciągnij `snippet_html` z wyniku
4. Node do zapisu w CMS / pliku

## Komendy modułowe (debug)

```bash
# Tylko pobranie HTML
python ai_buttons_gen.py fetch -u https://example.com -o page.html

# Tylko ekstrakcja metadanych
python ai_buttons_gen.py extract -u https://example.com -i page.html -o meta.json

# Tylko prompt (z meta.json)
python ai_buttons_gen.py prompt build -m meta.json -o prompt.txt

# Tylko render (z prompt.txt i meta.json)
python ai_buttons_gen.py render -p prompt.txt -m meta.json -o snippet.html
```

## Setup i diagnostyka

```bash
# Szablon configu
python ai_buttons_gen.py init-config -o config.yaml

# Lista providerów
python ai_buttons_gen.py providers

# Walidacja URL
python ai_buttons_gen.py validate-url -u https://example.com
```

## Flagi

| Flaga          | Opis                                    |
|----------------|-----------------------------------------|
| `-c, --config` | Plik konfiguracji (YAML/JSON)           |
| `--lang`       | pl / en                                 |
| `--theme`      | brand / minimal / dark / light          |
| `--providers`  | np. chatgpt,claude,perplexity           |
| `--prompt-mode`| default / injection                     |
| `--mode`       | links / copy / hybrid                   |
| `--heading`    | Własny nagłówek                         |
| `--no-copy`    | Ukryj przycisk Kopiuj prompt            |
| `--no-icons`   | Ukryj ikony providerów                  |
| `--no-excerpt` | Bez fragmentu treści w prompcie         |
| `--no-inline-js` | Textarea zamiast JS (CSP)             |
| `--stdout`     | JSON na stdout (generate)               |

## Kody wyjścia

- `0` – sukces
- `1` – błąd (URL, fetch, ekstrakcja, itd.)
