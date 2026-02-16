"""Extract metadata and content from HTML."""

import json
import re
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

from bs4 import BeautifulSoup


@dataclass
class PageData:
    url: str
    canonical: str = ""
    title: str = ""
    keywords: str = ""
    desc: str = ""
    excerpt: str = ""
    lang: str = ""
    author: str = ""
    site: str = ""


def _clean(s: str | None) -> str:
    """Clean whitespace."""
    return re.sub(r"\s+", " ", (s or "").strip())


def smart_truncate(text: str, maxlen: int, suffix: str = " [...]") -> str:
    """Ucina tekst na ostatniej spacji przed limitem. Dodaje suffix na końcu."""
    if not text or len(text) <= maxlen:
        return text
    cutoff = text[:maxlen].rfind(" ")
    if cutoff <= 0:
        cutoff = maxlen
    return text[:cutoff].strip() + suffix


def _meta(soup: BeautifulSoup, selectors: list, attr: str = "content") -> str:
    """Try CSS selectors in order, return first non-empty match."""
    for sel in selectors:
        tag = soup.select_one(sel)
        if tag and _clean(tag.get(attr, "")):
            return _clean(tag[attr])
    return ""


def _extract_keywords(soup: BeautifulSoup) -> str:
    """Extract keywords from meta, article:tag, or JSON-LD."""
    kw = _meta(soup, ["meta[name='keywords']"])
    if kw:
        return kw
    tags = soup.select("meta[property='article:tag']")
    if tags:
        return ", ".join(_clean(t.get("content", "")) for t in tags if t.get("content"))
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(script.string or "{}")
            if isinstance(data, dict) and "keywords" in data:
                k = data["keywords"]
                return ", ".join(k) if isinstance(k, list) else str(k)
            if isinstance(data, list):
                for item in data:
                    if isinstance(item, dict) and "keywords" in item:
                        k = item["keywords"]
                        return ", ".join(k) if isinstance(k, list) else str(k)
        except (json.JSONDecodeError, TypeError):
            pass
    return ""


def _excerpt(
    soup: BeautifulSoup,
    maxlen: int = 600,
    main_selectors: list | None = None,
    noise_tags: set | None = None,
    noise_classes: set | None = None,
    min_paragraph_len: int = 60,
) -> str:
    """Extract main content excerpt, skipping navigation and noise."""
    main_selectors = main_selectors or [
        "main", "[role='main']", "article",
        ".entry-content", ".post-content", "#content"
    ]
    noise_tags = noise_tags or {
        "nav", "header", "footer", "aside", "script", "style", "noscript", "form"
    }
    noise_classes = noise_classes or {
        "cookie", "banner", "popup", "modal", "sidebar", "widget", "menu"
    }

    body = soup.find("body") or soup
    main = body
    for sel in main_selectors:
        el = body.select_one(sel)
        if el:
            main = el
            break

    result = ""
    for p in main.find_all(["p", "li"]):
        skip = False
        for parent in p.parents:
            if parent.name in noise_tags:
                skip = True
                break
            cls = " ".join(parent.get("class", [])).lower()
            if any(kw in cls for kw in noise_classes):
                skip = True
                break
        if skip:
            continue

        txt = _clean(p.get_text(" "))
        if len(txt) < min_paragraph_len or txt.count("|") > 2:
            continue

        candidate = result + (" " if result else "") + txt
        if len(candidate) > maxlen:
            if not result:
                result = smart_truncate(txt, maxlen)
            break
        result = candidate

    return result


def extract(
    url: str,
    raw_html: str,
    max_desc: int = 300,
    max_excerpt: int = 600,
    main_selectors: list | None = None,
    noise_tags: list | None = None,
    noise_classes: list | None = None,
    min_paragraph_len: int = 60,
    noindex_hide: bool = False,
) -> PageData:
    """Parse HTML into structured PageData."""
    soup = BeautifulSoup(raw_html, "lxml")

    canonical = _meta(soup, ["link[rel='canonical']"], "href") or url

    title = (
        _meta(soup, ["meta[property='og:title']"])
        or _clean(soup.title.string if soup.title and soup.title.string else "")
        or _clean(soup.select_one("h1").get_text(" ") if soup.select_one("h1") else "")
        or urlparse(url).netloc
    )

    desc = smart_truncate(
        _meta(soup, [
            "meta[name='description']",
            "meta[property='og:description']",
            "meta[name='twitter:description']",
        ]) or "",
        max_desc,
    )

    keywords = _extract_keywords(soup)

    excerpt = _excerpt(
        soup,
        maxlen=max_excerpt,
        main_selectors=main_selectors,
        noise_tags=set(noise_tags) if noise_tags else None,
        noise_classes=set(noise_classes) if noise_classes else None,
        min_paragraph_len=min_paragraph_len,
    )

    lang = ""
    html_tag = soup.find("html")
    if html_tag:
        lang = html_tag.get("lang", "")

    author = _meta(soup, ["meta[name='author']", "meta[property='article:author']"])
    site_name = _meta(soup, ["meta[property='og:site_name']"])

    robots = _meta(soup, ["meta[name='robots']"])
    if noindex_hide and "noindex" in robots.lower():
        raise ValueError(f"noindex page: {url}")

    return PageData(
        url=url,
        canonical=canonical,
        title=title,
        keywords=keywords,
        desc=desc,
        excerpt=excerpt,
        lang=lang,
        author=author,
        site=site_name,
    )
