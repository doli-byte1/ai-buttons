"""Render HTML snippet with AI provider buttons."""

import hashlib
import html as html_mod
from dataclasses import dataclass, field
from urllib.parse import quote

from .extract import PageData
from .providers import PROVIDERS
from .config import Config


@dataclass
class RenderResult:
    """Result of render with provider status."""
    html: str
    providers_included: list = field(default_factory=list)
    providers_skipped: list = field(default_factory=list)


def _build_css(theme: str, btn_style: str, uid: str) -> str:
    br = {"pill": "999px", "rounded": "8px", "square": "2px"}.get(btn_style, "999px")
    base = (
        f".ais-{uid}{{border:1px solid #e2e5e9;border-radius:14px;padding:16px 18px;"
        f"margin:20px 0;font-family:system-ui,-apple-system,'Segoe UI',Roboto,sans-serif;"
        f"line-height:1.4;box-sizing:border-box}}"
        f".ais-{uid} .ais-h{{display:block;margin-bottom:12px;font-size:15px;font-weight:600}}"
        f".ais-{uid} .ais-g{{display:flex;flex-wrap:wrap;gap:8px;align-items:center}}"
        f".ais-{uid} .ais-b{{"
        f"display:inline-flex;align-items:center;gap:5px;border:none;border-radius:{br};"
        f"padding:8px 14px;font-size:13px;font-weight:500;line-height:1;"
        f"cursor:pointer;text-decoration:none;transition:opacity .15s,transform .1s}}"
        f".ais-{uid} .ais-b:hover{{opacity:.85;transform:translateY(-1px)}}"
        f".ais-{uid} .ais-b:active{{transform:translateY(0)}}"
        f".ais-{uid} .ais-i{{font-size:15px}}"
        f"@media(max-width:480px){{"
        f".ais-{uid} .ais-g{{gap:6px}}"
        f".ais-{uid} .ais-b{{padding:7px 10px;font-size:12px}}}}"
    )
    themes = {
        "brand": (
            f".ais-{uid}{{background:#fff}}"
            f".ais-{uid} .ais-h{{color:#374151}}"
        ),
        "minimal": (
            f".ais-{uid}{{background:transparent;border:1px dashed #d1d5db}}"
            f".ais-{uid} .ais-h{{color:#6b7280}}"
            f".ais-{uid} .ais-b{{"
            f"border:1px solid #d1d5db!important;background:#fff!important;color:#374151!important}}"
        ),
        "dark": (
            f".ais-{uid}{{background:#1f2937;border-color:#374151}}"
            f".ais-{uid} .ais-h{{color:#e5e7eb}}"
        ),
        "light": (
            f".ais-{uid}{{background:#f9fafb;border-color:#e5e7eb}}"
            f".ais-{uid} .ais-h{{color:#111827}}"
        ),
    }
    return f"<style>{base}{themes.get(theme, '')}</style>"


def _build_copy_js(uid: str) -> str:
    return (
        "<script>(function(){"
        f"document.querySelectorAll('.ais-{uid} .ais-cp').forEach(function(b){{"
        "b.addEventListener('click',function(){"
        "var p=this.getAttribute('data-p'),self=this;"
        "function done(){self.textContent='\\u2713 Skopiowano';"
        "setTimeout(function(){self.textContent='Kopiuj prompt'},1500)}"
        "if(navigator.clipboard){navigator.clipboard.writeText(p).then(done)}"
        "else{var t=document.createElement('textarea');t.value=p;"
        "t.style.cssText='position:fixed;left:-9999px';"
        "document.body.appendChild(t);t.select();document.execCommand('copy');"
        "document.body.removeChild(t);done()}"
        "})})})();</script>"
    )


def _build_copy_textarea(prompt_text: str) -> str:
    """Copy as textarea (no inline JS, CSP-safe)."""
    esc = html_mod.escape(prompt_text)
    return (
        '<textarea readonly class="ais-ta" rows="4" style="width:100%;margin-top:8px;'
        'padding:8px;font-size:12px;border:1px solid #e2e5e9;border-radius:6px;resize:vertical">'
        f"{esc}</textarea>"
        '<p style="margin:4px 0 0;font-size:12px;color:#6b7280">Skopiuj powyższy tekst i wklej do AI.</p>'
    )


def render(
    prompt_text: str,
    data: PageData,
    cfg: Config,
    output_mode: str | None = None,
    no_inline_js: bool = False,
) -> RenderResult:
    """Build HTML snippet. output_mode: links | copy | hybrid."""
    mode = output_mode or cfg.output_mode or "hybrid"
    uid = hashlib.md5(data.canonical.encode()).hexdigest()[:8]
    encoded = quote(prompt_text, safe="")
    heading_text = cfg.heading_pl if cfg.lang == "pl" else cfg.heading_en

    show_links = mode in ("links", "hybrid")
    show_copy = mode in ("copy", "hybrid")

    sorted_keys = sorted(
        [p for p in cfg.providers if p in PROVIDERS],
        key=lambda p: PROVIDERS[p]["order"],
    )

    buttons = []
    included = []
    skipped = []

    for key in sorted_keys:
        prov = PROVIDERS[key]
        href = prov["url"].format(q=encoded)
        if show_links:
            icon = f'<span class="ais-i">{prov["icon"]}</span>' if cfg.icons else ""
            label = html_mod.escape(prov["label"])
            style = "" if cfg.theme == "minimal" else f' style="background:{prov["color"]};color:#fff"'
            if cfg.link_type == "button":
                safe_href = html_mod.escape(href).replace("'", "\\'")
                buttons.append(
                    f'<button class="ais-b" type="button"{style}'
                    f" onclick=\"window.open('{safe_href}','_blank','noopener')\">"
                    f"{icon}{label}</button>"
                )
            else:
                buttons.append(
                    f'<a class="ais-b" href="{html_mod.escape(href)}"'
                    f' target="_blank" rel="nofollow noopener noreferrer"{style}>'
                    f"{icon}{label}</a>"
                )
            included.append(key)

    copy_part = ""
    if show_copy:
        if no_inline_js:
            copy_part = _build_copy_textarea(prompt_text)
        else:
            esc_prompt = html_mod.escape(prompt_text, quote=True)
            copy_style = "" if cfg.theme == "minimal" else ' style="background:#6b7280;color:#fff"'
            copy_part = (
                f'<button class="ais-b ais-cp" type="button"{copy_style}'
                f' data-p="{esc_prompt}">Kopiuj prompt</button>'
            )
        included.append("copy")

    tag = cfg.heading_tag
    extra_cls = f" {cfg.css_class}" if cfg.css_class else ""
    hide_prompt = getattr(cfg, "hide_raw_prompt", True)

    css = _build_css(cfg.theme, cfg.btn_style, uid)
    js = _build_copy_js(uid) if show_copy and not no_inline_js else ""

    raw_prompt_block = ""
    if not hide_prompt:
        esc = html_mod.escape(prompt_text)
        raw_prompt_block = (
            f'<details class="ais-prompt" style="margin-top:12px;font-size:12px;color:#6b7280">'
            f"<summary>Zobacz prompt</summary>"
            f'<pre style="white-space:pre-wrap;word-break:break-word;margin:8px 0 0;padding:8px;'
            f'background:#f3f4f6;border-radius:6px;max-height:200px;overflow:auto">{esc}</pre>'
            f"</details>"
        )

    html_parts = [
        css,
        f'<div class="ais-{uid}{extra_cls}">',
        f"  <{tag} class=\"ais-h\">{html_mod.escape(heading_text)}</{tag}>",
        f'  <div class="ais-g">',
        f"    {''.join(buttons)}",
        f"    {copy_part}",
        f"  </div>",
        raw_prompt_block,
        f"</div>",
        js,
    ]

    return RenderResult(
        html="\n".join(html_parts),
        providers_included=included,
        providers_skipped=skipped,
    )
