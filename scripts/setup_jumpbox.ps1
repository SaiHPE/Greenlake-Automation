<#
.SYNOPSIS
  Install alletra-onboard on the jump box: create venv, install the package, health-check.

.DESCRIPTION
  Run this from the alletra_onboard package directory (the folder containing pyproject.toml),
  after copying/cloning the repo onto the jump box. Component A (GreenLake REST) needs only
  internet egress to GreenLake; it does NOT need the Playwright browser download.

.PARAMETER Proxy
  Optional proxy URL for pip AND the GreenLake API calls, e.g.
  http://proxy.example.net:8080
  (httpx honors HTTPS_PROXY, which this script sets for the health check.)

.EXAMPLE
  .\scripts\setup_jumpbox.ps1 -Proxy http://proxy.example.net:8080
#>
param([string]$Proxy = "")

$ErrorActionPreference = "Stop"
Write-Host "== alletra-onboard jump box setup ==" -ForegroundColor Cyan

if (-not (Test-Path pyproject.toml)) {
    Write-Error "Run this from the alletra_onboard package directory (where pyproject.toml is)."
    exit 1
}

# 1. Python 3.12+
$py = Get-Command python -ErrorAction SilentlyContinue
if (-not $py) {
    Write-Error "Python not found. Install Python 3.12+ from https://www.python.org/downloads/ (check 'Add to PATH'), then re-run."
    exit 1
}
Write-Host ("Python: " + (python --version))

# 2. Proxy (for pip, git already configured separately, and httpx via HTTPS_PROXY)
if ($Proxy) {
    $env:HTTP_PROXY = $Proxy
    $env:HTTPS_PROXY = $Proxy
    Write-Host "Using proxy: $Proxy"
}

# 3. venv
if (-not (Test-Path .venv)) { python -m venv .venv }
$vpy = ".\.venv\Scripts\python.exe"

# 4. install (runtime deps only; append '[dev]' if you also want to run the test suite)
& $vpy -m pip install --upgrade pip | Out-Null
$pipArgs = @("-m", "pip", "install", "-e", ".")
if ($Proxy) { $pipArgs += @("--proxy", $Proxy) }
& $vpy @pipArgs
Write-Host "Package installed." -ForegroundColor Green

# 5. credentials + health check
if (Test-Path .env) {
    Write-Host "== read-only health check ==" -ForegroundColor Cyan
    & ".\.venv\Scripts\onboard.exe" check
} else {
    Write-Host "No .env found. Add GreenLake credentials with:" -ForegroundColor Yellow
    Write-Host "    .\.venv\Scripts\onboard.exe configure" -ForegroundColor Yellow
    Write-Host "then run:  .\.venv\Scripts\onboard.exe check"
}
Write-Host "Setup complete." -ForegroundColor Green
