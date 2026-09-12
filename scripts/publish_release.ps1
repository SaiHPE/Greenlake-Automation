<#
.SYNOPSIS
  Publish Alletra Onboard to a GitHub Release on whatever GitHub host `origin` points at.

.DESCRIPTION
  The ONE implementation of "publish a release". `.github/workflows/*.yml` call this script on
  github.com (hosted Windows runners); on github.hpe.com, where Actions is disabled for user-owned
  repos (2026-09-12), you run it by hand from the dev workstation or the jump box.

  Two modes:
    (default)      Rolling "latest": build the release zip (scripts/build_release.ps1) and refresh the
                   single `latest` release in place - assets clobbered, never delete+recreate.
    -Tag vX.Y.Z    Tagged release: upload the packaged .exe zips from dist/ (build them first with
                   -BuildExe, Windows only) to the tag's release; a pre-release when the tag has a '-'.

  Host, owner and repo are read from the git remote (-Remote, default `origin`), so the same script
  publishes to github.hpe.com (origin) and to github.com (-Remote github-com). Authentication is `gh`
  (gh auth login --hostname <host>); in Actions the workflow passes the job token via GH_TOKEN /
  GH_ENTERPRISE_TOKEN.

.EXAMPLE
  .\scripts\publish_release.ps1                       # build zip, refresh the rolling latest release
  .\scripts\publish_release.ps1 -NoBuild              # zip already in release/ (e.g. built by CI step)
  .\scripts\publish_release.ps1 -Tag vX.Y.Z-rc.N -BuildExe   # build the three .exe zips, upload to the tag
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
  # gh writes progress AND errors to stderr; under ErrorActionPreference=Stop PowerShell would treat
  # that as failure, so relax it for the call, echo everything to the log (the first rc.6 CI run
  # failed with only our own "does not exist" message because gh's 422 was swallowed here), and
  # return the exit code for the caller to judge.
  param([Parameter(ValueFromRemainingArguments)][string[]]$Args)
  $ErrorActionPreference = "Continue"
  try {
    & gh @Args 2>&1 | ForEach-Object { Write-Host "  gh> $_" -ForegroundColor DarkGray }
    return $LASTEXITCODE
  } finally { $ErrorActionPreference = "Stop" }
}

function Publish-Assets {
  # Create the release if it is missing, else upload into it. Create-then-upload is racy against a
  # human: on 2026-09-12 the operator published the tag's release from a browser between our
  # Test-Release and our create, and create returned 422 "tag_name already exists". Any create
  # failure therefore falls through to upload --clobber; Assert-Assets judges the outcome.
  param([string]$name, [string[]]$paths, [string[]]$createArgs)
  if (-not (Test-Release $name)) {
    Write-Host "Creating release '$name'" -ForegroundColor Cyan
    $rc = Invoke-Gh release create $name --repo $target @createArgs @paths
    if ($rc -eq 0) { return }
    Write-Host "create returned $rc - uploading into the existing release instead" -ForegroundColor Yellow
  } else {
    Write-Host "Release '$name' exists - uploading assets" -ForegroundColor Cyan
  }
  Invoke-Gh release upload $name --repo $target --clobber @paths | Out-Null
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
  Publish-Assets 'latest' $assets @('--title', $title, '--notes', $notes, '--latest')
  Invoke-Gh release edit latest --repo $target --title $title --notes $notes --latest | Out-Null
  Assert-Assets 'latest' $assets

  # The rolling release is ONE download for operators. Versioned zips from earlier builds
  # accumulate there (86 assets by rc.6 on github.com) and bury alletra-onboard-latest.zip; the
  # tagged releases hold the history, so drop everything on `latest` that is not this build.
  $ErrorActionPreference = "Continue"
  try { $json = & gh release view latest --repo $target --json assets 2>$null | Out-String } finally { $ErrorActionPreference = "Stop" }
  $keep = @($assets | ForEach-Object { Split-Path $_ -Leaf })
  $stale = @(($json | ConvertFrom-Json).assets | ForEach-Object { $_.name } | Where-Object { $_ -notin $keep })
  foreach ($name in $stale) {
    Write-Host "Removing stale asset $name from 'latest'" -ForegroundColor DarkGray
    Invoke-Gh release delete-asset latest $name --repo $target --yes | Out-Null
  }
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
Publish-Assets $Tag $exeAssets (@('--title', "Alletra Onboard $Tag", '--generate-notes') + $extra)
Assert-Assets $Tag $exeAssets
Write-Host "Published https://$target/releases/tag/$Tag" -ForegroundColor Green
