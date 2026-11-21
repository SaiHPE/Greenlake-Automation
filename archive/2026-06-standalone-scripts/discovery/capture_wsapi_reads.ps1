<#
.SYNOPSIS
  S-0 (SPEC-001): read-only WSAPI capture of hosts, host sets, volumes, volume sets and VLUNs.

.DESCRIPTION
  PowerShell twin of scripts/discovery/asbuilt_wsapi.py for a jump box without Python. Logs in to
  WSAPI, GETs the five object lists the provisioning plan compares against, writes each response
  verbatim to script-logs\wsapi-<array>-<timestamp>\<name>.json, and deletes the session key.

  Read-only: only GET calls after the login POST; the session is closed with DELETE /credentials.
  Nothing on the array changes. The password is prompted (never a parameter, never logged).

  Works on Windows PowerShell 5.1 and PowerShell 7. TLS validation is skipped for the array's
  self-signed certificate, for this process only.

.PARAMETER Array     Array management IP (default: rack13arcus).
.PARAMETER User      WSAPI user (default 3paradm).
.PARAMETER OutRoot   Where to write the capture folder (default .\script-logs).

.EXAMPLE
  .\scripts\discovery\capture_wsapi_reads.ps1 -Array 10.132.30.121
  Then copy the folder to tests\fixtures\rack13_wsapi\ and pin the parsers to it.
#>
param(
  [string]$Array = '10.132.30.121',
  [string]$User = '3paradm',
  [string]$OutRoot = '.\script-logs'
)
$ErrorActionPreference = 'Stop'

$base = "https://$Array/api/v1"
$stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$outDir = Join-Path $OutRoot "wsapi-$Array-$stamp"
New-Item -ItemType Directory -Path $outDir -Force | Out-Null

# The array is on the internal management network: never route it through the jump-box proxy.
$common = @{ TimeoutSec = 60 }
if ($PSVersionTable.PSVersion.Major -ge 6) {
  $common['SkipCertificateCheck'] = $true
  $common['NoProxy'] = $true
} else {
  [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.SecurityProtocolType]::Tls12
  [System.Net.ServicePointManager]::ServerCertificateValidationCallback = { $true }
  [System.Net.WebRequest]::DefaultWebProxy = $null
}

$secure = Read-Host -Prompt "WSAPI password for $User@$Array" -AsSecureString
$plain = [System.Net.NetworkCredential]::new('', $secure).Password

Write-Host "POST $base/credentials"
$login = Invoke-RestMethod @common -Method Post -Uri "$base/credentials" -ContentType 'application/json' `
  -Body (@{ user = $User; password = $plain } | ConvertTo-Json)
$plain = $null
$key = $login.key
if (-not $key) { throw 'login returned no session key' }
$headers = @{ 'X-HP3PAR-WSAPI-SessionKey' = $key }

try {
  foreach ($name in 'hosts', 'hostsets', 'volumes', 'volumesets', 'vluns') {
    $uri = "$base/$name"
    Write-Host "GET  $uri"
    # -UseBasicParsing keeps 5.1 from touching IE; the raw body is what the fixture must hold.
    $resp = Invoke-WebRequest @common -Method Get -Uri $uri -Headers $headers -UseBasicParsing
    $path = Join-Path $outDir "$name.json"
    [System.IO.File]::WriteAllText((Resolve-Path $outDir).Path + "\$name.json", $resp.Content, [System.Text.Encoding]::UTF8)
    $total = ($resp.Content | ConvertFrom-Json).total
    Write-Host ("     -> {0}  (total={1}, {2} bytes)" -f $path, $total, $resp.Content.Length)
  }
} finally {
  Write-Host "DELETE $base/credentials/<key>"
  try { Invoke-RestMethod @common -Method Delete -Uri "$base/credentials/$key" -Headers $headers | Out-Null }
  catch { Write-Warning "session delete failed: $($_.Exception.Message) (the key expires on its own)" }
}

Write-Host ""
Write-Host "Capture complete: $outDir"
Write-Host "Copy the folder to tests\fixtures\rack13_wsapi\ and attach it to the SPEC-001 S-0 line."
