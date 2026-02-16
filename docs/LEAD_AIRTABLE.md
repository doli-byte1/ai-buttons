# Zbieranie leadów przez Airtable

Snippet może pokazywać **formularz (email, imię)** zamiast od razu przycisków AI. Po wysłaniu formularza dane trafiają do **Airtable**, a użytkownik widzi odblokowane przyciski.

## Architektura

1. **Snippet na stronie** – formularz wysyła POST na Twój backend (JSON: `email`, `name`, `source_url`).
2. **Backend** (`lead_api.py`) – przyjmuje request, zapisuje rekord do Airtable (klucz API tylko na serwerze).
3. **Airtable** – tabela np. "Leads" z kolumnami: Email, Name, Source URL.

## Konfiguracja Airtable

1. Zaloguj się do [Airtable](https://airtable.com), utwórz bazę (lub użyj istniejącej).
2. **ID bazy (Base ID):** w URL bazy jest fragment `airtable.com/APPxxxxxx/...` – `APPxxxxxx` to Base ID.
3. **Token API:** [airtable.com/create/tokens](https://airtable.com/create/tokens) – utwórz token z zakresem `data.records:write` (i `schema.bases:read` jeśli potrzebujesz). Skopiuj token.
4. W bazie utwórz tabelę (np. **Leads**) z kolumnami:
   - **Email** (Single line text) – obowiązkowe
   - **Name** (Single line text) – opcjonalne
   - **Source URL** (URL lub Single line) – opcjonalne, skąd przyszedł lead

Nazwy kolumn w API muszą dokładnie odpowiadać: `Email`, `Name`, `Source URL`.

## Streamlit Cloud (ai-buttons-seo-geo.streamlit.app)

W aplikacji Streamlit przed „Podgląd snippetu” jest **opcjonalny formularz**: „Dodaj swojego maila, wyślemy Ci informacje o najnowszych narzędziach SEO-GEO!”. Adresy trafiają do Airtable.

W Streamlit Cloud (Settings → Secrets) dodaj:
```
AIRTABLE_API_KEY = "patxxxx..."
AIRTABLE_BASE_ID = "appxxxx..."
AIRTABLE_TABLE_NAME = "Leads"
```
Bez tych wpisów formularz nadal wyświetla się, ale adresy nie będą zapisywane (użytkownik i tak dostanie „Dziękujemy”).

## Test lokalny (wszystko podlaczone)

```powershell
# 1. Wygeneruj testowa strone z formularzem
python generate_test_leads.py

# 2. Uruchom lead_api + serwer (jedna komenda)
.\run_dev.ps1
```

Otworz w przegladarce: http://localhost:8080/test_leads.html  
Wypelnij formularz – po wyslaniu przyciski AI sie odblokuja, a lead pojawi sie w Airtable (tabela Leads).

## Uruchomienie backendu (produkcja / osobno)

```bash
# Środowisko
export AIRTABLE_API_KEY="patxxxxxxxxxxxx"
export AIRTABLE_BASE_ID="APPxxxxxxxxxx"
export AIRTABLE_TABLE_NAME="Leads"

# Uruchom (z katalogu projektu)
pip install fastapi uvicorn
uvicorn lead_api:app --host 0.0.0.0 --port 8000
```

Endpoint do zapisu: `POST /submit` z ciałem JSON:

```json
{
  "email": "jan@example.com",
  "name": "Jan",
  "source_url": "https://twoja-strona.pl/artykul"
}
```

Na produkcji wystaw backend pod domeną (np. `https://api.twoja-domena.com`) z HTTPS i podaj w generatorze:  
`https://api.twoja-domena.com/submit`.

## Generator (Streamlit / CLI)

- **Streamlit:** w sidebarze włącz "Formularz lead przed przyciskami AI" i wpisz URL endpointu (np. `https://api.twoja-domena.com/submit`). Wygenerowany snippet będzie zawierał formularz; po poprawnym POST przyciski AI się pokażą.
- **CLI / config:** w pliku konfiguracyjnym ustaw:
  - `lead_gate_enabled: true`
  - `lead_submit_url: "https://api.twoja-domena.com/submit"`

Opcjonalnie możesz ustawić własne etykiety formularza (np. `lead_form_heading_pl`, `lead_form_submit_pl`) w configu.

## Bezpieczeństwo i GDPR

- Klucz Airtable **nie** może być w HTML/JS – tylko w zmiennych środowiskowych na serwerze.
- Na stronie z formularzem powinna być informacja o przetwarzaniu danych i link do polityki prywatności; rozważ checkbox zgody przed wysłaniem (wymagałoby małej zmiany w snippecie).
