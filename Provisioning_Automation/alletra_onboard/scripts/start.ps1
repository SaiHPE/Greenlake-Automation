<#
.SYNOPSIS
  One-click launcher for Alletra Onboard. First run sets up the Python venv + Playwright;
  every run launches the operator web app at http://127.0.0.1:8765.

.PARAMETER Proxy
  Optional proxy for pip and the app (the jump box), e.g. http://proxy.example.net:8080.
  The launched DSCC browser reuses it automatically.

.EXAMPLE
  .\start.ps1
.EXAMPLE
  .\start.ps1 -Proxy http://proxy.example.net:8080
#>
param([string]$Proxy = "")
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

if ($Proxy) {
  $env:HTTPS_PROXY = $Proxy
  $env:HTTP_PROXY = $Proxy
  $env:NO_PROXY = "localhost,127.0.0.1,169.254.*"
}

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
  Write-Error "Python 3.12+ not found. Install it from https://www.python.org/downloads/ (tick 'Add to PATH'), then re-run this script."
  exit 1
}

$vpy = ".\.venv\Scripts\python.exe"
if (-not (Test-Path .venv)) {
  Write-Host "First run - creating the virtual environment and installing (this takes a few minutes)..." -ForegroundColor Cyan
  python -m venv .venv
  & $vpy -m pip install --upgrade pip | Out-Null
  & $vpy -m pip install -e .            # editable, so the bundled frontend/dist is served
  & $vpy -m playwright install chromium # Component B (cloudinit) launches a browser
}

Write-Host ""
Write-Host "Launching Alletra Onboard -> http://127.0.0.1:8765   (Ctrl+C to stop)" -ForegroundColor Green
& ".\.venv\Scripts\onboard.exe" ui
