# Jak wrzucić AI Buttons na GitHub

Projekt jest już przygotowany jako oddzielna paczka. Wystarczy utworzyć repozytorium na GitHub i wypchnąć kod.

## Krok 1: Utwórz repozytorium na GitHub

1. Wejdź na [github.com](https://github.com) i zaloguj się.
2. Kliknij **„New repository”** (zielony przycisk).
3. Uzupełnij:
   - **Repository name:** `ai-buttons` (albo dowolna nazwa)
   - **Description:** `AI Share Buttons Generator – universal HTML snippets`
   - **Public**
   - **Nie** zaznaczaj „Add a README” ani innych plików (repo ma być puste).
4. Kliknij **„Create repository”**.

## Krok 2: Inicjalizacja gita i push (lokalnie)

W terminalu w katalogu projektu:

```powershell
cd C:\Users\pdola\Desktop\ai-buttons

# Zainicjuj repo (jeśli jeszcze nie ma)
git init

# Dodaj wszystko
git add .

# Pierwszy commit
git commit -m "Initial commit: AI Share Buttons Generator v3"

# Podłącz zdalne repo (zamień YOUR_USERNAME na swoją nazwę użytkownika GitHub)
git remote add origin https://github.com/YOUR_USERNAME/ai-buttons.git

# Wypchnij na GitHub
git branch -M main
git push -u origin main
```

## Krok 3: Gotowe

Po pushu projekt jest dostępny pod adresem:
`https://github.com/YOUR_USERNAME/ai-buttons`

## Pierwsze uruchomienie po sklonowaniu

```powershell
cd ai-buttons
pip install -e .
python ai_buttons_gen.py init-config -o config.yaml
python ai_buttons_gen.py generate -u https://example.com -o snippets/
```

## Opcjonalnie: Streamlit / Gradio na GitHub

- **Streamlit Cloud:** [share.streamlit.io](https://share.streamlit.io) → New app → wybierz swoje repo `ai-buttons`.
- **Hugging Face Spaces:** [huggingface.co/spaces](https://huggingface.co/spaces) → Create Space → clone z GitHub.
