"""Configuration loading from YAML or JSON."""

import json
import os
from dataclasses import dataclass, field
from pathlib import Path

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

from .providers import DEFAULT_PROVIDERS, PROVIDERS


def _get_pkg_dir() -> Path:
    return Path(__file__).resolve().parent


@dataclass
class Config:
    """Main configuration for AI Buttons Generator."""

    # Defaults
    lang: str = "pl"
    prompt_mode: str = "injection"  # default | injection (wzor-like: injection)
    prompt_format: str = "compact"  # compact (ściana tekstu jak wzor) | readable (zachowaj \n)
    hide_raw_prompt: bool = True  # True: tylko przyciski, prompt w data-p; False: widoczny blok tekstu
    max_url_len: int = 1900
    max_excerpt: int = 600
    max_desc: int = 300

    # Fetch
    timeout: int = 10
    max_bytes: int = 3_000_000
    user_agent: str = "Mozilla/5.0 (compatible; AIButtonsGen/3.0)"
    allow_redirects: bool = True

    # Extract (as lists for YAML)
    main_selectors: list = field(
        default_factory=lambda: ["main", "[role='main']", "article", ".entry-content", ".post-content", "#content"]
    )
    noise_tags: list = field(
        default_factory=lambda: ["nav", "header", "footer", "aside", "script", "style", "noscript", "form"]
    )
    noise_classes: list = field(
        default_factory=lambda: ["cookie", "banner", "popup", "modal", "sidebar", "widget", "menu"]
    )
    min_paragraph_len: int = 60

    # Prompt template paths (relative to package or cwd)
    template_pl_default: str = ""
    template_pl_injection: str = ""
    template_en_default: str = ""
    template_en_injection: str = ""

    # Providers & render
    providers: list = field(default_factory=lambda: list(DEFAULT_PROVIDERS))
    theme: str = "brand"
    btn_style: str = "pill"
    copy_btn: bool = True
    icons: bool = True
    link_type: str = "a"
    heading_tag: str = "strong"
    heading_pl: str = "Przeanalizuj i cytuj treść przez sztuczną inteligencję:"
    heading_en: str = "Analyze and cite content with AI:"
    css_class: str = ""
    noindex_hide: bool = False

    # Output
    output_dir: str = "dist"
    report_file: str = "report.json"

    # Output mode: links | copy | hybrid
    output_mode: str = "hybrid"

    @classmethod
    def _flatten_nested(cls, d: dict) -> dict:
        """Flatten nested config: {defaults: {lang: pl}, fetch: {timeout: 10}} -> {lang: pl, timeout: 10}"""
        out = {}
        for section, val in d.items():
            if isinstance(val, dict) and section != "providers":
                for k, v in val.items():
                    if k == "default" and section == "providers":
                        out["providers"] = v
                    else:
                        out[k] = v
            else:
                out[section] = val
        return out

    @classmethod
    def load(cls, path: str | Path) -> "Config":
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Config not found: {path}")
        with open(path, "r", encoding="utf-8") as f:
            raw = f.read()
        if path.suffix in (".yaml", ".yml"):
            if not HAS_YAML:
                raise ImportError("PyYAML required for YAML config. pip install pyyaml")
            data = yaml.safe_load(raw)
        else:
            data = json.loads(raw)
        data = data or {}
        flat = cls._flatten_nested(data)
        return cls._from_dict(flat)

    @classmethod
    def _from_dict(cls, d: dict) -> "Config":
        allowed = {f.name for f in cls.__dataclass_fields__.values()}
        # Map YAML output.dir -> output_dir, output.mode -> output_mode
        aliases = {"dir": "output_dir", "mode": "output_mode"}
        kwargs = {}
        for k, v in d.items():
            key = aliases.get(k, k)
            if key in allowed:
                kwargs[key] = v
        return cls(**kwargs)

    def to_dict(self) -> dict:
        from dataclasses import asdict
        return asdict(self)

    def save(self, path: str | Path) -> None:
        path = Path(path)
        data = self.to_dict()
        with open(path, "w", encoding="utf-8") as f:
            if path.suffix in (".yaml", ".yml"):
                if not HAS_YAML:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                else:
                    yaml.dump(data, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
            else:
                json.dump(data, f, indent=2, ensure_ascii=False)

    def get_template_path(self, lang: str, mode: str) -> Path:
        """Resolve template path. mode: default | injection."""
        key = f"template_{lang}_{mode}"
        rel = getattr(self, key, "") or ""
        if not rel:
            pkg = _get_pkg_dir()
            candidates = [
                pkg.parent / "templates" / f"prompt_{lang}_{mode}.txt",
                pkg / "templates" / f"prompt_{lang}_{mode}.txt",
            ]
            for c in candidates:
                if c.exists():
                    return c
            return pkg.parent / "templates" / f"prompt_{lang}_{mode}.txt"
        p = Path(rel)
        if not p.is_absolute():
            p = Path.cwd() / p
        return p


def create_sample_config() -> Config:
    """Create default config with template paths."""
    pkg = Path(__file__).resolve().parent
    templates_dir = pkg.parent / "templates"
    return Config(
        template_pl_default=str(templates_dir / "prompt_pl_default.txt"),
        template_pl_injection=str(templates_dir / "prompt_pl_injection.txt"),
        template_en_default=str(templates_dir / "prompt_en_default.txt"),
        template_en_injection=str(templates_dir / "prompt_en_injection.txt"),
    )
