#!/usr/bin/env python3
"""
Minimalny backend do zbierania leadów z formularza i zapisu do Airtable.
Uruchom: uvicorn lead_api:app --host 0.0.0.0 --port 8000

Sekrety: .env (AIRTABLE_API_KEY, AIRTABLE_BASE_ID, AIRTABLE_TABLE_NAME)
lub zmienne środowiskowe.
"""

import os
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parent / ".env")
except ImportError:
    pass
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Dodaj ścieżkę projektu
import sys
_path = Path(__file__).resolve().parent
if str(_path) not in sys.path:
    sys.path.insert(0, str(_path))

from ai_buttons.airtable_lead import add_lead


class LeadSubmit(BaseModel):
    email: str
    name: str | None = None
    source_url: str | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(
    title="Lead API (Airtable)",
    description="Endpoint do zapisu leadów z formularza do Airtable.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["POST", "OPTIONS"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"service": "lead-api", "airtable": "configured"}


@app.post("/submit")
def submit_lead(body: LeadSubmit):
    api_key = os.environ.get("AIRTABLE_API_KEY", "").strip()
    base_id = os.environ.get("AIRTABLE_BASE_ID", "").strip()
    table_name = os.environ.get("AIRTABLE_TABLE_NAME", "Leads").strip()
    if not api_key or not base_id:
        raise HTTPException(status_code=503, detail="Airtable nie jest skonfigurowane")
    ok, err = add_lead(
        email=body.email,
        api_key=api_key,
        base_id=base_id,
        table_name=table_name or "Leads",
        name=body.name,
        source_url=body.source_url,
    )
    if not ok:
        raise HTTPException(status_code=400, detail=err)
    return {"ok": True}
