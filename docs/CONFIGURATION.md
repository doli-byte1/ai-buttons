# Konfiguracja

## Plik config.yaml

Generowany przez `ai-buttons init-config -o config.yaml`.

### Sekcje

#### defaults

| Parametr     | Opis              | Domyślnie  |
|--------------|-------------------|------------|
| lang         | Język (pl/en)     | pl         |
| prompt_mode  | default / injection | injection |
| prompt_format| compact (ściana tekstu jak wzor) / readable (czytelny) | compact |
| hide_raw_prompt | true: tylko przyciski; false: blok „Zobacz prompt” | true |
| max_url_len  | Maks. długość URL | 1900       |
| max_excerpt  | Maks. znaków excerpt | 600     |
| max_desc     | Maks. znaków opisu | 300      |

#### fetch

| Parametr       | Opis           | Domyślnie |
|----------------|----------------|-----------|
| timeout        | Sekundy        | 10        |
| max_bytes      | Bajty          | 3000000   |
| user_agent     | User-Agent     | AIButtonsGen/3.0 |
| allow_redirects| Śledzenie przekierowań | true |

#### extract

| Parametr        | Opis                                  |
|-----------------|---------------------------------------|
| main_selectors  | CSS selectory głównej treści          |
| noise_tags      | Tagi do pominięcia (nav, footer, …)   |
| noise_classes   | Klasy do pominięcia (cookie, banner, …) |
| min_paragraph_len | Min. długość akapitu (filtr szumu) |

#### prompt

Ścieżki do szablonów:

- `template_pl_default`, `template_pl_injection`
- `template_en_default`, `template_en_injection`

#### providers

- `default`: lista providerów, np. `[chatgpt, perplexity, claude, gemini]`

#### render

| Parametr   | Opis                    |
|------------|-------------------------|
| heading_pl | Nagłówek PL             |
| heading_en | Nagłówek EN             |
| theme      | brand / minimal / dark / light |
| btn_style  | pill / rounded / square |
| copy_btn   | Czy pokazać Kopiuj prompt |
| link_type  | a (link) / button       |
| css_class  | Dodatkowa klasa na kontener |

#### output

| Parametr    | Opis          |
|-------------|---------------|
| dir         | Domyślny katalog wyjścia |
| report_file | Nazwa pliku raportu (batch) |
| mode        | links / copy / hybrid |

## Placeholdery w szablonach

| Placeholder   | Źródło                    |
|---------------|---------------------------|
| {canonical}   | link canonical, fallback URL |
| {title}       | og:title, title, h1       |
| {keywords}    | meta keywords, article:tag, JSON-LD |
| {description} | meta description, og:description |
| {excerpt}     | Główna treść (main/article) |
| {lang}        | atrybut lang na html      |
| {site_name}   | og:site_name              |
| {author}      | meta author, article:author |
