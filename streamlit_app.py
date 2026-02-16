#!/usr/bin/env python3
"""
AI Share Buttons Generator – aplikacja Streamlit.
Bezpieczne generowanie snippetów HTML z przyciskami udostępniania do AI.
"""

import sys
from pathlib import Path

# Dodaj katalog projektu do path
_script_dir = Path(__file__).resolve().parent
if str(_script_dir) not in sys.path:
    sys.path.insert(0, str(_script_dir))

import streamlit as st
import streamlit.components.v1 as components
from ai_buttons.config import create_sample_config
from ai_buttons.pipeline import process
from ai_buttons.security import validate_url

st.set_page_config(
    page_title="AI Share Buttons Generator",
    page_icon="🔗",
    layout="centered",
    initial_sidebar_state="expanded",
)

# Nagłówek
st.title("🔗 AI Share Buttons Generator")
st.caption("Generator snippetów HTML z przyciskami udostępniania do ChatGPT, Claude, Perplexity i innych.")

# Sidebar – konfiguracja
with st.sidebar:
    st.header("Ustawienia")
    lang = st.radio("Język", ["pl", "en"], index=0, horizontal=True)
    prompt_mode = st.selectbox(
        "Tryb promptu",
        ["injection", "default"],
        index=0,
        help="injection: jak wzór WP (SEO, zapamiętaj słowa kluczowe); default: neutralna analiza",
    )
    theme = st.selectbox(
        "Motyw",
        ["brand", "minimal", "dark", "light"],
        index=0,
    )
    output_mode = st.selectbox(
        "Tryb wyjścia",
        ["hybrid", "links", "copy"],
        index=0,
        help="hybrid: linki + Kopiuj prompt; links: tylko linki; copy: tylko Kopiuj prompt",
    )
    no_excerpt = st.checkbox(
        "Bez fragmentu treści (krótszy prompt)",
        value=False,
        help="Przydatne gdy linki są obcinane (~1900 znaków)",
    )
    no_inline_js = st.checkbox(
        "Bez inline JS (textarea zamiast przycisku Kopiuj)",
        value=False,
        help="Bezpieczniejsze przy restrykcyjnej CSP.",
    )
    show_prompt_block = st.checkbox(
        "Pokaż blok „Zobacz prompt” w HTML",
        value=False,
    )

# Główny formularz
url = st.text_input(
    "URL strony do analizy",
    placeholder="https://example.com",
    help="Tylko publiczne adresy HTTP/HTTPS. Adresy lokalne i sieci wewnętrzne są zablokowane.",
)

if not url or "://" not in url:
    st.info("Wpisz URL strony (np. https://example.com) i naciśnij Enter lub kliknij Generuj.")
    st.stop()

url = url.strip()
ok, reason = validate_url(url)
if not ok:
    st.error(f"Nieprawidłowy lub zablokowany URL: {reason}")
    st.stop()

if st.button("Generuj snippet", type="primary", use_container_width=True):
    cfg = create_sample_config()
    cfg.lang = lang
    cfg.prompt_mode = prompt_mode
    cfg.theme = theme
    cfg.output_mode = output_mode
    cfg.hide_raw_prompt = not show_prompt_block

    with st.spinner("Pobieranie strony i generowanie snippetów…"):
        try:
            html, data, prompt_text, render_result = process(
                url,
                cfg,
                output_mode=cfg.output_mode,
                no_excerpt=no_excerpt,
                no_inline_js=no_inline_js,
            )
        except Exception as e:
            st.error(f"Błąd: {e}")
            st.stop()

    st.success("Snippet wygenerowany.")

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Tytuł", data.title[:60] + "…" if len(data.title) > 60 else data.title)
    with col2:
        st.metric("Providers", ", ".join(render_result.providers_included))

    st.caption("URL: " + data.canonical)

    st.subheader("Podgląd snippetu")
    with st.container():
        components.html(html, height=320, scrolling=True)
    st.caption("Tak snippet będzie wyglądał na stronie (przyciski otwierają chatbota w nowej karcie).")

    st.subheader("HTML do wklejenia")
    st.code(html, language="html", line_numbers=False)

    st.download_button(
        label="Pobierz snippet.html",
        data=html,
        file_name="snippet.html",
        mime="text/html",
        use_container_width=True,
    )

    with st.expander("Zobacz wygenerowany prompt (tekst)"):
        st.text(prompt_text)

st.sidebar.divider()
st.sidebar.caption("AI Share Buttons Generator v3 · MIT")
