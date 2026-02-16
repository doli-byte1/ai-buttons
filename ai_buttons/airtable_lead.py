"""Zapis leadów do Airtable przez REST API."""

import os
import re
import requests


def _sanitize_email(email: str) -> str | None:
    if not email or not isinstance(email, str):
        return None
    email = email.strip().lower()
    if len(email) > 254:
        return None
    if not re.match(r"^[^@]+@[^@]+\.[^@]+$", email):
        return None
    return email


def add_lead(
    email: str,
    api_key: str,
    base_id: str,
    table_name: str,
    name: str | None = None,
    source_url: str | None = None,
    extra_fields: dict | None = None,
) -> tuple[bool, str]:
    """
    Dodaje rekord (lead) do tabeli w Airtable.
    Zwraca (True, "") przy sukcesie, (False, "komunikat błędu") przy błędzie.
    """
    email = _sanitize_email(email)
    if not email:
        return False, "Nieprawidłowy adres email"

    if not api_key or not base_id or not table_name:
        return False, "Brak konfiguracji Airtable (API key, base ID lub nazwa tabeli)"

    table_name_encoded = requests.utils.quote(table_name, safe="")
    url = f"https://api.airtable.com/v0/{base_id.strip()}/{table_name_encoded}"

    headers = {
        "Authorization": f"Bearer {api_key.strip()}",
        "Content-Type": "application/json",
    }

    fields = {"Email": email}
    if name and isinstance(name, str) and name.strip():
        fields["Name"] = name.strip()[:200]
    if source_url and isinstance(source_url, str) and source_url.strip():
        fields["Source URL"] = source_url.strip()[:500]
    if extra_fields and isinstance(extra_fields, dict):
        for k, v in extra_fields.items():
            if k and v is not None and k not in ("Email", "Name", "Source URL"):
                fields[str(k)] = str(v)[:500]

    payload = {"fields": fields}

    try:
        r = requests.post(url, json=payload, headers=headers, timeout=10)
    except requests.RequestException as e:
        return False, f"Błąd połączenia: {e}"

    if r.status_code == 200:
        return True, ""
    try:
        err = r.json()
        msg = err.get("error", {}).get("message", r.text) or str(r.status_code)
    except Exception:
        msg = r.text or str(r.status_code)
    return False, f"Airtable ({r.status_code}): {msg}"
