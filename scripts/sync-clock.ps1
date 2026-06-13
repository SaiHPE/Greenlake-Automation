<#
.SYNOPSIS
  Set the system clock from an HTTPS Date header (for hosts where UDP/NTP port 123 is blocked
  but an HTTPS proxy works, e.g. the jump box).

.DESCRIPTION
  DSCC login fails with "iat is in the future" when the host clock drifts behind real time.
  NTP can't fix it here (UDP 123 is firewalled and proxies don't carry NTP), so this reads the
  authoritative Date header from an HTTPS endpoint through the proxy and sets the clock from it
  (accurate to ~1s — plenty for JWT validation). Requires Administrator (Set-Date).

.PARAMETER Url
  HTTPS URL whose Date header to trust. Default: https://www.hpe.com.

.PARAMETER Proxy
  Proxy URL. Default: the HTTPS_PROXY environment variable.

.EXAMPLE
  .\scripts\sync-clock.ps1
.EXAMPLE
  .\scripts\sync-clock.ps1 -Url https://console-jp1.data.cloud.hpe.com
#>
param(
  [string]$Url = "https://www.hpe.com",
  [string]$Proxy = $env:HTTPS_PROXY
)
$ErrorActionPreference = "Stop"

$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole(
  [Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
  Write-Error "Run this as Administrator (Set-Date requires elevation)."
  exit 1
}

$params = @{ Uri = $Url; UseBasicParsing = $true }
if ($Proxy) { $params.Proxy = $Proxy }
$resp = Invoke-WebRequest @params

$dateHeader = [string]$resp.Headers.Date
if (-not $dateHeader) { Write-Error "No Date header returned from $Url"; exit 1 }

$before = Get-Date
Set-Date ([DateTimeOffset]::Parse($dateHeader).LocalDateTime) | Out-Null
Write-Host "Clock synced from $Url" -ForegroundColor Green
Write-Host ("  server : {0}" -f $dateHeader)
Write-Host ("  was    : {0:u}" -f $before)
Write-Host ("  now    : {0:u}" -f (Get-Date))
