# Uruchom lead_api + serwer z testowa strona
# Uzycie: .\run_dev.ps1
# Otworz: http://localhost:8080/test_leads.html

$ErrorActionPreference = "Stop"
$root = $PSScriptRoot
cd $root

Write-Host "1. Generowanie test_leads.html..." -ForegroundColor Cyan
python generate_test_leads.py

Write-Host "2. Uruchamianie lead_api (port 8000)..." -ForegroundColor Cyan
Start-Process python -ArgumentList "-m","uvicorn","lead_api:app","--host","127.0.0.1","--port","8000" -WindowStyle Hidden

Start-Sleep -Seconds 2

Write-Host ""
Write-Host "Lead API:  http://127.0.0.1:8000" -ForegroundColor Green
Write-Host "Test strona: http://localhost:8080/test_leads.html" -ForegroundColor Green
Write-Host ""
Write-Host "Otworz w przegladarce i wypelnij formularz. Ctrl+C = stop." -ForegroundColor Yellow
Write-Host ""

python -m http.server 8080
