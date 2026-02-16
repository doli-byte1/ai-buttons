#!/usr/bin/env python3
"""Generuje test_leads.html z wlaczonym lead gate (POST na localhost:8000)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ai_buttons.config import create_sample_config
from ai_buttons.pipeline import process

cfg = create_sample_config()
cfg.lead_gate_enabled = True
cfg.lead_submit_url = "http://127.0.0.1:8000/submit"
cfg.providers = ["chatgpt", "claude", "perplexity"]  # krotki zestaw do testu
html, data, _, _ = process("https://httpbin.org/html", cfg)

out = Path(__file__).parent / "test_leads.html"
full = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>Test Lead Gate</title></head>
<body style="font-family:sans-serif;max-width:600px;margin:40px auto;padding:20px">
<h1>Test zbierania leadow</h1>
<p>Wypelnij formularz - po wyslaniu odblokuja sie przyciski AI. Dane trafia do Airtable.</p>
<hr>
{html}
<hr>
<p style="font-size:12px;color:#666">Backend: http://127.0.0.1:8000 | Sprawdz baze Airtable (tabela Leads)</p>
</body></html>
"""
out.write_text(full, encoding="utf-8")
print(f"Zapisano: {out}")
