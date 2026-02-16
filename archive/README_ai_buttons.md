# AI Share Buttons Generator v2.0

## Instalacja

```bash
pip install requests beautifulsoup4 lxml
```

## Szybki start

```bash
# Pojedyncza strona
python ai_buttons_gen.py https://fizjoterapia2-0.pl/

# Z dark theme
python ai_buttons_gen.py https://fizjoterapia2-0.pl/ --theme dark -o fizjo.html

# Tylko ChatGPT + Claude + Perplexity
python ai_buttons_gen.py https://example.com --providers chatgpt,claude,perplexity

# Angielska wersja
python ai_buttons_gen.py https://example.com --lang en

# Przyciski <button> zamiast <a> (lepsze dla SEO - nie liczone jako linki)
python ai_buttons_gen.py https://example.com --link-type button
```

## Batch mode (wiele stron naraz)

```bash
# Stworz plik urls.txt:
# https://strona1.pl/
# https://strona2.pl/
# # komentarze zaczynajace sie od # sa pomijane

python ai_buttons_gen.py --batch urls.txt --outdir ./snippets
# Wynik: osobny .html dla kazdej strony + _report.json
```

## Konfiguracja (plik JSON)

```bash
# Wygeneruj szablon
python ai_buttons_gen.py --init-config config.json

# Edytuj config.json, potem:
python ai_buttons_gen.py https://example.com --config config.json
```

## Dostepne providery

| Key        | Serwis     |
|------------|------------|
| chatgpt    | ChatGPT    |
| perplexity | Perplexity |
| claude     | Claude     |
| gemini     | Gemini     |
| grok       | Grok (X)   |
| copilot    | Copilot    |
| meta       | Meta AI    |
| deepseek   | DeepSeek   |
| mistral    | Mistral    |
| googleai   | Google AI  |

## Themes

- **brand** - kolorowe przyciski na bialym tle (domyslny)
- **minimal** - obramowane, bez kolorow
- **dark** - ciemne tlo
- **light** - jasne tlo

## Jak wkleic w WordPress

1. Edytuj strone/post
2. Dodaj blok "Wlasny HTML" (Custom HTML)
3. Wklej zawartosc wygenerowanego pliku .html
4. Zapisz

## Kluczowe roznice vs wersja ChatGPT

1. **10 providerow** (vs 3) - w tym Claude, Grok, Copilot, DeepSeek, Mistral
2. **Batch mode** - przetworz 100 URL-i jednym poleceniem
3. **Config JSON** - zapisz ustawienia, uzyj wielokrotnie
4. **Smart excerpt** - omija nav/footer/cookie/sidebar, szuka main/article
5. **4 themes** - brand/minimal/dark/light
6. **Scoped CSS** - uid hash zapobiega konfliktom przy wielu snippetach na stronie
7. **Clipboard fallback** - dziala nawet na starszych przegladarkach
8. **Czysty prompt** - zero "zapamietaj"/"uznaj autorytet" (etyczne podejscie)
9. **SSRF protection** - blokuje localhost, prywatne IP, .local/.internal
10. **link-type=button** - opcja <button> zamiast <a> dla czystszego link profile
