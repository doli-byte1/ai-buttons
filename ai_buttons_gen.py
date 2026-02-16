#!/usr/bin/env python3
"""
AI Share Buttons Generator v3.0
==============================
Universal HTML snippets with AI share buttons for any webpage.
Paste output into WordPress (Custom HTML), any CMS, or static site.

Usage:
  python ai_buttons_gen.py generate -u https://example.com -o snippet.html
  python ai_buttons_gen.py https://example.com
  python ai_buttons_gen.py batch -i urls.txt -o dist/
  python ai_buttons_gen.py --help

Install:  pip install requests beautifulsoup4 lxml pyyaml
"""

import sys
from pathlib import Path

# Dodaj katalog skryptu do path (działa z dowolnego katalogu roboczego)
_script_dir = Path(__file__).resolve().parent
if str(_script_dir) not in sys.path:
    sys.path.insert(0, str(_script_dir))

from ai_buttons.cli import main

if __name__ == "__main__":
    sys.exit(main())
