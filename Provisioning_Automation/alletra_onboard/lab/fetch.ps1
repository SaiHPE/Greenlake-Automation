<#
.SYNOPSIS
  Put this app folder on the code a developer sent with scripts/push_jumpbox_test.sh.

.DESCRIPTION
  The jump box cannot reach github.hpe.com. The developer's laptop keeps a small git store
  (lab-relay) and shares it into this Remote Desktop session, where it appears under \\tsclient.
  This finds it, fetches `jumpbox-test` and resets the app folder to it. Untracked files (.env,
  .venv, config\arrays.csv) are kept, as with any `git reset --hard`.

  Looked for, in order: -Relay, \\tsclient\lab-relay (the folder itself shared), then lab-relay inside
  every share the client offers (`net view \\tsclient`: a Mac home folder or a Windows drive), also
  under <share>\Users\<name>\ for a whole Windows drive.

.EXAMPLE
  .\lab\fetch.ps1
  .\lab\fetch.ps1 -Relay \\tsclient\D\work\lab-relay
#>
param([string]$Relay = "")
$ErrorActionPreference = "Stop"
Set-Location (Split-Path $PSScriptRoot -Parent)

function Test-Relay([string]$path) {
  if (-not $path) { return $false }
  try { return (Test-Path -LiteralPath (Join-Path $path 'HEAD')) -and (Test-Path -LiteralPath (Join-Path $path 'refs')) } catch { return $false }
}

if (-not $Relay) {
  $candidates = @('\\tsclient\lab-relay')
  $shares = @()
  try { $shares = @(& net view \\tsclient 2>$null | ForEach-Object { if ($_ -match '^(\S.*?)\s{2,}Disk') { $Matches[1].Trim() } }) } catch { }
  foreach ($share in $shares) {
    $root = "\\tsclient\$share"
    $candidates += Join-Path $root 'lab-relay'
    if (Test-Path (Join-Path $root 'Users')) {
      $candidates += Get-ChildItem (Join-Path $root 'Users') -Directory -ErrorAction SilentlyContinue | ForEach-Object { Join-Path $_.FullName 'lab-relay' }
    }
  }
  $Relay = $candidates | Where-Object { Test-Relay $_ } | Select-Object -First 1
}
if (-not (Test-Relay $Relay)) {
  Write-Host "No lab-relay found in this Remote Desktop session." -ForegroundColor Red
  Write-Host ("Shares offered by your computer: " + $(if ($shares) { $shares -join ', ' } else { 'none (folder sharing is off)' }))
  Write-Host "On your laptop: run scripts/push_jumpbox_test.sh, then share its ~/lab-relay folder in the"
  Write-Host "Remote Desktop settings (Mac Windows App: Edit PC > Folders; Windows mstsc: Local Resources >"
  Write-Host "More > Drives) and reconnect. Or name it: .\lab\fetch.ps1 -Relay \\tsclient\..."
  exit 1
}

# The share belongs to the laptop's user, which git counts as unsafe; trust it for this fetch only.
$ErrorActionPreference = "Continue"
& git -c "safe.directory=*" fetch --no-tags $Relay jumpbox-test
if ($LASTEXITCODE -ne 0) { Write-Host "git fetch from $Relay failed." -ForegroundColor Red; exit 1 }
& git reset -q --hard FETCH_HEAD
if ($LASTEXITCODE -ne 0) {
  Write-Host "git reset failed. If a file is locked: Get-Process git | Stop-Process -Force, then run again." -ForegroundColor Red
  exit 1
}
$ErrorActionPreference = "Stop"
Write-Host ("Now on: " + (& git log -1 --format=%s)) -ForegroundColor Green
