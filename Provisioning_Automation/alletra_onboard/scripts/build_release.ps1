<#
.SYNOPSIS
  Build a self-contained Alletra Onboard release zip (run on the dev workstation; needs Node + Python).

.DESCRIPTION
  Builds the React UI, stages just the runtime files (no node_modules / tests / captures / .venv),
  and zips them with the one-click start.ps1 at the root. Upload the zip to a GitHub Release so
  operators download ONE file, extract, and run start.ps1 - no git clone, no digging through subdirs.

.EXAMPLE
  .\scripts\build_release.ps1
#>
param([string]$Version = "")
$ErrorActionPreference = "Stop"
$pkg = Split-Path $PSScriptRoot -Parent
Set-Location $pkg

if (-not $Version) {
  $m = Select-String -Path (Join-Path $pkg 'pyproject.toml') -Pattern '^version\s*=\s*"([^"]+)"' | Select-Object -First 1
  if (-not $m) { throw "Could not read version from pyproject.toml" }
  $Version = $m.Matches[0].Groups[1].Value
}
Write-Host "== Building alletra-onboard v$Version ==" -ForegroundColor Cyan

# 1. Build the UI. npm writes notices to stderr; under ErrorActionPreference=Stop PowerShell
# would treat that as a failure, so drop to Continue here and check exit codes explicitly.
Push-Location frontend
try {
  $ErrorActionPreference = "Continue"
  & npm install
  if ($LASTEXITCODE -ne 0) { throw "npm install failed (exit $LASTEXITCODE)" }
  & npm run build
  if ($LASTEXITCODE -ne 0) { throw "npm run build failed (exit $LASTEXITCODE)" }
} finally {
  $ErrorActionPreference = "Stop"
  Pop-Location
}
if (-not (Test-Path frontend\dist\index.html)) { throw "frontend build did not produce dist/index.html" }

# 2. Stage runtime files only
$releaseDir = Join-Path $pkg 'release'
$stage = Join-Path $releaseDir 'alletra-onboard'
if (Test-Path $releaseDir) { Remove-Item -Recurse -Force $releaseDir }
New-Item -ItemType Directory -Force "$stage\frontend", "$stage\config", "$stage\scripts" | Out-Null

Copy-Item -Recurse src "$stage\src"
Copy-Item -Recurse frontend\dist "$stage\frontend\dist"
Copy-Item pyproject.toml, README.md "$stage\"
Copy-Item config\arrays.example.csv "$stage\config\"
Copy-Item scripts\setup_jumpbox.ps1 "$stage\scripts\"
Copy-Item scripts\start.ps1 "$stage\start.ps1"
Copy-Item scripts\start.cmd "$stage\start.cmd"   # double-click launcher (bypasses exec policy, self-elevates)

# drop compiled caches so the zip is clean
Get-ChildItem -Recurse -Directory -Filter __pycache__ $stage | Remove-Item -Recurse -Force

# 3. Zip (top-level folder is alletra-onboard\)
$zip = Join-Path $releaseDir "alletra-onboard-$Version.zip"
Compress-Archive -Path $stage -DestinationPath $zip -Force
$sha = (Get-FileHash $zip -Algorithm SHA256).Hash
"$sha  alletra-onboard-$Version.zip" | Out-File (Join-Path $releaseDir "alletra-onboard-$Version.zip.sha256") -Encoding ascii

Write-Host ""
Write-Host "Built $zip" -ForegroundColor Green
Write-Host "SHA256 $sha"
Write-Host ""
Write-Host "Publish it:" -ForegroundColor Cyan
Write-Host "  gh release create v$Version `"$zip`" `"$zip.sha256`" --title `"Alletra Onboard v$Version`" --notes `"...`""
Write-Host "Operators then: download the zip, extract, run start.ps1 (no git needed)."
