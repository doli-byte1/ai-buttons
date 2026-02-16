#!/usr/bin/env python3
"""
AI Share Buttons Generator – aplikacja Streamlit.
Bezpieczne generowanie snippetów HTML z przyciskami udostępniania do AI.
"""

import sys
from pathlib import Path

_script_dir = Path(__file__).resolve().parent
if str(_script_dir) not in sys.path:
    sys.path.insert(0, str(_script_dir))

try:
    from dotenv import load_dotenv
    load_dotenv(_script_dir / ".env")
except ImportError:
    pass

import streamlit as st
import streamlit.components.v1 as components
from ai_buttons.config import create_sample_config
from ai_buttons.pipeline import process
from ai_buttons.providers import PROVIDERS
from ai_buttons.security import validate_url

# ---- Styl: wcielam się w grafika ----
st.markdown("""
<style>
    /* Mniej przestrzeni na górze */
    div.block-container { padding-top: 1rem !important; padding-bottom: 1rem !important; }
    
    /* Kolory i zmienne */
    :root { --accent: #6366f1; --accent-dim: #818cf8; --card-bg: #f8fafc; --radius: 12px; }
    
    /* Hero: nagłówek z charakterem – kompaktowy */
    h1 {
        font-weight: 700 !important;
        letter-spacing: -0.02em !important;
        margin-top: 0 !important;
        margin-bottom: 0.15rem !important;
        padding-bottom: 0 !important;
        background: linear-gradient(135deg, #1e293b 0%, #475569 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    [data-testid="stCaptionContainer"] { margin-top: 0 !important; padding-top: 0 !important; }
    
    /* Sekcje w kartach */
    div[data-testid="stVerticalBlock"] > div:has(> div[data-testid="stMarkdown"] h2) {
        background: var(--card-bg);
        padding: 1.25rem 1.5rem;
        border-radius: var(--radius);
        border: 1px solid #e2e8f0;
        margin: 0.5rem 0;
    }
    
    /* Pole URL – większe, przyjazne */
    div[data-testid="stTextInput"] { margin-bottom: 0.5rem; }
    
    /* Przycisk główny – wyraźny */
    div[data-testid="stButton"] > button[kind="primary"] {
        background: linear-gradient(135deg, var(--accent) 0%, #4f46e5 100%) !important;
        font-weight: 600 !important;
        padding: 0.6rem 1.5rem !important;
        border-radius: 10px !important;
        border: none !important;
        box-shadow: 0 2px 8px rgba(99, 102, 241, 0.35);
    }
    div[data-testid="stButton"] > button[kind="primary"]:hover {
        box-shadow: 0 4px 14px rgba(99, 102, 241, 0.45);
    }
    
    /* Sidebar – czytelne sekcje, mniej paddingu */
    section[data-testid="stSidebar"] { padding-top: 1rem !important; }
    section[data-testid="stSidebar"] .stMarkdown { font-size: 0.95rem; }
    section[data-testid="stSidebar"] hr { margin: 0.75rem 0; border-color: #e2e8f0; }
    
    /* Metryki po wyniku – kompaktowe */
    [data-testid="stMetricValue"] { font-size: 1rem !important; }
</style>
""", unsafe_allow_html=True)

st.set_page_config(
    page_title="AI Share Buttons Generator",
    page_icon="🔗",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---- Nagłówek w sidebarze (mniej miejsca na górze) ----
with st.sidebar:
    st.markdown("### 🔗 AI Share Buttons Generator")
    st.caption("Przyciski AI do ChatGPT, Claude, Perplexity… Wklej do WordPressa.")
    st.divider()
    st.header("⚙️ Ustawienia")

    st.subheader("Które LLM mają być na snippecie")
    provider_order = sorted(PROVIDERS, key=lambda x: PROVIDERS[x]["order"])
    provider_labels = {k: PROVIDERS[k]["label"] for k in provider_order}
    selected_providers = st.multiselect(
        "Wybierz chatboty (kolejność = kolejność na snippecie)",
        options=provider_order,
        default=provider_order,
        format_func=lambda k: provider_labels[k],
    )
    if not selected_providers:
        st.warning("Zaznacz co najmniej jeden chatbot.")
    st.caption("Domyślnie: wszystkie. Odznacz te, których nie chcesz w HTML.")

    st.divider()
    st.subheader("Wygląd snippetu")

    theme = st.selectbox(
        "Motyw",
        ["brand", "minimal", "dark", "light"],
        index=0,
        format_func=lambda x: {
            "brand": "🎨 Brand – kolorowe przyciski (domyślny)",
            "minimal": "⬜ Minimal – obramowane, bez koloru",
            "dark": "🌙 Dark – ciemne tło",
            "light": "☀️ Light – jasne tło",
        }[x],
    )

    btn_style = st.radio(
        "Kształt przycisków",
        ["pill", "rounded", "square"],
        index=0,
        format_func=lambda x: {"pill": "Pill (zaokrąglone)", "rounded": "Zaokrąglone", "square": "Prostokąt"}[x],
        horizontal=True,
    )

    show_icons = st.checkbox("Ikony przy nazwach chatbotów", value=True)

    st.divider()
    st.subheader("Zachowanie")

    lang = st.radio("Język", ["pl", "en"], index=0, horizontal=True)
    prompt_mode = st.selectbox(
        "Tryb promptu",
        ["injection", "default"],
        index=0,
        help="injection: SEO + zapamiętaj słowa kluczowe; default: neutralna analiza",
    )
    output_mode = st.selectbox(
        "Tryb wyjścia",
        ["hybrid", "links", "copy"],
        index=0,
        help="hybrid: linki + Kopiuj prompt; links: tylko linki; copy: tylko Kopiuj",
    )
    no_excerpt = st.checkbox("Bez fragmentu treści (krótszy prompt)", value=False)
    no_inline_js = st.checkbox("Bez inline JS (textarea zamiast Kopiuj)", value=False)
    show_prompt_block = st.checkbox("Pokaż blok „Zobacz prompt” w HTML", value=False)

    st.divider()
    with st.expander("Lead gate (formularz w snippecie)"):
        lead_gate_enabled = st.checkbox(
            "Formularz lead przed przyciskami AI",
            value=False,
            help="Użytkownik wpisuje email w snippecie, odblokowuje przyciski. Wymaga backendu (lead_api).",
            key="lead_gate",
        )
        lead_submit_url = st.text_input(
            "URL endpointu POST",
            value="",
            placeholder="https://twoja-domena.com/submit",
            key="lead_url",
        )

# ---- Główny formularz ----
url = st.text_input(
    "URL strony do analizy",
    placeholder="example.com lub www.example.com",
    help="Możesz pominąć https:// – zostanie dodane automatycznie.",
)

if not url:
    st.info("Wpisz URL strony i kliknij **Generuj snippet**.")
    st.stop()

url = url.strip()
if "://" not in url:
    url = "https://" + url.lstrip("/")
ok, reason = validate_url(url)
if not ok:
    st.error(f"Nieprawidłowy lub zablokowany URL: {reason}")
    st.stop()

if not selected_providers:
    st.warning("Wybierz w sidebarze co najmniej jeden chatbot (LLM).")
    st.stop()

if st.button("Generuj snippet", type="primary", use_container_width=True):
    cfg = create_sample_config()
    cfg.lang = lang
    cfg.prompt_mode = prompt_mode
    cfg.theme = theme
    cfg.btn_style = btn_style
    cfg.icons = show_icons
    cfg.providers = selected_providers
    cfg.output_mode = output_mode
    cfg.hide_raw_prompt = not show_prompt_block
    cfg.lead_gate_enabled = lead_gate_enabled and bool(lead_submit_url.strip())
    cfg.lead_submit_url = lead_submit_url.strip()

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

    st.session_state["snippet_result"] = {
        "html": html,
        "data": data,
        "prompt_text": prompt_text,
        "render_result": render_result,
        "cfg": cfg,
    }

if "snippet_result" in st.session_state:
    res = st.session_state["snippet_result"]
    html = res["html"]
    data = res["data"]
    prompt_text = res["prompt_text"]
    render_result = res["render_result"]
    cfg = res["cfg"]

    st.success("Snippet wygenerowany.")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Tytuł", data.title[:50] + "…" if len(data.title) > 50 else data.title or "—")
    with col2:
        st.metric("Chatboty", ", ".join(render_result.providers_included))
    with col3:
        st.metric("URL", data.canonical[:40] + "…" if len(data.canonical) > 40 else data.canonical)

    # Opcjonalny newsletter – przed podglądem
    st.markdown("""
    <div style="background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%); border: 1px solid #bae6fd;
    border-radius: 12px; padding: 20px 24px; margin: 16px 0;">
    <p style="margin: 0 0 4px; font-size: 14px; color: #0369a1; font-weight: 600;">📬 Newsletter SEO-GEO</p>
    <p style="margin: 0; font-size: 15px; color: #0c4a6e;">Dodaj swojego maila, wyślemy Ci informacje o najnowszych narzędziach SEO-GEO!</p>
    </div>
    """, unsafe_allow_html=True)
    with st.form("newsletter", clear_on_submit=True):
        nc1, nc2 = st.columns([3, 1])
        with nc1:
            newsletter_email = st.text_input("Email", placeholder="twoj@email.pl", key="newsletter_email", label_visibility="collapsed")
        with nc2:
            sub = st.form_submit_button("Wyślij", use_container_width=True)
        if sub and newsletter_email and "@" in newsletter_email:
            try:
                from ai_buttons.airtable_lead import add_lead
                import os
                api_key = os.environ.get("AIRTABLE_API_KEY", "")
                base_id = os.environ.get("AIRTABLE_BASE_ID", "")
                table = os.environ.get("AIRTABLE_TABLE_NAME", "Leads") or "Leads"
                try:
                    if not api_key:
                        api_key = str(st.secrets["AIRTABLE_API_KEY"])
                    if not base_id:
                        base_id = str(st.secrets["AIRTABLE_BASE_ID"])
                    try:
                        table = str(st.secrets["AIRTABLE_TABLE_NAME"])
                    except KeyError:
                        pass
                except (KeyError, TypeError, AttributeError):
                    pass
                if api_key and base_id:
                    ok, _ = add_lead(newsletter_email, api_key, base_id, table, source_url="https://ai-buttons-seo-geo.streamlit.app/")
                    st.toast("Wysłano! Dziękujemy.", icon="✅")
                else:
                    st.toast("Dziękujemy za zainteresowanie!", icon="✅")
            except Exception:
                st.toast("Dziękujemy za zainteresowanie!", icon="✅")
        elif sub and (not newsletter_email or "@" not in newsletter_email):
            st.toast("Podaj poprawny adres email.", icon="⚠️")

    st.subheader("Podgląd snippetu")
    with st.container():
        components.html(html, height=340, scrolling=True)
    st.caption("Tak snippet będzie wyglądał na stronie. Przyciski otwierają chatbota w nowej karcie.")

    if cfg.lead_gate_enabled and cfg.lead_submit_url:
        st.info(
            "📬 **Lead gate włączony** – snippet zawiera formularz e-mail przed przyciskami AI. "
            "Użytkownik wpisze adres (i opcjonalnie imię), dopiero potem zobaczy chatbota. "
            "Dane trafiają do Airtable przez backend."
        )

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
