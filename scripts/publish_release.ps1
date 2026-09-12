<#
.SYNOPSIS
  Publish Alletra Onboard to a GitHub Release on whatever GitHub host `origin` points at.

.DESCRIPTION
  The ONE implementation of "publish a release". `.github/workflows/*.yml` call this script; you can
  run it by hand from the dev workstation or the jump box when no Actions runner is available
  (github.hpe.com has Actions disabled for user-owned repos as of 2026-09-12).

  Two modes:
    (default)      Rolling "latest": build the release zip (scripts/build_release.ps1) and refresh the
                   single `latest` release in place - assets clobbered, never delete+recreate.
    -Tag vX.Y.Z    Tagged release: upload the packaged .exe zips from dist/ (build them first with
                   -BuildExe, Windows only) to the tag's release; a pre-release when the tag has a '-'.

  Host, owner and repo are read from `git remote get-url origin`, so the same script works against
  github.hpe.com and github.com. Authentication is `gh` (gh auth login --hostname <host>); in Actions
  the workflow passes the job token via GH_TOKEN / GH_ENTERPRISE_TOKEN.

.EXAMPLE
  .\scripts\publish_release.ps1                       # build zip, refresh the rolling latest release
  .\scripts\publish_release.ps1 -NoBuild              # zip already in release/ (e.g. built by CI step)
  .\scripts\publish_release.ps1 -Tag v0.16.0-rc.6 -BuildExe   # build the three .exe zips, upload to the tag
#>
[CmdletBinding()]
param(
  [string]$Tag = "",
  [switch]$NoBuild,
  [switch]$BuildExe,
  [string]$Remote = "origin"
)
$ErrorActionPreference = "Stop"
$pkg = Split-Path $PSScriptRoot -Parent
Set-Location $pkg

if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
  throw "GitHub CLI (gh) is required: https://cli.github.com - then 'gh auth login --hostname <your GitHub host>'."
}

# --- where are we publishing? (host/owner/repo from the git remote) ---------------------------------
$url = (& git remote get-url $Remote).Trim()
if (-not $url) { throw "No git remote named '$Remote'." }
if ($url -match '^https?://([^/]+)/([^/]+)/([^/]+?)(?:\.git)?/?$') {
  $ghHost, $owner, $repo = $Matches[1], $Matches[2], $Matches[3]
} elseif ($url -match '^git@([^:]+):([^/]+)/([^/]+?)(?:\.git)?$') {
  $ghHost, $owner, $repo = $Matches[1], $Matches[2], $Matches[3]
} else {
  throw "Cannot parse remote URL '$url'."
}
$target = "$ghHost/$owner/$repo"
Write-Host "== Publishing to https://$target ==" -ForegroundColor Cyan

$m = Select-String -Path (Join-Path $pkg 'pyproject.toml') -Pattern '^version\s*=\s*"([^"]+)"' | Select-Object -First 1
if (-not $m) { throw "Could not read version from pyproject.toml" }
$ver = $m.Matches[0].Groups[1].Value
$sha = (& git rev-parse --short HEAD).Trim()

function Invoke-Gh {
  # gh writes progress to stderr; under ErrorActionPreference=Stop PowerShell would treat that as
  # failure, so relax it for the call and check the exit code ourselves.
  param([Parameter(ValueFromRemainingArguments)][string[]]$Args)
  $ErrorActionPreference = "Continue"
  try { & gh @Args 2>&1 | ForEach-Object { "$_" } ; return $LASTEXITCODE } finally { $ErrorActionPreference = "Stop" }
}

function Test-Release([string]$name) {
  $ErrorActionPreference = "Continue"
  try { & gh release view $name --repo $target *> $null; return ($LASTEXITCODE -eq 0) } finally { $ErrorActionPreference = "Stop" }
}

function Assert-Assets([string]$name, [string[]]$paths) {
  # The outcome is the truth, not gh's exit code: on GHES 3.16 `gh release create` uploads every
  # asset and then exits 1 (measured 2026-09-12 against github.hpe.com), so a caller that trusted the
  # code would report failure for a release that is complete. Check the release itself.
  $ErrorActionPreference = "Continue"
  try { $json = & gh release view $name --repo $target --json assets 2>$null | Out-String } finally { $ErrorActionPreference = "Stop" }
  if (-not $json) { throw "Release '$name' does not exist on $target after publishing." }
  $have = @(($json | ConvertFrom-Json).assets | ForEach-Object { $_.name })
  $missing = @($paths | ForEach-Object { Split-Path $_ -Leaf } | Where-Object { $_ -notin $have })
  if ($missing) { throw "Release '$name' is missing asset(s): $($missing -join ', ')" }
}

if (-not $Tag) {
  # ---------------------------------------------------------------- rolling "latest" ----------------
  if (-not $NoBuild) { & (Join-Path $PSScriptRoot 'build_release.ps1'); if ($LASTEXITCODE -ne 0) { throw "build_release.ps1 failed" } }
  $zip = Join-Path $pkg "release/alletra-onboard-$ver.zip"
  if (-not (Test-Path $zip)) { throw "Release zip not found: $zip (run without -NoBuild)" }
  Copy-Item $zip (Join-Path $pkg "release/alletra-onboard-latest.zip") -Force
  $assets = @($zip, "$zip.sha256", (Join-Path $pkg "release/alletra-onboard-latest.zip"))

  $subject = (& git log -1 --format=%s).Trim()
  $notes = "Automated build from ``main`` @ $sha.`n`n$subject`n`nDownload **alletra-onboard-latest.zip**, extract, and run ``start.cmd``."
  $title = "Alletra Onboard v$ver (latest build from main)"

  # Create the release once; thereafter refresh notes + clobber the assets in place, so a failed
  # upload can never leave the operators' download link pointing at nothing.
  if (Test-Release 'latest') {
    Write-Host "Refreshing existing 'latest' release" -ForegroundColor Cyan
    Invoke-Gh release edit latest --repo $target --title $title --notes $notes | Out-Null
    Invoke-Gh release upload latest --repo $target --clobber @assets | Out-Null
  } else {
    Write-Host "Creating 'latest' release" -ForegroundColor Cyan
    Invoke-Gh release create latest --repo $target --title $title --notes $notes @assets | Out-Null
  }
  Assert-Assets 'latest' $assets
  Write-Host "Published https://$target/releases/latest" -ForegroundColor Green
  exit 0
}

# ---------------------------------------------------------------- tagged (.exe) release -----------
if ($BuildExe) {
  if (-not $IsWindows) { throw "-BuildExe needs Windows (PyInstaller builds the .exe for the platform it runs on)." }
  foreach ($flags in @(@(), @('-Chromium'), @('-Profile', 'init-only'))) {
    & (Join-Path $PSScriptRoot 'build_exe.ps1') @flags
    if ($LASTEXITCODE -ne 0) { throw "build_exe.ps1 $flags failed" }
  }
}
$exeAssets = @(
  'dist/alletra-onboard-win64.zip', 'dist/alletra-onboard-win64.zip.sha256',
  'dist/alletra-onboard-offline-win64.zip', 'dist/alletra-onboard-offline-win64.zip.sha256',
  'dist/alletra-mp-initialization-win64.zip', 'dist/alletra-mp-initialization-win64.zip.sha256'
) | ForEach-Object { Join-Path $pkg $_ } | Where-Object { Test-Path $_ }
if (-not $exeAssets) { throw "No .exe zips in dist/. Build them on Windows: publish_release.ps1 -Tag $Tag -BuildExe" }

# A semver pre-release tag (v0.13.0-rc.1) is published as a pre-release, so a candidate built for
# review never presents itself as the current stable download.
$extra = if ($Tag -like '*-*') { @('--prerelease') } else { @() }
if (Test-Release $Tag) {
  Invoke-Gh release upload $Tag --repo $target --clobber @exeAssets | Out-Null
} else {
  Invoke-Gh release create $Tag --repo $target --title "Alletra Onboard $Tag" --generate-notes @extra @exeAssets | Out-Null
}
Assert-Assets $Tag $exeAssets
Write-Host "Published https://$target/releases/tag/$Tag" -ForegroundColor Green
