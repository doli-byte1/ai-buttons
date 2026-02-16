"""CLI for AI Share Buttons Generator."""

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

from . import __version__
from .config import Config, create_sample_config
from .extract import extract
from .fetch import fetch_html
from .pipeline import batch, process, process_json
from .prompt import build_prompt
from .providers import PROVIDERS
from .render import render
from .security import validate_url


def _load_config(path: str | None) -> Config:
    if path and Path(path).exists():
        return Config.load(path)
    return create_sample_config()


def _output_filename(canonical_url: str) -> str:
    """Generuje nazwę pliku: domena_z_underscores_YYYYMMDD_HHMMSS.html"""
    netloc = urlparse(canonical_url).netloc or "strona"
    domain = re.sub(r"^www\.", "", netloc, flags=re.I)
    slug = domain.replace(".", "_").replace("-", "_")
    slug = re.sub(r"[^a-z0-9_]", "", slug.lower()) or "strona"
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{slug}_{ts}.html"


def cmd_init_config(args: argparse.Namespace) -> int:
    cfg = create_sample_config()
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    cfg.save(out)
    print(f"Config template: {out}")
    print(f"Available providers: {', '.join(PROVIDERS.keys())}")
    return 0


def cmd_providers_list(args: argparse.Namespace) -> int:
    for name, p in sorted(PROVIDERS.items(), key=lambda x: x[1]["order"]):
        print(f"  {name}: {p['label']} - {p['url']}")
    return 0


def cmd_validate_url(args: argparse.Namespace) -> int:
    ok, reason = validate_url(args.url)
    if ok:
        print("OK: URL valid")
        return 0
    print(f"INVALID: {reason}", file=sys.stderr)
    return 1


def cmd_generate(args: argparse.Namespace) -> int:
    cfg = _load_config(args.config)
    if args.lang:
        cfg.lang = args.lang
    if args.theme:
        cfg.theme = args.theme
    if args.providers:
        cfg.providers = [p.strip() for p in args.providers.split(",") if p.strip()]
    if args.prompt_mode:
        cfg.prompt_mode = args.prompt_mode
    if getattr(args, "prompt_format", None):
        cfg.prompt_format = args.prompt_format
    if getattr(args, "hide_prompt", False):
        cfg.hide_raw_prompt = False  # --show-prompt => pokaż blok
    if args.mode:
        cfg.output_mode = args.mode
    if args.heading:
        if cfg.lang == "pl":
            cfg.heading_pl = args.heading
        else:
            cfg.heading_en = args.heading
    if args.no_copy:
        cfg.copy_btn = False
        if cfg.output_mode == "hybrid":
            cfg.output_mode = "links"
    if args.no_icons:
        cfg.icons = False

    try:
        html, data, prompt, render_result = process(
            args.url,
            cfg,
            output_mode=cfg.output_mode,
            no_excerpt=args.no_excerpt,
            no_inline_js=args.no_inline_js,
        )
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    if args.stdout_json:
        result = {
            "ok": True,
            "url": args.url,
            "uid": str(hash(data.canonical) % 10**8),
            "meta": {
                "title": data.title,
                "canonical": data.canonical,
                "keywords": data.keywords,
            },
            "prompt": prompt,
            "snippet_html": html,
            "providers_included": render_result.providers_included,
            "providers_skipped": render_result.providers_skipped,
        }
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    out = Path(args.output)
    use_auto_name = (
        out.suffix != ".html"
        or out.name == "snippet.html"
        or str(args.output).rstrip("/").endswith("/")
    )
    if use_auto_name:
        base = out.parent if out.suffix == ".html" else out
        base = base if base.name else Path("snippets")
        out = Path(base) / _output_filename(data.canonical)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")

    print(f"  Zapisano: {out}")
    print(f"  Tytuł:    {data.title}")
    print(f"  URL:      {data.canonical}")
    print(f"  Providers:{', '.join(render_result.providers_included)}")
    print(f"")
    print(f"  >> Otwórz plik i skopiuj całą zawartość do WordPress (blok Custom HTML) lub innego CMS.")
    return 0


def cmd_batch(args: argparse.Namespace) -> int:
    cfg = _load_config(args.config)
    if args.mode:
        cfg.output_mode = args.mode

    with open(args.input, "r", encoding="utf-8") as f:
        urls = [line.strip() for line in f if line.strip() and not line.startswith("#")]

    if not urls:
        print("No URLs found in file.", file=sys.stderr)
        return 1

    results = batch(
        urls,
        cfg,
        args.outdir,
        report_path=args.report,
        output_mode=cfg.output_mode,
        no_excerpt=args.no_excerpt,
    )
    ok_count = sum(1 for r in results if r.get("status") == "ok")
    print(f"\nDone: {ok_count}/{len(results)} -> {args.outdir}/")
    if args.report:
        print(f"Report: {args.report}")
    return 0


def cmd_fetch(args: argparse.Namespace) -> int:
    ok, reason = validate_url(args.url)
    if not ok:
        print(f"INVALID URL: {reason}", file=sys.stderr)
        return 1
    cfg = _load_config(args.config)
    try:
        html = fetch_html(
            args.url,
            timeout=cfg.timeout,
            max_bytes=cfg.max_bytes,
            user_agent=cfg.user_agent,
        )
        Path(args.output).write_text(html, encoding="utf-8")
        print(f"Saved: {args.output} ({len(html)} chars)")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    return 0


def cmd_extract(args: argparse.Namespace) -> int:
    cfg = _load_config(args.config)
    raw = Path(args.input).read_text(encoding="utf-8")
    data = extract(
        args.url,
        raw,
        max_desc=cfg.max_desc,
        max_excerpt=cfg.max_excerpt,
        main_selectors=cfg.main_selectors,
        noise_tags=cfg.noise_tags,
        noise_classes=cfg.noise_classes,
        min_paragraph_len=cfg.min_paragraph_len,
    )
    from dataclasses import asdict
    Path(args.output).write_text(
        json.dumps(asdict(data), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"Saved: {args.output}")
    return 0


def cmd_prompt_build(args: argparse.Namespace) -> int:
    cfg = _load_config(args.config)
    meta = json.loads(Path(args.meta).read_text(encoding="utf-8"))
    from .extract import PageData
    data = PageData(**{k: v for k, v in meta.items() if k in PageData.__dataclass_fields__})
    prompt = build_prompt(data, cfg)
    Path(args.output).write_text(prompt, encoding="utf-8")
    print(f"Saved: {args.output} ({len(prompt)} chars)")
    return 0


def _input_default(prompt: str, default: str = "") -> str:
    """Pytanie z domyślną wartością. Enter = zostaw default."""
    if default:
        s = input(f"{prompt} [{default}]: ").strip()
        return s if s else default
    return input(f"{prompt}: ").strip()


def cmd_interactive(args: argparse.Namespace) -> int:
    """Tryb interaktywny – pytania zamiast opcji."""
    print("\n=== AI Share Buttons Generator – tryb interaktywny ===\n")

    cfg = _load_config(args.config)

    url = _input_default("URL strony do analizy", "https://example.com")
    if not url or "://" not in url:
        print("Błąd: podaj poprawny URL.", file=sys.stderr)
        return 1

    output = _input_default("Katalog lub ścieżka wyjścia", "snippets")
    lang_choice = _input_default("Język (pl/en)", cfg.lang)
    if lang_choice in ("pl", "en"):
        cfg.lang = lang_choice

    prompt_mode_choice = _input_default("Tryb promptu: default (neutralny) | injection (jak wzor WP)", cfg.prompt_mode)
    if prompt_mode_choice in ("default", "injection"):
        cfg.prompt_mode = prompt_mode_choice

    prompt_format_choice = _input_default("Format promptu: compact (ściana tekstu) | readable (zachowaj \\n)", cfg.prompt_format)
    if prompt_format_choice in ("compact", "readable"):
        cfg.prompt_format = prompt_format_choice

    show_prompt_raw = _input_default("Pokaż blok 'Zobacz prompt' w HTML? (tak/nie)", "nie")
    cfg.hide_raw_prompt = show_prompt_raw.lower() not in ("tak", "t", "yes", "y")

    mode_choice = _input_default("Tryb wyjścia: links | copy | hybrid", cfg.output_mode)
    if mode_choice in ("links", "copy", "hybrid"):
        cfg.output_mode = mode_choice

    print("\n--- Przetwarzanie ---\n")

    # Symuluj args dla cmd_generate
    class FakeArgs:
        pass
    fake = FakeArgs()
    fake.url = url
    fake.output = output
    fake.config = args.config
    fake.lang = cfg.lang
    fake.theme = cfg.theme
    fake.providers = None
    fake.prompt_mode = cfg.prompt_mode
    fake.prompt_format = cfg.prompt_format
    fake.hide_prompt = not cfg.hide_raw_prompt
    fake.mode = cfg.output_mode
    fake.heading = None
    fake.no_copy = False
    fake.no_icons = cfg.icons
    fake.no_excerpt = False
    fake.no_inline_js = False
    fake.stdout_json = False

    return cmd_generate(fake)


def cmd_render(args: argparse.Namespace) -> int:
    cfg = _load_config(args.config)
    prompt = Path(args.prompt).read_text(encoding="utf-8")
    meta = json.loads(Path(args.meta).read_text(encoding="utf-8"))
    from .extract import PageData
    data = PageData(**{k: v for k, v in meta.items() if k in PageData.__dataclass_fields__})
    result = render(prompt, data, cfg, no_inline_js=args.no_inline_js)
    Path(args.output).write_text(result.html, encoding="utf-8")
    print(f"Saved: {args.output}")
    return 0


def main() -> int:
    # Backward compat: URL as first arg -> generate -u URL
    argv = sys.argv[1:]
    if argv and argv[0].startswith("http") and "://" in argv[0]:
        argv = ["generate", "-u", argv[0]] + argv[1:]

    ap = argparse.ArgumentParser(
        prog="ai-buttons",
        description="AI Share Buttons Generator v3 - universal HTML snippets",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    ap.add_argument("--config", "-c", help="Config file (YAML or JSON)")
    sub = ap.add_subparsers(dest="cmd", help="Commands")

    # interactive
    p_int = sub.add_parser("interactive", aliases=["wizard"], help="Tryb interaktywny – pytania zamiast opcji")
    p_int.add_argument("--config", "-c", dest="config", help="Config file (YAML or JSON)")
    p_int.set_defaults(func=cmd_interactive)

    # init-config
    p_init = sub.add_parser("init-config", help="Create sample config")
    p_init.add_argument("-o", "--output", default="config.yaml")
    p_init.set_defaults(func=cmd_init_config)

    # providers list
    p_prov = sub.add_parser("providers", help="List providers")
    p_prov.set_defaults(func=cmd_providers_list)

    # validate-url
    p_val = sub.add_parser("validate-url", help="Validate URL")
    p_val.add_argument("-u", "--url", required=True)
    p_val.set_defaults(func=cmd_validate_url)

    # generate
    p_gen = sub.add_parser("generate", help="Full pipeline: fetch -> extract -> prompt -> render")
    p_gen.add_argument("--config", "-c", dest="config", help="Config file (YAML or JSON)")
    p_gen.add_argument("-u", "--url", required=True)
    p_gen.add_argument("-o", "--output", default="snippets", help="Katalog (domyślnie snippets/) lub ścieżka do pliku .html")
    p_gen.add_argument("--lang", choices=["pl", "en"])
    p_gen.add_argument("--theme", choices=["brand", "minimal", "dark", "light"])
    p_gen.add_argument("--providers", help="Comma-separated: chatgpt,claude,...")
    p_gen.add_argument("--prompt-mode", choices=["default", "injection"])
    p_gen.add_argument("--prompt-format", choices=["readable", "compact"], help="readable=zachowaj \\n, compact=ściana tekstu")
    p_gen.add_argument("--show-prompt", action="store_true", dest="hide_prompt", help="Pokaż blok 'Zobacz prompt' (domyślnie ukryty)")
    p_gen.add_argument("--mode", choices=["links", "copy", "hybrid"], help="Output mode")
    p_gen.add_argument("--heading", help="Custom heading text")
    p_gen.add_argument("--no-copy", action="store_true")
    p_gen.add_argument("--no-icons", action="store_true")
    p_gen.add_argument("--no-excerpt", action="store_true")
    p_gen.add_argument("--no-inline-js", action="store_true")
    p_gen.add_argument("--stdout", dest="stdout_json", action="store_true", help="Output JSON to stdout")
    p_gen.set_defaults(func=cmd_generate)

    # batch
    p_batch = sub.add_parser("batch", help="Process multiple URLs")
    p_batch.add_argument("-i", "--input", required=True, help="File with URLs")
    p_batch.add_argument("-o", "--outdir", default="dist")
    p_batch.add_argument("--report", help="Report JSON path")
    p_batch.add_argument("--mode", choices=["links", "copy", "hybrid"])
    p_batch.add_argument("--no-excerpt", action="store_true")
    p_batch.set_defaults(func=cmd_batch)

    # fetch
    p_fetch = sub.add_parser("fetch", help="Fetch HTML only")
    p_fetch.add_argument("-u", "--url", required=True)
    p_fetch.add_argument("-o", "--output", default="page.html")
    p_fetch.set_defaults(func=cmd_fetch)

    # extract
    p_ext = sub.add_parser("extract", help="Extract metadata from HTML")
    p_ext.add_argument("-u", "--url", required=True)
    p_ext.add_argument("-i", "--input", required=True, help="HTML file")
    p_ext.add_argument("-o", "--output", default="meta.json")
    p_ext.set_defaults(func=cmd_extract)

    # prompt build
    p_pr = sub.add_parser("prompt", help="Build prompt from meta")
    p_pr_s = p_pr.add_subparsers(dest="prompt_cmd")
    p_pr_build = p_pr_s.add_parser("build")
    p_pr_build.add_argument("-m", "--meta", required=True)
    p_pr_build.add_argument("-o", "--output", default="prompt.txt")
    p_pr_build.set_defaults(func=cmd_prompt_build)

    # render
    p_rend = sub.add_parser("render", help="Render HTML from prompt and meta")
    p_rend.add_argument("-p", "--prompt", required=True)
    p_rend.add_argument("-m", "--meta", required=True)
    p_rend.add_argument("-o", "--output", default="snippet.html")
    p_rend.add_argument("--no-inline-js", action="store_true")
    p_rend.set_defaults(func=cmd_render)

    args = ap.parse_args(argv)

    if args.cmd is None:
        ap.print_help()
        return 0

    return args.func(args)
