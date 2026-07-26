$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

if (-not (Test-Path ".venv")) {
    py -3.12 -m venv .venv
}

& .\.venv\Scripts\python.exe -m pip install --upgrade pip
& .\.venv\Scripts\python.exe -m pip install -e ".[dev]"
& .\.venv\Scripts\python.exe -m pytest
& .\.venv\Scripts\python.exe -m ruff check src tests
& .\.venv\Scripts\pyinstaller.exe --noconfirm --clean InterestStatementGeneratorPro.spec

Write-Host "Build complete: dist\InterestStatementGeneratorPro" -ForegroundColor Green
