# Setup Python venv for AI Share Buttons Generator
# Run: .\setup.ps1

$ErrorActionPreference = "Stop"
$projectRoot = $PSScriptRoot

Write-Host 'AI Share Buttons - inicjalizacja venv...' -ForegroundColor Cyan

$venvPath = Join-Path $projectRoot '.venv'
$pip = Join-Path $venvPath 'Scripts\pip.exe'

if (-not (Test-Path $venvPath)) {
    Write-Host 'Tworzenie .venv...'
    python -m venv $venvPath
    if ($LASTEXITCODE -ne 0) {
        Write-Host 'Blad: uruchom python -m venv .venv recznie.' -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host 'Katalog .venv istnieje.' -ForegroundColor Gray
}

Write-Host 'Instalacja z requirements.txt...'
& $pip install -r (Join-Path $projectRoot 'requirements.txt') -q
if ($LASTEXITCODE -ne 0) {
    Write-Host 'Blad instalacji.' -ForegroundColor Red
    exit 1
}

Write-Host ''
Write-Host 'Gotowe.' -ForegroundColor Green
Write-Host ''
Write-Host 'Aktywacja i uruchomienie:'
Write-Host '  .venv\Scripts\Activate.ps1'
Write-Host '  streamlit run streamlit_app.py'
Write-Host ''
Write-Host 'CLI:'
Write-Host '  .venv\Scripts\Activate.ps1'
Write-Host '  python ai_buttons_gen.py generate -u https://example.com -o snippet.html'
Write-Host ''
