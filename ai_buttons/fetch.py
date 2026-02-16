"""Fetch HTML with size limits and streaming."""

import requests


def fetch_html(
    url: str,
    timeout: int = 10,
    max_bytes: int = 3_000_000,
    user_agent: str = "Mozilla/5.0 (compatible; AIButtonsGen/3.0)",
    allow_redirects: bool = True,
) -> str:
    """Download HTML with safety limits."""
    r = requests.get(
        url,
        headers={
            "User-Agent": user_agent,
            "Accept": "text/html,application/xhtml+xml",
            "Accept-Language": "pl,en;q=0.9",
        },
        timeout=timeout,
        allow_redirects=allow_redirects,
        stream=True,
    )
    r.raise_for_status()
    ct = r.headers.get("Content-Type", "")
    if "html" not in ct and "xhtml" not in ct:
        raise ValueError(f"Not HTML: {ct}")
    parts = []
    sz = 0
    for chunk in r.iter_content(65536):
        if not chunk:
            break
        sz += len(chunk)
        if sz > max_bytes:
            break
        parts.append(chunk)
    return b"".join(parts).decode(r.encoding or "utf-8", errors="replace")
