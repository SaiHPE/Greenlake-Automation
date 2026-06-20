<#
.SYNOPSIS
  Build a self-contained Alletra Onboard .exe (PyInstaller, onedir) — no Python needed to run it.

.DESCRIPTION
  Runs PyInstaller against alletra_onboard.spec, bundling the app + React UI + Discovery Tool.
  Without -Chromium: the SLIM build (downloads Chromium on first run) -> alletra-onboard-win64.zip.
  With    -Chromium: the OFFLINE build (Chromium bundled) -> alletra-onboard-offline-win64.zip.
  Always emits the zip + a .sha256 next to it under dist\.

.PARAMETER SkipInstall  Skip pip/playwright install (deps already present, e.g. in CI).
.PARAMETER Chromium     Bundle Chromium (the offline build).
#>
param([switch]$SkipInstall, [switch]$Chromium)
$ErrorActionPreference = 'Stop'
Set-Location (Join-Path $PSScriptRoot '..')

# Use the project .venv if it exists (local dev); otherwise the Python on PATH (CI installs the
# deps into the system Python). Only create a .venv when we're going to populate it.
if (Test-Path '.\.venv\Scripts\python.exe') {
  $py = '.\.venv\Scripts\python.exe'
} elseif (-not $SkipInstall) {
  python -m venv .venv
  $py = '.\.venv\Scripts\python.exe'
} else {
  $py = 'python'
}

if (-not $SkipInstall) {
  & $py -m pip install --upgrade pip | Out-Null
  & $py -m pip install -e . | Out-Null
  & $py -m pip install pyinstaller | Out-Null
  & $py -m playwright install chromium
}

if ($Chromium) {
  $env:ALLETRA_BUNDLE_CHROMIUM = '1'
  $zip = 'dist\alletra-onboard-offline-win64.zip'
} else {
  Remove-Item Env:\ALLETRA_BUNDLE_CHROMIUM -ErrorAction SilentlyContinue
  $zip = 'dist\alletra-onboard-win64.zip'
}

Remove-Item -Recurse -Force build, 'dist\AlletraOnboard' -ErrorAction SilentlyContinue
& $py -m PyInstaller --noconfirm --clean alletra_onboard.spec
if ($LASTEXITCODE -ne 0) { throw "PyInstaller failed (exit $LASTEXITCODE)" }

Remove-Item $zip, "$zip.sha256" -ErrorAction SilentlyContinue
Compress-Archive -Path 'dist\AlletraOnboard' -DestinationPath $zip -CompressionLevel Optimal
((Get-FileHash $zip -Algorithm SHA256).Hash.ToLower() + '  ' + (Split-Path $zip -Leaf)) |
  Out-File "$zip.sha256" -Encoding ascii
Write-Host "Built $zip"
