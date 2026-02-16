# Wdrożenie na Streamlit Cloud

Instrukcja publikacji na https://ai-buttons-seo-geo.streamlit.app/

## 1. Repozytorium

Upewnij się, że kod jest na GitHubie (np. `doli-byte1/ai-buttons`).

## 2. Streamlit Cloud

1. Wejdź na [share.streamlit.io](https://share.streamlit.io)
2. Zaloguj się przez GitHub
3. **New app** → wybierz repozytorium, branch `main`
4. **Main file path:** `streamlit_app.py`
5. **App URL:** (opcjonalnie) `ai-buttons-seo-geo`
6. Kliknij **Deploy**

## 3. Sekrety (hasła do Airtable)

Aby formularz newslettera zapisywał e‑maile do Airtable:

1. W Streamlit Cloud otwórz aplikację → **Settings** (⚙️) → **Secrets**
2. Wklej (uzupełnij własnymi danymi):

```toml
AIRTABLE_API_KEY = "patxxxxxxxxxxxxxxxx"
AIRTABLE_BASE_ID = "appxxxxxxxx"
AIRTABLE_TABLE_NAME = "Leads"
```

### Skąd wziąć wartości?

| Sekret | Gdzie |
|--------|-------|
| `AIRTABLE_API_KEY` | [airtable.com/create/tokens](https://airtable.com/create/tokens) – utwórz token z `data.records:write` |
| `AIRTABLE_BASE_ID` | URL bazy w Airtable: `airtable.com/appXXXXX/...` → `appXXXXX` |
| `AIRTABLE_TABLE_NAME` | Nazwa tabeli (np. `Leads`) – musi mieć kolumny: Email, Name, Source URL |

### Bez sekretów

Aplikacja działa normalnie. Formularz newslettera się pokazuje, ale adresy nie będą zapisywane – użytkownik i tak zobaczy „Wysłano!”.

## 4. Po zapisaniu sekretów

Kliknij **Save** – aplikacja zrestartuje się z nowymi zmiennymi.

## 5. Pliki potrzebne do wdrożenia

W repo muszą być:
- `streamlit_app.py` – główna aplikacja
- `requirements.txt` – zależności
- `ai_buttons/` – moduł
- `templates/` – szablony promptów
- `.streamlit/config.toml` – konfiguracja (motyw, serwer)
- `config/config.sample.yaml` – (opcjonalnie)

Pliki w `.gitignore` (`.env`, `archive/`, `test_leads.html`, `.streamlit/secrets.toml`) nie trafiają do repo.

---

**Uwaga:** Sekrety wpisujesz tylko w interfejsie Streamlit Cloud (Settings → Secrets), nigdy w kodzie ani w plikach w repo.
