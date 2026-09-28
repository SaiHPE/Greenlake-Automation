<#
.SYNOPSIS
  SPEC-014 live check: discovery of the sheet's hosts (serial, WWPN, IQN, per OS) - READ-ONLY.

.DESCRIPTION
  Drives the running Alletra Onboard app over its own HTTP API against ANY array (training array,
  Landing Zone, Vault Zone) and asserts what discovery reports for the hosts you list in -HostsFile:

    Discover   every Hosts-tab row is listed (R1); each row's expectation holds (found / not_found /
               read_ok / read_fail / blocked); vCenter returned serial numbers (R2)
    Zoning     the looked-up WWPNs reach the zoning plan (switch reads only; -SkipZoning to omit)
    Plan       a typed WWPN the server does not have is a blocker (R6); an unfound row is noted
    Secrets    no host / array password in GET /runs/{id} or any run event (R7)
    Read-only  the array's WSAPI counts are identical before and after

  NOTHING IS WRITTEN ANYWHERE. The runner never calls /storage/apply, never opens SSH or WinRM itself
  (the app does the host logins), never talks to a switch. The zz_s14_* names exist only in the
  plan preview. Safe on a production array.

  Writes hosts-session-<stamp>\report.md plus every API response and WSAPI read. Exit 1 on any FAIL.

.PARAMETER BaseSheet  The environment's Initialisation_sheet.xlsx (array, vCenter, switch IPs and
                      users come from it; its Volumes / Host sets / Hosts tabs are REPLACED in a copy).
.PARAMETER HostsFile  CSV: name,os,address,wwpns,iqn,username,expect,expect_serial,expect_wwpns
                      expect = found | not_found | read_ok | read_fail | blocked. Passwords are asked
                      for, once per username@address, and never written to disk.
.PARAMETER Api        The app's API (default http://127.0.0.1:8765).
.PARAMETER Cpg        CPG for the preview-only volume (default: the first CPG the array reports).
.PARAMETER SkipZoning Do not build the zoning plan (no switch logins).
.PARAMETER OutRoot    Where the hosts-session-<stamp> folder goes (default: next to this script).

.EXAMPLE
  .\hosts_session.cmd -BaseSheet C:\sheets\Initialisation_sheet_LZ.xlsx -HostsFile C:\sheets\hosts_LZ.csv
#>
[CmdletBinding()]
param(
  [Parameter(Mandatory = $true)][string]$BaseSheet,
  [Parameter(Mandatory = $true)][string]$HostsFile,
  [string]$Api = 'http://127.0.0.1:8765',
  [string]$Cpg = '',
  [switch]$SkipZoning,
  [string]$OutRoot = ''
)
$ErrorActionPreference = 'Stop'
if (-not $OutRoot) {
  $OutRoot = if ($PSScriptRoot) { $PSScriptRoot } else { Split-Path -Parent $MyInvocation.MyCommand.Path }
  if (-not $OutRoot) { $OutRoot = (Get-Location).Path }
}
$Prefix = 'zz_s14_'
$PollSeconds = 1; $CeilingSeconds = 600
$Expectations = @('found', 'not_found', 'read_ok', 'read_fail', 'blocked')

# ------------------------------------------------------------------ evidence folder + report

$stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$Out = Join-Path $OutRoot "hosts-session-$stamp"
New-Item -ItemType Directory -Path $Out -Force | Out-Null
$Out = (Resolve-Path $Out).Path
$script:Seq = 0
$script:Results = New-Object System.Collections.ArrayList
$script:Section = ''

function Write-Evidence([string]$name, [string]$text) {
  $script:Seq++
  $file = Join-Path $Out ('{0:D2}-{1}' -f $script:Seq, $name)
  [System.IO.File]::WriteAllText($file, $text, [System.Text.UTF8Encoding]::new($false))
  return (Split-Path $file -Leaf)
}
function Check([string]$what, [bool]$ok, [string]$detail = '') {
  $verdict = if ($ok) { 'PASS' } else { 'FAIL' }
  [void]$script:Results.Add([pscustomobject]@{ Section = $script:Section; Verdict = $verdict; What = $what; Detail = $detail })
  $color = if ($ok) { 'Green' } else { 'Red' }
  Write-Host ("  [{0}] {1}{2}" -f $verdict, $what, $(if ($detail) { " - $detail" } else { '' })) -ForegroundColor $color
}
function Section([string]$title) { $script:Section = $title; Write-Host ""; Write-Host "== $title" -ForegroundColor Cyan }
function Note([string]$text) { Write-Host "  $text" -ForegroundColor DarkGray }

# ------------------------------------------------------------------ HTTP (same transport as session.ps1)

$script:TlsCallback = 'not needed (PowerShell 6+)'
if ($PSVersionTable.PSVersion.Major -lt 6) {
  [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.SecurityProtocolType]::Tls12
  # Compiled callback: a script-block one only survives the first TLS handshake on 5.1 (LESSONS 40).
  try {
    Add-Type -IgnoreWarnings -TypeDefinition @'
using System.Net;
public static class HostsSessionTrustArrayCert {
  public static void Enable() { ServicePointManager.ServerCertificateValidationCallback = delegate { return true; }; }
}
'@ -ErrorAction Stop
    [HostsSessionTrustArrayCert]::Enable()
    $script:TlsCallback = 'compiled'
  } catch {
    $script:TlsCallback = "SCRIPT-BLOCK FALLBACK - Add-Type failed: $($_.Exception.Message)"
    [System.Net.ServicePointManager]::ServerCertificateValidationCallback = { $true }
  }
  [System.Net.WebRequest]::DefaultWebProxy = $null
}
$Common = @{ TimeoutSec = 180; UseBasicParsing = $true }
if ($PSVersionTable.PSVersion.Major -ge 6) { $Common['SkipCertificateCheck'] = $true; $Common['NoProxy'] = $true }

function Invoke-Json {
  param([string]$Method, [string]$Uri, $Body = $null, [hashtable]$Headers = @{}, [string]$Save = '')
  $req = @{ Method = $Method; Uri = $Uri; Headers = $Headers }
  if ($null -ne $Body) { $req['ContentType'] = 'application/json'; $req['Body'] = ($Body | ConvertTo-Json -Depth 12 -Compress) }
  try {
    $resp = Invoke-WebRequest @Common @req
    $status = [int]$resp.StatusCode
    $text = if ($resp.RawContentStream) { [System.Text.Encoding]::UTF8.GetString($resp.RawContentStream.ToArray()) } else { $resp.Content }
  } catch [System.Net.WebException] {
    $r = $_.Exception.Response
    if ($null -eq $r) { throw }
    $status = [int]$r.StatusCode
    $text = $_.ErrorDetails.Message
  } catch {
    if ($_.Exception.Response) { $status = [int]$_.Exception.Response.StatusCode; $text = $_.ErrorDetails.Message } else { throw }
  }
  if ($Save) { Write-Evidence "$Save.json" $text | Out-Null }
  $json = $null
  if ($text) { try { $json = $text | ConvertFrom-Json } catch { $json = $null } }
  return @{ Status = $status; Text = $text; Json = $json }
}
function Api([string]$Method, [string]$Path, $Body = $null, [string]$Save = '') {
  return Invoke-Json -Method $Method -Uri "$Api$Path" -Body $Body -Save $Save
}
function ApiOk([string]$Method, [string]$Path, $Body = $null, [string]$Save = '') {
  $r = Api $Method $Path $Body $Save
  if ($r.Status -lt 200 -or $r.Status -ge 300) { throw "$Method $Path -> HTTP $($r.Status): $($r.Text)" }
  return $r.Json
}
function Event-Count([string]$RunId) { return @((Api 'GET' "/runs/$RunId/events").Json.events).Count }
function Run-Step {
  # POST a step, then wait (by event, not run status) for one of $Types after the POST.
  param([string]$RunId, [string]$Path, $Body, [string[]]$Types, [string]$Save)
  $since = Event-Count $RunId
  $r = Api 'POST' "/runs/$RunId$Path" $Body "$Save-post"
  if ($r.Status -lt 200 -or $r.Status -ge 300) { throw "POST $Path -> HTTP $($r.Status): $($r.Text)" }
  $Types = @($Types) + 'step.crashed'
  $deadline = (Get-Date).AddSeconds($CeilingSeconds)
  $found = $null
  while ((Get-Date) -lt $deadline -and -not $found) {
    Start-Sleep -Seconds $PollSeconds
    $events = @((Api 'GET' "/runs/$RunId/events").Json.events)
    for ($i = $events.Count - 1; $i -ge $since; $i--) {
      if ($Types -contains $events[$i].event_type) { $found = $events[$i]; break }
    }
  }
  if (-not $found) { throw "waited ${CeilingSeconds}s for $($Types -join '|') after POST $Path" }
  Write-Evidence "$Save.json" ($found | ConvertTo-Json -Depth 20) | Out-Null
  if ($found.event_type -eq 'step.crashed') { throw "step crashed: $($found.message)" }
  return $found
}

# ------------------------------------------------------------------ WSAPI, read-only (the before/after proof)

$script:Wsapi = $null
function Wsapi-Login([string]$ArrayHost, [string]$User, [string]$Password) {
  $base = "https://$ArrayHost/api/v1"
  $login = Invoke-Json -Method 'POST' -Uri "$base/credentials" -Body @{ user = $User; password = $Password }
  if ($login.Status -ne 201 -and $login.Status -ne 200) { throw "WSAPI login failed: HTTP $($login.Status) $($login.Text)" }
  $script:Wsapi = @{ Base = $base; Headers = @{ 'X-HP3PAR-WSAPI-SessionKey' = $login.Json.key } }
}
function Wsapi-Logout() {
  if ($script:Wsapi) { try { Invoke-Json -Method 'DELETE' -Uri "$($script:Wsapi.Base)/credentials/$($script:Wsapi.Headers['X-HP3PAR-WSAPI-SessionKey'])" -Headers $script:Wsapi.Headers | Out-Null } catch {} }
}
function Wsapi-Counts([string]$when) {
  $counts = [ordered]@{}
  foreach ($name in 'hosts', 'hostsets', 'volumes', 'volumesets', 'vluns') {
    $r = Invoke-Json -Method 'GET' -Uri "$($script:Wsapi.Base)/$name" -Headers $script:Wsapi.Headers
    if ($r.Status -ne 200) { throw "WSAPI GET $name -> HTTP $($r.Status)" }
    Write-Evidence "wsapi-$name-$when.json" $r.Text | Out-Null
    $members = @($r.Json.members)
    if ($name -eq 'vluns') { $members = @($members | Where-Object { $_.active -ne $true }) }
    $counts[$name] = $members.Count
  }
  return $counts
}

# ------------------------------------------------------------------ sheet + rows

function Read-SheetBytes([string]$path) {
  $fs = [System.IO.File]::Open((Resolve-Path $path).Path, [System.IO.FileMode]::Open, [System.IO.FileAccess]::Read, [System.IO.FileShare]::ReadWrite)
  try { $ms = New-Object System.IO.MemoryStream; $fs.CopyTo($ms); return $ms.ToArray() } finally { $fs.Dispose() }
}
$BaseB64 = [Convert]::ToBase64String((Read-SheetBytes $BaseSheet))
function Compose($targets, $volumes, $hostsets, $hosts, [string]$Save) {
  $body = @{ base_b64 = $BaseB64; targets = $targets }
  if ($null -ne $volumes) { $body['volumes'] = $volumes }
  if ($null -ne $hostsets) { $body['hostsets'] = $hostsets }
  if ($null -ne $hosts) { $body['hosts'] = $hosts }
  $r = Api 'POST' '/init-sheet/compose' $body
  if ($r.Status -ne 200) { throw "compose -> HTTP $($r.Status): $($r.Text)" }
  Write-Evidence "$Save.txt" "composed sheet: $($r.Json.content_b64.Length) base64 chars" | Out-Null
  return $r.Json.content_b64
}
function Upload([string]$b64, [string]$Save) {
  $r = ApiOk 'POST' '/init-sheet/upload' @{ content_b64 = $b64 }
  if ($r.work_item -and $r.work_item.PSObject.Properties['subscription_key']) { $r.work_item.subscription_key = '<redacted>' }
  Write-Evidence "$Save.json" ($r | ConvertTo-Json -Depth 12) | Out-Null
  return $r
}
function Split-Ids([string]$text) {
  return @(($text -split '[,; ]+') | Where-Object { $_ } | ForEach-Object { (($_ -replace '[^0-9A-Fa-f]', '')).ToUpper() })
}

$Rows = @(Import-Csv -Path $HostsFile)
if ($Rows.Count -eq 0) { Write-Host "$HostsFile has no rows." -ForegroundColor Red; exit 1 }
foreach ($row in $Rows) {
  foreach ($col in 'name', 'os', 'address', 'wwpns', 'iqn', 'username', 'expect', 'expect_serial', 'expect_wwpns') {
    if (-not $row.PSObject.Properties[$col]) { $row | Add-Member -NotePropertyName $col -NotePropertyValue '' }
  }
  if ($Expectations -notcontains $row.expect) {
    Write-Host "Row '$($row.name)': expect must be one of $($Expectations -join ', ') (got '$($row.expect)')." -ForegroundColor Red; exit 1
  }
}

# ------------------------------------------------------------------ prompts

Write-Host "SPEC-014 hosts session (read-only) - evidence folder: $Out"
try { $health = Api 'GET' '/health' $null 'health' } catch { $health = @{ Status = 0; Text = $_.Exception.Message } }
if ($health.Status -ne 200) {
  Write-Host "The app is not answering at $Api ($($health.Text)). Start it, then run this again." -ForegroundColor Red
  exit 1
}
$Version = $health.Json.version
Write-Host "App version: $Version"

function Read-Secret([string]$prompt) {
  $s = Read-Host -Prompt $prompt -AsSecureString
  return [System.Net.NetworkCredential]::new('', $s).Password
}
$ArrayPw = Read-Secret 'Array admin password'
$VcPw = Read-Secret 'vCenter password'
$Targets = @{ prov_array_password = $ArrayPw; prov_vcenter_password = $VcPw }
if (-not $SkipZoning) {
  $SwPw = Read-Secret 'Switch password (both fabrics; -SkipZoning to skip)'
  $Targets['prov_sw1_password'] = $SwPw; $Targets['prov_sw2_password'] = $SwPw
}
$HostPw = @{}
foreach ($row in $Rows) {
  if (-not $row.username) { continue }
  $key = "$($row.username)@$($row.address)"
  if (-not $HostPw.ContainsKey($key)) { $HostPw[$key] = Read-Secret "Hosts tab login password for $key" }
}
$Secrets = @($ArrayPw, $VcPw) + @($HostPw.Values) | Where-Object { $_ -and $_.Length -ge 4 }

$HostRows = @($Rows | ForEach-Object {
  $h = @{ name = $_.name; os = $_.os; address = $_.address; wwpns = $_.wwpns; iqn = $_.iqn }
  if ($_.username) { $h['username'] = $_.username; $h['password'] = $HostPw["$($_.username)@$($_.address)"] }
  $h
})

$ArrayHost = ''; $ArrayUser = ''; $RunId = ''; $Baseline = $null; $report = $null

try {
  # ---------------------------------------------------------------- preflight
  Section 'Preflight'
  $probe = Upload (Compose $Targets $null $null $null 'compose-probe') 'upload-probe'
  $ArrayHost = $probe.targets.array_host; $ArrayUser = $probe.targets.array_user
  if (-not $ArrayHost) { throw 'the base sheet has no array management IP on its Provisioning tab' }
  Note "Array $ArrayHost as $ArrayUser; vCenter $($probe.targets.vcenter_host); $($Rows.Count) Hosts-tab row(s)"
  try {
    Wsapi-Login $ArrayHost $ArrayUser $ArrayPw
    $Baseline = Wsapi-Counts 'before'
    Check 'WSAPI baseline read' $true (($Baseline.GetEnumerator() | ForEach-Object { "$($_.Key)=$($_.Value)" }) -join ' ')
    if (-not $Cpg) {
      $cpgs = Invoke-Json -Method 'GET' -Uri "$($script:Wsapi.Base)/cpgs" -Headers $script:Wsapi.Headers -Save 'wsapi-cpgs'
      $names = @($cpgs.Json.members | ForEach-Object { $_.name })
      $Cpg = @($names | Where-Object { $_ -like '*SSD*' })[0]
      if (-not $Cpg) { $Cpg = $names[0] }
    }
  } catch {
    Note "WSAPI not available ($($_.Exception.Message)) - the before/after proof and the plan's array reads are skipped."
    $Baseline = $null
  }
  if (-not $Cpg) { $Cpg = 'SSD_r6' }

  $Volumes = @(@{ name = "${Prefix}vol01"; size_gib = '1'; provisioning_type = 'tpvv'; cpg = $Cpg })
  $HostSetName = "${Prefix}hs"
  $Sheet = Compose $Targets $Volumes @(@{ name = $HostSetName; members = '' }) $HostRows 'compose-run'
  $token = (Upload $Sheet 'upload-run').token
  $RunId = (ApiOk 'POST' '/runs/from-sheet' @{ token = $token; mode = 'PROVISION_ONLY' } 'run').run.run_id
  Note "run $RunId"

  # ---------------------------------------------------------------- discovery
  Section 'Discover'
  $ev = Run-Step -RunId $RunId -Path '/discover' -Types @('discover.completed') -Save 'discover'
  $report = $ev.data.report
  Check 'discovery completed without an array error' (-not $report.error) $(if ($report.error) { $report.error } else { "$(@($report.hosts).Count) host(s), $(@($report.notes).Count) note(s)" })
  $notes = @($report.notes)
  Write-Evidence 'discovery-notes.txt' ($notes -join "`r`n") | Out-Null
  $byName = @{}
  foreach ($h in @($report.hosts)) { $byName[$h.name] = $h }

  foreach ($row in $Rows) {
    $h = $byName[$row.name]
    Check "R1: sheet host '$($row.name)' is listed" ($null -ne $h) $(if ($h) { "os=$($h.os) sources=$(@($h.sources) -join ',')" } else { 'missing from report.hosts' })
    if (-not $h) { continue }
    $ids = @($h.wwpns) + @($h.iqns)
    $detail = "lookup='$($h.lookup)' host_read='$($h.host_read)' serial='$($h.serial_number)' wwpns=$(@($h.wwpns) -join ',') iqns=$(@($h.iqns) -join ',')"
    switch ($row.expect) {
      'found' {
        $how = (-not $h.lookup) -or $h.lookup -like 'found*' -or $h.lookup -like 'read from*'
        Check "'$($row.name)' found, initiators filled" ($how -and $ids.Count -gt 0) $detail
      }
      'not_found' {
        Check "'$($row.name)' reported not found" ($h.lookup -like 'not found*' -and $ids.Count -eq 0) $detail
        Check "'$($row.name)' named in the discovery notes" (@($notes | Where-Object { $_ -like "Sheet host $($row.name):*" }).Count -eq 1) ''
      }
      'read_ok' {
        Check "'$($row.name)' read from the server itself" ($h.host_read -like 'read over*') $detail
        Check "'$($row.name)' reported a serial number" ([bool]$h.serial_number) $detail
        if ($row.os) { Check "'$($row.name)' OS is $($row.os)" ($h.os -eq $row.os) "os=$($h.os) os_text=$($h.os_text)" }
        Check "'$($row.name)' reported initiators" ($ids.Count -gt 0) $detail
        if ($h.multipath) { Note "$($row.name) multipath: $($h.multipath)" }
      }
      'read_fail' {
        Check "'$($row.name)' login failure reported on the row" ($h.host_read -and $h.host_read -notlike 'read over*') "host_read='$($h.host_read)'"
      }
      'blocked' {
        Check "'$($row.name)' read from the server (needed to compare)" ($h.host_read -like 'read over*') $detail
      }
    }
    if ($row.expect_serial) { Check "'$($row.name)' serial equals $($row.expect_serial)" ($h.serial_number -eq $row.expect_serial) "got '$($h.serial_number)'" }
    if ($row.expect_wwpns) {
      $want = @(Split-Ids $row.expect_wwpns | Sort-Object -Unique); $got = @(@($h.wwpns) | Sort-Object -Unique)
      Check "'$($row.name)' WWPNs equal the ground truth" (($want -join ',') -eq ($got -join ',')) "want=$($want -join ',') got=$($got -join ',')"
    }
  }

  $idents = @($report.host_identities)
  $withSerial = @($idents | Where-Object { $_.serial_number })
  Check 'R2: vCenter returned a serial number per ESXi host' ($idents.Count -gt 0 -and $withSerial.Count -eq $idents.Count) "$($withSerial.Count) of $($idents.Count) host(s): $(($idents | ForEach-Object { "$($_.host_name)=$($_.serial_number)" }) -join ', ')"
  $iscsiEsx = @($idents | Where-Object { @($_.iqns).Count -gt 0 })
  Note "ESXi hosts with an iSCSI adapter: $($iscsiEsx.Count) ($(($iscsiEsx | ForEach-Object { $_.host_name }) -join ', '))"
  $os = @{}; foreach ($h in @($report.hosts | Where-Object { $_.in_run })) { $os[$h.os] = 1 + [int]$os[$h.os] }
  Note ("hosts in this run by OS: " + (($os.GetEnumerator() | ForEach-Object { "$($_.Key)=$($_.Value)" }) -join ' '))

  # ---------------------------------------------------------------- zoning (switch reads only)
  if (-not $SkipZoning) {
    Section 'Zoning'
    $zev = Run-Step -RunId $RunId -Path '/zoning/plan' -Types @('zoning.plan') -Save 'zoning-plan'
    $zplan = $zev.data.plan
    if ($zplan.error) {
      Check 'zoning plan built from both switches' $false $zplan.error
    } else {
      $fabricWwpns = @{}
      foreach ($fab in @($zplan.fabrics)) { foreach ($e in @($fab.hosts)) { $fabricWwpns[$e.wwpn] = "$($fab.fabric):$($e.host_name)" } }
      $offline = (@($zplan.offline_hosts) -join ' ')
      foreach ($row in @($Rows | Where-Object { $_.expect -eq 'found' -or $_.expect -eq 'read_ok' })) {
        $h = $byName[$row.name]; if (-not $h -or @($h.wwpns).Count -eq 0) { continue }
        $placed = @(@($h.wwpns) | Where-Object { $fabricWwpns.ContainsKey($_) } | ForEach-Object { "$_ on $($fabricWwpns[$_])" })
        $unplaced = @(@($h.wwpns) | Where-Object { -not $fabricWwpns.ContainsKey($_) })
        $reported = @($unplaced | Where-Object { $offline -like "*$($row.name)*" -or $offline -like "*$(($_ -split '(..)' | Where-Object { $_ }) -join ':')*".ToLower() })
        Check "'$($row.name)' WWPNs reach the zoning plan" ($placed.Count + $reported.Count -eq @($h.wwpns).Count) "placed: $($placed -join '; ') | not on a fabric: $($unplaced -join ',')"
      }
    }
  }

  # ---------------------------------------------------------------- plan preview (reads only; never applied)
  Section 'Plan'
  $members = @($Rows | Where-Object { @('found', 'read_ok', 'blocked') -contains $_.expect } | ForEach-Object { $_.name })
  $builder = @{ host_sets = @(@{ name = $HostSetName; members = $members }); exports = @(); vvsets = @{} }
  ApiOk 'POST' "/runs/$RunId/storage/builder" $builder 'builder' | Out-Null
  $pev = Run-Step -RunId $RunId -Path '/storage/preview' -Types @('storage.previewed', 'storage.preview.failed') -Save 'preview'
  $plan = $pev.data.plan
  $blockers = @($plan.blockers); $pnotes = @($plan.notes)
  Write-Evidence 'plan-blockers-notes.txt' (($blockers + '---' + $pnotes) -join "`r`n") | Out-Null
  if ($plan.error) { Note "plan error (array reads): $($plan.error)" }
  foreach ($row in $Rows) {
    $mine = @($blockers | Where-Object { $_ -like "Host '$($row.name)': sheet*" })
    if ($row.expect -eq 'blocked') {
      Check "R6: typed WWPN/IQN on '$($row.name)' blocks the plan" ($mine.Count -ge 1) ($mine -join ' | ')
    } else {
      Check "no typed-vs-read blocker on '$($row.name)'" ($mine.Count -eq 0) ($mine -join ' | ')
    }
    if ($row.expect -eq 'not_found') {
      Check "plan notes '$($row.name)' as not planned" (@($pnotes | Where-Object { $_ -like "Host '$($row.name)' is on the sheet with no WWPN/IQN*" }).Count -eq 1) ''
    }
  }

  # ---------------------------------------------------------------- secrets (R7)
  Section 'Secrets'
  $detailText = (Api 'GET' "/runs/$RunId" $null 'run-detail').Text
  $eventsText = (Api 'GET' "/runs/$RunId/events" $null 'run-events').Text
  $leaks = @($Secrets | Where-Object { $detailText.Contains($_) -or $eventsText.Contains($_) })
  Check 'no password in GET /runs/{id} or any run event' ($leaks.Count -eq 0) "$($Secrets.Count) secret(s) searched, $($leaks.Count) found"
}
catch {
  Check "session aborted: $($_.Exception.Message)" $false ''
  Write-Evidence 'error.txt' ($_ | Out-String) | Out-Null
}

# ------------------------------------------------------------------ read-only proof
Section 'Read-only'
if ($Baseline) {
  try {
    $after = Wsapi-Counts 'after'
    $same = $true; foreach ($k in $Baseline.Keys) { if ($Baseline[$k] -ne $after[$k]) { $same = $false } }
    Check 'array unchanged (WSAPI counts before = after)' $same (($after.GetEnumerator() | ForEach-Object { "$($_.Key)=$($_.Value)/$($Baseline[$_.Key])" }) -join ' ')
  } catch { Check 'array unchanged (WSAPI counts before = after)' $false $_.Exception.Message }
} else {
  Note 'WSAPI was not available: the before/after proof was not taken (the runner still never calls apply).'
}
Wsapi-Logout
$ArrayPw = $null; $VcPw = $null; $SwPw = $null; $HostPw = $null; $Targets = $null; $HostRows = $null; $Secrets = $null

# ------------------------------------------------------------------ report
$fails = @($script:Results | Where-Object { $_.Verdict -eq 'FAIL' }).Count
$passes = @($script:Results | Where-Object { $_.Verdict -eq 'PASS' }).Count
$lines = @(
  "# SPEC-014 hosts session (read-only) - $stamp",
  "",
  "- App version: $Version",
  "- Runner: PowerShell $($PSVersionTable.PSVersion); TLS callback: $($script:TlsCallback)",
  "- Array: $ArrayHost ($ArrayUser); run: $RunId; hosts file: $(Split-Path $HostsFile -Leaf) ($($Rows.Count) rows)",
  "- Result: **$passes PASS, $fails FAIL**",
  "",
  "| Section | Verdict | Check | Detail |",
  "|---|---|---|---|"
)
foreach ($r in $script:Results) { $lines += "| $($r.Section) | $($r.Verdict) | $($r.What) | $(($r.Detail -replace '\|', '/') -replace "`r?`n", ' ') |" }
$lines += ""
$lines += "Nothing was written: no apply, no switch, no host write. Evidence: NN-<step>.json, wsapi-<what>-before/after.json."
$lines += ""
$lines += "## Still needs eyes - one screenshot each (open run $RunId in the browser)"
$lines += "1. Discovery: 'Hosts in this run - <OS>' tables, one per OS, with the Serial number column (SPEC-014 R3)."
$lines += "2. Discovery: a looked-up row showing 'sheet host found ...' and a read row showing 'read over SSH/WINRM ...'."
$lines += "3. Discovery: the not-found row in warning colour, and its sentence in the notes panel."
$lines += "4. Provision after Build plan: the typed-vs-read blocker sentence (R6)."
[System.IO.File]::WriteAllText((Join-Path $Out 'report.md'), ($lines -join "`r`n") + "`r`n", [System.Text.UTF8Encoding]::new($false))
Write-Host ""
Write-Host ("Hosts session complete: {0} PASS, {1} FAIL  ->  {2}\report.md" -f $passes, $fails, $Out) -ForegroundColor $(if ($fails -eq 0) { 'Green' } else { 'Red' })
if ($fails -gt 0) { exit 1 }
exit 0
