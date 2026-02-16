"""Main pipeline: validate -> fetch -> extract -> prompt -> render."""

import json
import re
import time
from pathlib import Path
from urllib.parse import urlparse

from .config import Config
from .extract import PageData, extract
from .fetch import fetch_html
from .prompt import build_prompt
from .render import render, RenderResult
from .security import validate_url


def process(
    url: str,
    cfg: Config,
    output_mode: str | None = None,
    no_excerpt: bool = False,
    no_inline_js: bool = False,
) -> tuple[str, PageData, str, RenderResult]:
    """Full pipeline. Returns (snippet_html, page_data, prompt_text, render_result)."""
    ok, reason = validate_url(url)
    if not ok:
        raise ValueError(f"URL rejected: {reason}")

    raw = fetch_html(
        url,
        timeout=cfg.timeout,
        max_bytes=cfg.max_bytes,
        user_agent=cfg.user_agent,
        allow_redirects=cfg.allow_redirects,
    )

    extract_kwargs = {
        "max_desc": cfg.max_desc,
        "max_excerpt": 0 if no_excerpt else cfg.max_excerpt,
        "main_selectors": cfg.main_selectors,
        "noise_tags": cfg.noise_tags,
        "noise_classes": cfg.noise_classes,
        "min_paragraph_len": cfg.min_paragraph_len,
        "noindex_hide": cfg.noindex_hide,
    }

    data = extract(url, raw, **extract_kwargs)
    prompt_text = build_prompt(data, cfg)
    render_result = render(
        prompt_text,
        data,
        cfg,
        output_mode=output_mode,
        no_inline_js=no_inline_js,
    )
    return render_result.html, data, prompt_text, render_result


def process_json(
    url: str,
    cfg: Config,
    output_mode: str | None = None,
    no_excerpt: bool = False,
    no_inline_js: bool = False,
) -> dict:
    """Run pipeline and return result as JSON-serializable dict."""
    try:
        html, data, prompt, render_result = process(
            url, cfg,
            output_mode=output_mode,
            no_excerpt=no_excerpt,
            no_inline_js=no_inline_js,
        )
        uid = str(hash(data.canonical) % 10**8)
        return {
            "ok": True,
            "url": url,
            "uid": uid,
            "meta": {
                "title": data.title,
                "canonical": data.canonical,
                "keywords": data.keywords,
                "description": data.desc[:100] + "..." if len(data.desc) > 100 else data.desc,
            },
            "prompt": prompt,
            "snippet_html": html,
            "providers_included": render_result.providers_included,
            "providers_skipped": render_result.providers_skipped,
        }
    except Exception as e:
        return {
            "ok": False,
            "url": url,
            "error": str(e),
            "providers_included": [],
            "providers_skipped": [],
        }


def batch(
    urls: list[str],
    cfg: Config,
    outdir: str | Path,
    report_path: str | Path | None = None,
    output_mode: str | None = None,
    no_excerpt: bool = False,
) -> list[dict]:
    """Process multiple URLs, save HTML files, return report list."""
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    results = []
    report_path = Path(report_path or outdir / cfg.report_file)

    for i, url in enumerate(urls, 1):
        url = url.strip()
        if not url or url.startswith("#"):
            continue
        print(f"[{i}/{len(urls)}] {url} ... ", end="", flush=True)
        try:
            html, data, _, _ = process(url, cfg, output_mode=output_mode, no_excerpt=no_excerpt)
            slug = re.sub(
                r"[^a-z0-9]+", "-",
                urlparse(url).netloc + urlparse(url).path,
            ).strip("-")[:80]
            fpath = outdir / f"{slug}.html"
            fpath.write_text(html, encoding="utf-8")
            print(f"OK -> {fpath}")
            results.append({"url": url, "title": data.title, "file": str(fpath), "status": "ok"})
        except Exception as e:
            print(f"FAIL: {e}")
            results.append({"url": url, "file": "", "status": str(e)})
        if i < len(urls):
            time.sleep(0.5)

    report_path.write_text(
        json.dumps(results, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return results
