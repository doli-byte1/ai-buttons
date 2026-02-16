"""URL validation and SSRF protection."""

from urllib.parse import urlparse

BLOCKED_HOSTS = {"localhost", "::1", "0.0.0.0", "[::1]"}


def validate_url(url: str) -> tuple[bool, str]:
    """Validate URL: public HTTP(S) only, no SSRF."""
    url = url.strip()
    p = urlparse(url)
    if p.scheme not in ("http", "https"):
        return False, "Only http/https"
    if not p.netloc:
        return False, "No host"
    h = (p.hostname or "").lower()
    if h in BLOCKED_HOSTS:
        return False, f"Blocked: {h}"
    if h.startswith("127."):
        return False, f"Blocked loopback: {h}"
    for pfx in ("10.", "192.168.", "169.254."):
        if h.startswith(pfx):
            return False, f"Private IP: {h}"
    for i in range(16, 32):
        if h.startswith(f"172.{i}."):
            return False, f"Private IP: {h}"
    if h.endswith((".local", ".internal")):
        return False, f"Local domain: {h}"
    return True, ""
