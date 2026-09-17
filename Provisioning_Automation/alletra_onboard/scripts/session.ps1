<#
.SYNOPSIS
  SPEC-006: the live provisioning session, run by a script instead of a person.

.DESCRIPTION
  Drives the running Alletra Onboard app over its own HTTP API (the same calls the UI makes), checks
  the array over read-only WSAPI, runs six scenarios against a CLEAN array and asserts every outcome:

    1 Create      two volumes in a VV set, one host set, one set export      -> everything created
    2 Rerun       the same sheet again                                        -> everything exists (P-21)
    3 Conflict    one volume at a different size                              -> blocker, apply refused
    4 Blank       host set with no members, nothing composed                  -> blocker names the set (SPEC-005)
    5 Documents   verify + as-built on run 1                                  -> no mismatch, docx names the run
    6 Cleanup     run 1's own removal set (SPEC-007) pasted over SSH          -> array back to baseline

  From rc.24 the scenarios also assert the rc.19-rc.23 changes that the API exposes: one array
  credential per run (SPEC-008), Discovery identity/in-run flags and the names check (SPEC-009), the
  FOS-ordered command set and alias suggestion (SPEC-010, one read-only login per switch), verify match
  rules and status detail rows (SPEC-011), result identifiers and the as-built page flow (SPEC-012).
  UI-only changes cannot be asserted here; the report ends with the screenshots still needed.

  Everything it touches is named zz_s6_*. It refuses to start if the array already has such objects.
  Writes session-<stamp>\report.md and keeps every response, every WSAPI read, the docx and the SSH
  transcript in that folder. Exit code 1 on any FAIL. Send the folder back.

  The only writes to the array are the app's own apply (scenario 1) and the app's own removal lines
  (scenario 6). Nothing is written to a switch. The script never issues a CLI command it did not
  receive from the tool.

.PARAMETER BaseSheet   The operator's working Initialisation_sheet.xlsx (credentials, init fields,
                       switch IPs come from it; its row tables are REPLACED per scenario, in a copy).
.PARAMETER Api         The app's API (default http://127.0.0.1:8765 - start AlletraOnboard.exe first).
.PARAMETER Cpg         CPG for the two volumes (default: the first CPG the array reports; 'SSD' preferred).
.PARAMETER OutRoot     Where the session-<stamp> folder goes (default: next to this script).
.PARAMETER SkipCleanup Leave zz_s6_* on the array (to look at it in the UI); the report says so.

.EXAMPLE
  .\session.ps1 -BaseSheet C:\Users\me\Desktop\Initialisation_sheet.xlsx
#>
[CmdletBinding()]
param(
  [Parameter(Mandatory = $true)][string]$BaseSheet,
  [string]$Api = 'http://127.0.0.1:8765',
  [string]$Cpg = '',
  [string]$OutRoot = '',
  [switch]$SkipCleanup
)
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.IO.Compression.FileSystem
if (-not $OutRoot) {
  # $PSScriptRoot is empty in a param() default under `powershell -File` on 5.1 (session.cmd, 2026-09-15).
  $OutRoot = if ($PSScriptRoot) { $PSScriptRoot } else { Split-Path -Parent $MyInvocation.MyCommand.Path }
  if (-not $OutRoot) { $OutRoot = (Get-Location).Path }
}

$Prefix = 'zz_s6_'
$Vol1 = "${Prefix}vol01"; $Vol2 = "${Prefix}vol02"; $Vol3 = "${Prefix}vol03"; $VvSet = "${Prefix}vvs"; $HostSet = "${Prefix}hs"
$PollSeconds = 1; $CeilingSeconds = 300

# ------------------------------------------------------------------ evidence folder + report

$stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$Out = Join-Path $OutRoot "session-$stamp"
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
  return $ok
}
function Section([string]$title) { $script:Section = $title; Write-Host ""; Write-Host "== $title" -ForegroundColor Cyan }
function Note([string]$text) { Write-Host "  $text" -ForegroundColor DarkGray }

# ------------------------------------------------------------------ HTTP (the API and WSAPI are both on-site: no proxy)

$script:TlsCallback = 'not needed (PowerShell 6+)'
if ($PSVersionTable.PSVersion.Major -lt 6) {
  [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.SecurityProtocolType]::Tls12
  # A script-block callback ({ $true }) runs only on the FIRST handshake; later handshakes happen on
  # a .NET thread with no runspace and fail with "An unexpected error occurred on a send" (S-12 FAIL 4,
  # and every read on 2026-09-15 once keep-alive was off). The callback must be compiled code.
  # -IgnoreWarnings, no pragma: 5.1's csc treats warnings as errors and rejects non-numeric warning ids
  # (probe 2026-09-15: "Warning as Error: Invalid number" - rc.17/rc.18 silently fell back).
  try {
    Add-Type -IgnoreWarnings -TypeDefinition @'
using System.Net;
public static class SessionTrustArrayCert {
  public static void Enable() { ServicePointManager.ServerCertificateValidationCallback = delegate { return true; }; }
}
'@ -ErrorAction Stop
    [SessionTrustArrayCert]::Enable()
    $script:TlsCallback = 'compiled'
  } catch {
    $script:TlsCallback = "SCRIPT-BLOCK FALLBACK - Add-Type failed: $($_.Exception.Message)"
    Write-Warning "Add-Type failed ($($_.Exception.Message)); falling back to a script-block callback (WSAPI may drop on any new TLS connection)"
    [System.Net.ServicePointManager]::ServerCertificateValidationCallback = { $true }
  }
  [System.Net.WebRequest]::DefaultWebProxy = $null
}
$Common = @{ TimeoutSec = 120; UseBasicParsing = $true }
if ($PSVersionTable.PSVersion.Major -ge 6) { $Common['SkipCertificateCheck'] = $true; $Common['NoProxy'] = $true }

function Invoke-Json {
  # Returns @{ Status; Text; Json }; never throws on 4xx/5xx (scenario 3 EXPECTS a 409).
  param([string]$Method, [string]$Uri, $Body = $null, [hashtable]$Headers = @{}, [string]$Save = '')
  $req = @{ Method = $Method; Uri = $Uri; Headers = $Headers }
  if ($null -ne $Body) { $req['ContentType'] = 'application/json'; $req['Body'] = ($Body | ConvertTo-Json -Depth 12 -Compress) }
  try {
    $resp = Invoke-WebRequest @Common @req
    $status = [int]$resp.StatusCode
    # 5.1 decodes a charset-less JSON body as Latin-1; take the bytes and decode UTF-8 ourselves.
    $text = if ($resp.RawContentStream) { [System.Text.Encoding]::UTF8.GetString($resp.RawContentStream.ToArray()) } else { $resp.Content }
  } catch [System.Net.WebException] {
    $r = $_.Exception.Response
    if ($null -eq $r) { throw }
    $status = [int]$r.StatusCode
    # 5.1 puts the body of a 4xx in ErrorDetails; the response stream is already at its end by the
    # time the catch runs (S-13 and S-14 both recorded the conflict refusal as 'HTTP 409:  ').
    $text = $_.ErrorDetails.Message
    if (-not $text) { try { $s = $r.GetResponseStream(); if ($s.CanSeek) { $s.Position = 0 }; $reader = New-Object System.IO.StreamReader($s, [System.Text.Encoding]::UTF8); $text = $reader.ReadToEnd(); $reader.Close() } catch { $text = '' } }
  } catch {
    if ($_.Exception.Response) {
      $status = [int]$_.Exception.Response.StatusCode; $text = $_.ErrorDetails.Message
    } else { throw }
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

# ------------------------------------------------------------------ R5: wait by state, then read the event

function Wait-Step {
  # Polls until the newest event appended AFTER index $Since is one of $Types (or step.crashed), up to
  # the ceiling. The run STATUS is not the signal: verify and as-built never change it by design
  # (S-12 gave up after 5 s on a verify that needed 40). Timeout or a crash is a FAIL (caller decides).
  param([string]$RunId, [string[]]$Types, [int]$Since, [string]$Save)
  $deadline = (Get-Date).AddSeconds($CeilingSeconds)
  $status = ''
  $found = $null
  $Types = @($Types) + 'step.crashed'
  while ((Get-Date) -lt $deadline) {
    Start-Sleep -Seconds $PollSeconds
    $events = @((Api 'GET' "/runs/$RunId/events").Json.events)
    for ($i = $events.Count - 1; $i -ge $Since; $i--) {
      if ($Types -contains $events[$i].event_type) { $found = $events[$i]; break }
    }
    if ($found) { break }
  }
  $status = (Api 'GET' "/runs/$RunId").Json.run.status
  $all = @((Api 'GET' "/runs/$RunId/events" -Save "$Save-events").Json.events)
  if (-not $found) {
    $last = if ($all.Count -gt 0) { $all[$all.Count - 1] } else { $null }
    throw "waited ${CeilingSeconds}s for $($Types -join '|') - run status '$status', last event $(if ($last) { "$($last.event_type): $($last.message)" } else { 'none' })"
  }
  Write-Evidence "$Save.json" ($found | ConvertTo-Json -Depth 20) | Out-Null
  if ($found.event_type -eq 'step.crashed') { throw "step crashed: $($found.message)" }
  return $found
}
function Event-Count([string]$RunId) { return @((Api 'GET' "/runs/$RunId/events").Json.events).Count }
function Run-Step {
  # POST a step, then wait for its completion event. Returns the event's `data`.
  param([string]$RunId, [string]$Path, $Body, [string[]]$Types, [string]$Save)
  $since = Event-Count $RunId
  $r = Api 'POST' "/runs/$RunId$Path" $Body "$Save-post"
  if ($r.Status -lt 200 -or $r.Status -ge 300) { throw "POST $Path -> HTTP $($r.Status): $($r.Text)" }
  $ev = Wait-Step -RunId $RunId -Types $Types -Since $since -Save $Save
  return $ev
}

# ------------------------------------------------------------------ WSAPI, read-only

$script:Wsapi = $null
$script:WsapiCreds = $null
function Wsapi-Login([string]$ArrayHost, [string]$User, [string]$Password) {
  $base = "https://$ArrayHost/api/v1"
  $login = Invoke-Json -Method 'POST' -Uri "$base/credentials" -Body @{ user = $User; password = $Password }
  if ($login.Status -ne 201 -and $login.Status -ne 200) { throw "WSAPI login failed: HTTP $($login.Status) $($login.Text)" }
  $script:Wsapi = @{ Base = $base; Headers = @{ 'X-HP3PAR-WSAPI-SessionKey' = $login.Json.key } }
  $script:WsapiCreds = @{ ArrayHost = $ArrayHost; User = $User; Password = $Password }
}
function Wsapi-Logout() {
  if ($script:Wsapi) { try { Invoke-Json -Method 'DELETE' -Uri "$($script:Wsapi.Base)/credentials/$($script:Wsapi.Headers['X-HP3PAR-WSAPI-SessionKey'])" -Headers $script:Wsapi.Headers | Out-Null } catch {} }
}
function Wsapi-Get([string]$name) {
  # One retry: a dropped connection is retried as-is; 401/403 (session expired) re-logs in first.
  for ($attempt = 1; $attempt -le 2; $attempt++) {
    try {
      $r = Invoke-Json -Method 'GET' -Uri "$($script:Wsapi.Base)/$name" -Headers $script:Wsapi.Headers
      if ($r.Status -eq 200) { return $r }
      if (($r.Status -eq 401 -or $r.Status -eq 403) -and $attempt -eq 1) { Wsapi-Login $script:WsapiCreds.ArrayHost $script:WsapiCreds.User $script:WsapiCreds.Password; continue }
      throw "WSAPI GET $name -> HTTP $($r.Status)"
    } catch {
      if ($attempt -eq 2) { throw }
      Note "WSAPI GET $name failed once ($($_.Exception.Message)); retrying"
      Start-Sleep -Seconds 2
    }
  }
}
function Wsapi-Read([string]$when) {
  # The five lists the plan compares against, each saved verbatim as wsapi-<what>-<when>.json.
  $snap = @{}
  foreach ($name in 'hosts', 'hostsets', 'volumes', 'volumesets', 'vluns') {
    $r = Wsapi-Get $name
    Write-Evidence "wsapi-$name-$when.json" $r.Text | Out-Null
    $snap[$name] = @($r.Json.members)
  }
  return $snap
}
function Snap-Counts($snap) {
  # vluns counted as TEMPLATES: active per-path rows come and go with host logins.
  return [ordered]@{ hosts = $snap.hosts.Count; hostsets = $snap.hostsets.Count; volumes = $snap.volumes.Count; volumesets = $snap.volumesets.Count; vluns = (Snap-Templates $snap).Count }
}
function Snap-Prefixed($snap) {
  $names = @()
  foreach ($h in $snap.hosts) { if ($h.name -like "$Prefix*") { $names += "host $($h.name)" } }
  foreach ($s in $snap.hostsets) { if ($s.name -like "$Prefix*") { $names += "hostset $($s.name)" } }
  foreach ($v in $snap.volumes) { if ($v.name -like "$Prefix*") { $names += "volume $($v.name)" } }
  foreach ($s in $snap.volumesets) { if ($s.name -like "$Prefix*") { $names += "vvset $($s.name)" } }
  foreach ($t in @($snap.vluns | Where-Object { $_.active -ne $true })) { if ($t.volumeName -like "$Prefix*") { $names += "vlun $($t.volumeName) LUN $($t.lun) -> $($t.hostname)" } }
  return ($names | Sort-Object -Unique)
}
function Snap-Templates($snap) {
  # Mirrors the app's parse_vlun_templates (pinned to rack13_wsapi/vluns.json): a template is a record
  # with active != true, target exactly as written (`set:<hostset>` or a bare host). Active rows are
  # per-path and name the member host, so they are not templates.
  return @($snap.vluns | Where-Object { $_.active -ne $true } | ForEach-Object { "$($_.volumeName)|$($_.lun)|$($_.hostname)" } | Sort-Object -Unique)
}

# ------------------------------------------------------------------ sheets from JSON (R3)

function Read-SheetBytes([string]$path) {
  # FileShare ReadWrite: the operator usually has the sheet open in Excel (2026-09-15, first rc.16 attempt).
  $fs = [System.IO.File]::Open((Resolve-Path $path).Path, [System.IO.FileMode]::Open, [System.IO.FileAccess]::Read, [System.IO.FileShare]::ReadWrite)
  try { $ms = New-Object System.IO.MemoryStream; $fs.CopyTo($ms); return $ms.ToArray() } finally { $fs.Dispose() }
}
$BaseB64 = [Convert]::ToBase64String((Read-SheetBytes $BaseSheet))
function Compose($targets, $volumes, $hostsets, [string]$Save) {
  $body = @{ base_b64 = $BaseB64; targets = $targets }
  if ($null -ne $volumes) { $body['volumes'] = $volumes }
  if ($null -ne $hostsets) { $body['hostsets'] = $hostsets }
  $r = Api 'POST' '/init-sheet/compose' $body
  if ($r.Status -ne 200) { throw "compose -> HTTP $($r.Status): $($r.Text)" }
  Write-Evidence "$Save.txt" "composed sheet: $($r.Json.content_b64.Length) base64 chars; volumes=$($volumes | ConvertTo-Json -Compress) hostsets=$($hostsets | ConvertTo-Json -Compress)" | Out-Null
  return $r.Json.content_b64
}
function Upload([string]$b64, [string]$Save) {
  $r = ApiOk 'POST' '/init-sheet/upload' @{ content_b64 = $b64 }
  # Evidence goes back to the developer: keep the response, not the subscription key it echoes for the UI.
  if ($r.work_item -and $r.work_item.PSObject.Properties['subscription_key']) { $r.work_item.subscription_key = '<redacted>' }
  Write-Evidence "$Save.json" ($r | ConvertTo-Json -Depth 12) | Out-Null
  return $r
}
function New-Run([string]$token, [string]$Save) {
  $r = ApiOk 'POST' '/runs/from-sheet' @{ token = $token; mode = 'PROVISION_ONLY' } $Save
  return $r.run.run_id
}

# ------------------------------------------------------------------ prompts (R1)

Write-Host "SPEC-006 session runner - evidence folder: $Out"
try { $health = Api 'GET' '/health' $null 'health' }
catch { $health = @{ Status = 0; Text = $_.Exception.Message } }   # connection refused: no HTTP response to catch inside Invoke-Json
if ($health.Status -ne 200) {
  Write-Host "The app is not answering at $Api ($($health.Text))." -ForegroundColor Red
  Write-Host "Start AlletraOnboard.exe (or start.cmd) in this folder, wait for the browser to open, then run this again." -ForegroundColor Red
  exit 1
}
$Version = $health.Json.version
Write-Host "App version: $Version"

function Read-Secret([string]$prompt) {
  $s = Read-Host -Prompt $prompt -AsSecureString
  return [System.Net.NetworkCredential]::new('', $s).Password
}
$ArrayPw = Read-Secret 'Array admin password (3paradm)'
$VcPw = Read-Secret 'vCenter password'
$SwPw = Read-Secret 'Switch password (both fabrics)'
$Targets = @{ prov_array_password = $ArrayPw; prov_vcenter_password = $VcPw; prov_sw1_password = $SwPw; prov_sw2_password = $SwPw }

$Fail = $false
$Run1 = $null; $Run1Removals = @(); $Baseline = $null; $ArrayHost = ''; $ArrayUser = ''

try {
  # ---------------------------------------------------------------- R2: the array must be clean
  Section 'Preflight'
  $probe = Upload (Compose $Targets $null $null 'compose-probe') 'upload-probe'
  $ArrayHost = $probe.targets.array_host; $ArrayUser = $probe.targets.array_user
  if (-not $ArrayHost) { throw "the base sheet has no array management IP on its Provisioning tab" }
  Note "Array $ArrayHost as $ArrayUser (from the sheet)"
  Wsapi-Login $ArrayHost $ArrayUser $ArrayPw
  $Baseline = Wsapi-Read 'baseline'
  $dirty = Snap-Prefixed $Baseline
  if ($dirty.Count -gt 0) {
    Write-Host "The array already has $Prefix objects. Remove them first (paste over SSH), then rerun:" -ForegroundColor Red
    $seenT = @{}
    foreach ($t in @($Baseline.vluns | Where-Object { $_.active -ne $true })) {
      $line = "  removevlun -f $($t.volumeName) $($t.lun) $($t.hostname)"
      if ($t.volumeName -like "$Prefix*" -and -not $seenT[$line]) { $seenT[$line] = 1; Write-Host $line }
    }
    foreach ($s in $Baseline.volumesets) { if ($s.name -like "$Prefix*") { Write-Host "  removevvset -f $($s.name)" } }
    foreach ($v in $Baseline.volumes) { if ($v.name -like "$Prefix*") { Write-Host "  removevv -f $($v.name)" } }
    foreach ($s in $Baseline.hostsets) { if ($s.name -like "$Prefix*") { Write-Host "  removehostset -f $($s.name)" } }
    foreach ($h in $Baseline.hosts) { if ($h.name -like "$Prefix*") { Write-Host "  removehost $($h.name)" } }
    throw "dirty array: $($dirty -join ', ')"
  }
  $counts = Snap-Counts $Baseline
  Check "array has no $Prefix objects" $true (($counts.GetEnumerator() | ForEach-Object { "$($_.Key)=$($_.Value)" }) -join ' ') | Out-Null
  if (-not $Cpg) {
    $cpgs = Invoke-Json -Method 'GET' -Uri "$($script:Wsapi.Base)/cpgs" -Headers $script:Wsapi.Headers -Save 'wsapi-cpgs'
    $names = @($cpgs.Json.members | ForEach-Object { $_.name })
    $Cpg = @($names | Where-Object { $_ -like '*SSD*' })[0]
    if (-not $Cpg) { $Cpg = $names[0] }
    if (-not $Cpg) { throw 'the array reports no CPG' }
  }
  Note "CPG for the volumes: $Cpg"

  $Volumes = @(
    @{ name = $Vol1; size_gib = '1'; provisioning_type = 'tpvv'; cpg = $Cpg; vvset = $VvSet },
    @{ name = $Vol2; size_gib = '1'; provisioning_type = 'reduce'; cpg = $Cpg; vvset = $VvSet }
  )
  $HostSets = @(@{ name = $HostSet; members = '' })
  $SheetA = Compose $Targets $Volumes $HostSets 'compose-A'

  # ---------------------------------------------------------------- the per-run front half (discover, zoning check, objects)
  function Start-Provisioning([string]$label, [string]$sheet) {
    $token = (Upload $sheet "$label-upload").token
    $runId = New-Run $token "$label-run"
    Note "run $runId"
    $disc = Run-Step -RunId $runId -Path '/discover' -Types @('discover.completed') -Save "$label-discover"
    if ($disc.data.report.error) { throw "discovery failed: $($disc.data.report.error)" }
    $zon = Run-Step -RunId $runId -Path '/zoning/preview' -Types @('zoning.proper', 'zoning.previewed') -Save "$label-zoning"
    $objects = ApiOk 'GET' "/runs/$runId/storage/objects" $null "$label-objects"
    return @{ RunId = $runId; Discovery = $disc; Zoning = $zon; Objects = $objects }
  }
  function Pick-Host($front) {
    # R4 #1: the base sheet's first vCenter host that Discovery reports logged in on both fabrics.
    $zoned = @($front.Zoning.data.report.zoned_hosts)
    $cands = @($front.Objects.discovered_hosts | Where-Object { $_.source -eq 'vcenter' -and $_.status -like '*both fabrics*' })
    $pick = @($cands | Where-Object { $zoned -contains $_.name })[0]
    if (-not $pick) { $pick = $cands[0] }
    return $pick
  }
  function Compose-And-Preview($front, [string]$hostName, [string]$label) {
    $builder = @{
      host_sets = @(@{ name = $HostSet; members = @($hostName) })
      exports   = @(@{ source_kind = 'vvset'; source_name = $VvSet; target_kind = 'hostset'; target_name = $HostSet; lun = $null })
      vvsets    = @{ $VvSet = @($Vol1, $Vol2) }
    }
    ApiOk 'POST' "/runs/$($front.RunId)/storage/builder" $builder "$label-builder" | Out-Null
    $ev = Run-Step -RunId $front.RunId -Path '/storage/preview' -Types @('storage.previewed', 'storage.preview.failed') -Save "$label-preview"
    return $ev.data.plan
  }
  function Plan-Rows($plan, [string]$state) { return @($plan.actions | Where-Object { $_.state -eq $state }) }
  function Outcomes($result, [string]$status) { return @($result.outcomes | Where-Object { $_.status -eq $status }) }

  # ---------------------------------------------------------------- 1 Create
  Section '1 Create'
  $f1 = Start-Provisioning 'run1' $SheetA
  $Run1 = $f1.RunId
  $bothFabrics = @($f1.Objects.discovered_hosts | Where-Object { $_.status -like '*both fabrics*' })
  Check 'discovery reports >= 1 host on both fabrics' ($bothFabrics.Count -ge 1) (($bothFabrics | ForEach-Object { "$($_.name) [$($_.source)]" }) -join ', ') | Out-Null
  $pick = Pick-Host $f1
  if (-not $pick) { throw 'no vCenter host is logged in on both fabrics - scenario 1 needs one (as .136 was); nothing was created' }
  $HostName = $pick.name
  Note "host for ${HostSet}: $HostName ($($pick.status))"
  Check "zoning check puts $HostName in zoned_hosts" (@($f1.Zoning.data.report.zoned_hosts) -contains $HostName) ("zoned: " + (@($f1.Zoning.data.report.zoned_hosts) -join ', ')) | Out-Null

  # ---- rc.20 SPEC-009: Discovery says whose hosts these are (R1 identity, R2 in_run, R3 ports, R5 names check)
  $dhosts = @($f1.Discovery.data.report.hosts)
  $noFlags = @($dhosts | Where-Object { -not $_.PSObject.Properties['identified'] -or -not $_.PSObject.Properties['in_run'] })
  Check 'discovery: every host carries identified + in_run (SPEC-009)' ($dhosts.Count -gt 0 -and $noFlags.Count -eq 0) "hosts=$($dhosts.Count)" | Out-Null
  $me = @($dhosts | Where-Object { $_.name -eq $HostName })[0]
  Check "discovery: $HostName is in this run and identified" ($me -and $me.in_run -eq $true -and $me.identified -eq $true) $(if ($me) { "in_run=$($me.in_run) identified=$($me.identified) sources=$(@($me.sources) -join ',')" } else { 'not in report.hosts' }) | Out-Null
  $portKeys = @(); if ($me -and $me.ports) { $portKeys = @($me.ports.PSObject.Properties | Where-Object { @($_.Value).Count -gt 0 }) }
  Check "discovery: $HostName initiators carry their array ports" ($portKeys.Count -ge 1) (($portKeys | ForEach-Object { "$($_.Name) -> $(@($_.Value) -join ',')" }) -join '; ') | Out-Null
  $unid = @($dhosts | Where-Object { $_.identified -eq $false })
  $unidWrong = @($unid | Where-Object { -not ((@($_.wwpns) + @($_.iqns)) -contains $_.name) })
  Check 'discovery: unidentified only when the name is the initiator id itself (D-2)' ($unidWrong.Count -eq 0) (($unid | ForEach-Object { $_.name }) -join ', ') | Out-Null
  Note "hosts in this run: $(@($dhosts | Where-Object { $_.in_run -eq $true }).Count); other hosts on this array: $(@($dhosts | Where-Object { $_.in_run -ne $true }).Count)"
  $pre = Api 'GET' "/runs/$Run1/storage/preflight" $null 'run1-preflight'
  $namesCheck = $null; if ($pre.Status -eq 200) { $namesCheck = @($pre.Json.checks | Where-Object { $_.key -eq 'names' })[0] }
  Check 'preflight: names check counts objects by kind (D-4)' ($namesCheck -and $namesCheck.detail -match '^4 object name\(s\) free: 2 volumes, 1 VV set, 1 host set\.') $(if ($namesCheck) { "$($namesCheck.status): $($namesCheck.detail)" } else { "HTTP $($pre.Status)" }) | Out-Null

  # ---- rc.21 SPEC-010: the command set reads in FOS order (R1) and a bad alias gets a suggestion (R3).
  # The plan step logs into both switches READ-ONLY (as the Zoning step does); render is pure computation
  # and is not recorded on the run (no run_id), so the as-built below is what the scenarios produce.
  $zplan = $null
  try {
    $zev = Run-Step -RunId $Run1 -Path '/zoning/plan' -Types @('zoning.plan') -Save 'run1-zoning-plan'
    $zplan = $zev.data.plan
    if ($zplan.error) { Check 'zoning plan built from both switches' $false $zplan.error | Out-Null; $zplan = $null }
  } catch { Check 'zoning plan built from both switches' $false $_.Exception.Message | Out-Null }
  if ($zplan) {
    $chosen = @(); $aliases = @{}
    foreach ($fab in @($zplan.fabrics)) {
      $zonedKeys = @($fab.already_zoned | ForEach-Object { "$($_[0])|$($_[1])" })
      $pair = @($fab.pairs | Where-Object { $zonedKeys -notcontains "$($_[0])|$($_[1])" })[0]
      if (-not $pair) { continue }
      $chosen += , @($pair[0], $pair[1])
      foreach ($w in (@($fab.hosts) + @($fab.array_ports))) {
        if ($w.wwpn -eq $pair[0] -or $w.wwpn -eq $pair[1]) {
          if (@($w.existing_aliases).Count -gt 0) { $aliases[$w.wwpn] = @($w.existing_aliases)[0] }
          elseif ($w.proposed_alias) { $aliases[$w.wwpn] = $w.proposed_alias }
          else { $aliases[$w.wwpn] = "zz_s6_$($w.wwpn)" }
        }
      }
    }
    if ($chosen.Count -eq 0) {
      Note 'zoning render: every host-array pair on both fabrics is already zoned - nothing to render here (SPEC-010 R1/R3 need a screenshot instead)'
    } else {
      $render = Api 'POST' '/zoning/render' @{ plan = $zplan; aliases = $aliases; selected_pairs = $chosen } 'run1-zoning-render'
      $cmdSets = @()
      if ($render.Status -eq 200) { foreach ($p in $render.Json.commands.PSObject.Properties) { if (@($p.Value).Count -gt 0) { $cmdSets += , @($p.Value) } } }
      $orderOk = $cmdSets.Count -gt 0
      foreach ($c in $cmdSets) { if ($c[0] -ne 'cfgtransshow' -or $c[-2] -ne 'cfgsave' -or $c[-1] -notlike 'cfgenable *') { $orderOk = $false } }
      Check 'zoning render: cfgtransshow first, cfgsave + cfgenable last (Z-4)' $orderOk $(if ($render.Status -ne 200) { "HTTP $($render.Status): $($render.Text)" } else { ($cmdSets | ForEach-Object { "$($_[0]) ... $($_[-2]); $($_[-1])" }) -join ' | ' }) | Out-Null
      $badAliases = $aliases.Clone(); $badAliases[$chosen[0][0]] = 'bad name.1'
      $render2 = Api 'POST' '/zoning/render' @{ plan = $zplan; aliases = $badAliases; selected_pairs = $chosen } 'run1-zoning-render-badalias'
      $skippedAll = @(); if ($render2.Status -eq 200) { foreach ($p in $render2.Json.skipped.PSObject.Properties) { $skippedAll += @($p.Value) } }
      Check "zoning render: a rejected alias offers a corrected one (Z-3)" (@($skippedAll | Where-Object { $_ -like "*try 'bad_name_1'*" }).Count -ge 1) ($skippedAll -join ' | ') | Out-Null
    }
  }

  $plan1 = Compose-And-Preview $f1 $HostName 'run1'
  $mine = @($plan1.actions | Where-Object { $_.name -like "$Prefix*" -or $_.kind -eq 'vlun' })
  $hostRow = @($plan1.actions | Where-Object { $_.kind -eq 'host' -and $_.name -eq $HostName })[0]
  Check "plan: every $Prefix row and the export are 'create'" (($mine.Count -ge 5) -and (@($mine | Where-Object { $_.state -ne 'create' }).Count -eq 0)) (($mine | ForEach-Object { "$($_.kind) $($_.name)=$($_.state)" }) -join '; ') | Out-Null
  # The host row's state follows the array, not an assumption: after S-10's cleanup .136 did not exist
  # and the plan rightly said 'create' (S-12 FAIL 1 was the runner's, not the app's).
  $hostPreexists = @($Baseline.hosts | Where-Object { $_.name -eq $HostName }).Count -gt 0
  $wantHost = if ($hostPreexists) { 'exists' } else { 'create' }
  Check "plan: host row $HostName is '$wantHost' (array $(if ($hostPreexists) { 'has' } else { 'lacks' }) it)" ($hostRow -and $hostRow.state -eq $wantHost) $(if ($hostRow) { "$($hostRow.state) $($hostRow.reason)" } else { 'no host row' }) | Out-Null
  Check 'plan: 0 blockers' (@($plan1.blockers).Count -eq 0) (@($plan1.blockers) -join '; ') | Out-Null

  $before1 = Snap-Templates (Wsapi-Read 'before-apply-1')
  $ev = Run-Step -RunId $Run1 -Path '/storage/apply' -Types @('storage.applied', 'storage.apply.failed') -Save 'run1-apply'
  $res1 = $ev.data.result
  $plannedCreate = (Plan-Rows $plan1 'create').Count; $plannedExists = (Plan-Rows $plan1 'exists').Count
  Check 'apply: no outcome failed' ((Outcomes $res1 'failed').Count -eq 0 -and -not $res1.error) (($res1.outcomes | Where-Object { $_.status -eq 'failed' } | ForEach-Object { "$($_.kind) $($_.name): $($_.detail)" }) -join '; ') | Out-Null
  Check "apply: created == planned create ($plannedCreate)" ((Outcomes $res1 'created').Count -eq $plannedCreate) ("created=" + (Outcomes $res1 'created').Count) | Out-Null
  Check "apply: exists == planned exists ($plannedExists)" ((Outcomes $res1 'exists').Count -eq $plannedExists) ("exists=" + (Outcomes $res1 'exists').Count) | Out-Null
  $vlunOut = @($res1.outcomes | Where-Object { $_.kind -eq 'vlun' })[0]
  # Read-back is "LUN 0, LUN 1 -> set:..." for a clean create; "LUN 0/3" is the P-21 duplicate form.
  $lunTokens = if ($vlunOut) { @([regex]::Matches($vlunOut.detail, 'LUN \d+') | ForEach-Object { $_.Value }) } else { @() }
  Check 'apply: export read-back names two LUNs, no duplicate' ($lunTokens.Count -eq 2 -and $vlunOut.detail -notmatch 'LUN \d+/') $(if ($vlunOut) { $vlunOut.detail } else { 'no vlun outcome' }) | Out-Null
  # ---- rc.23 SPEC-012 R1 (P-8): result rows carry the array's identifiers (\u00b7 is the middle dot the server joins with)
  $oh = @($res1.outcomes | Where-Object { $_.kind -eq 'host' -and $_.name -eq $HostName })[0]
  Check 'result: host row names id, persona, WWN count (P-8)' ($oh -and $oh.detail -match '^id \d+ \u00b7 persona \S+ \u00b7 \d+ WWNs?$') $(if ($oh) { $oh.detail } else { 'no host outcome' }) | Out-Null
  $ov = @($res1.outcomes | Where-Object { $_.kind -eq 'volume' -and $_.name -eq $Vol1 })[0]
  Check "result: $Vol1 row names id, WWN, size, type, CPG" ($ov -and $ov.detail -match ('^id \d+ \u00b7 WWN [0-9A-F]{32} \u00b7 1024 MiB tpvv on ' + [regex]::Escape($Cpg) + '$')) $(if ($ov) { $ov.detail } else { 'no volume outcome' }) | Out-Null
  $ohs = @($res1.outcomes | Where-Object { $_.kind -eq 'hostset' })[0]
  Check 'result: host set row lists its member' ($ohs -and $ohs.detail -eq "1 member: $HostName") $(if ($ohs) { $ohs.detail } else { '' }) | Out-Null
  $ovs = @($res1.outcomes | Where-Object { $_.kind -eq 'vvset' })[0]
  Check 'result: VV set row lists its volumes' ($ovs -and $ovs.detail -eq "2 volumes: $Vol1, $Vol2") $(if ($ovs) { $ovs.detail } else { '' }) | Out-Null

  $after1Snap = Wsapi-Read 'after-apply-1'
  $after1 = Snap-Templates $after1Snap
  $new = @($after1 | Where-Object { $before1 -notcontains $_ })
  Check 'WSAPI: exactly two new VLUN templates' ($new.Count -eq 2) ($new -join '; ') | Out-Null
  Check "WSAPI: both new templates target set:$HostSet" (@($new | Where-Object { $_ -notlike "*|set:$HostSet" }).Count -eq 0) ($new -join '; ') | Out-Null

  $ev = Run-Step -RunId $Run1 -Path '/storage/verify-paths' -Types @('storage.paths.verified', 'storage.paths.failed') -Save 'run1-paths'
  $ph = @($ev.data.verification.hosts | Where-Object { $_.host -eq $HostName })[0]
  Check "paths: $HostName is 'live'" ($ph -and $ph.verdict -eq 'live') $(if ($ph) { $ph.detail } else { 'host not in report' }) | Out-Null
  Check 'paths: lun_count == 2' ($ph -and $ph.lun_count -eq 2) $(if ($ph) { "lun_count=$($ph.lun_count)" } else { '' }) | Out-Null
  Check 'paths: paths_per_lun >= 2' ($ph -and $ph.paths_per_lun -ge 2) $(if ($ph) { "paths_per_lun=$($ph.paths_per_lun)" } else { '' }) | Out-Null

  $Run1Removals = @($res1.removals)
  $order = @{ vlun = 0; vvset = 1; volume = 2; hostset = 3; host = 4 }
  $kinds = @($Run1Removals | ForEach-Object { $order[$_.kind] })
  $sorted = $true; for ($i = 1; $i -lt $kinds.Count; $i++) { if ($kinds[$i] -lt $kinds[$i - 1]) { $sorted = $false } }
  $wantLines = 6 + $(if ($hostPreexists) { 0 } else { 1 })
  Check "removal set: $wantLines lines in dependency order" ($Run1Removals.Count -eq $wantLines -and $sorted) (($Run1Removals | ForEach-Object { $_.command }) -join ' ; ') | Out-Null
  # Pasted in dependency order whatever the API sent (S-12 pasted host-before-set from an unsorted list).
  $Run1Removals = @($Run1Removals | Sort-Object { $order[$_.kind] })
  Write-Evidence 'run1-removal-set.txt' (($Run1Removals | ForEach-Object { $_.command }) -join "`r`n") | Out-Null

  # ---------------------------------------------------------------- 2 Rerun
  Section '2 Rerun'
  $f2 = Start-Provisioning 'run2' $SheetA
  $plan2 = Compose-And-Preview $f2 $HostName 'run2'
  Check "plan: every row 'exists', 0 to create" ((Plan-Rows $plan2 'create').Count -eq 0 -and @($plan2.actions | Where-Object { $_.state -ne 'exists' }).Count -eq 0) (($plan2.actions | ForEach-Object { "$($_.kind) $($_.name)=$($_.state)" }) -join '; ') | Out-Null
  Check 'plan: 0 blockers' (@($plan2.blockers).Count -eq 0) (@($plan2.blockers) -join '; ') | Out-Null
  $ev = Run-Step -RunId $f2.RunId -Path '/storage/apply' -Types @('storage.applied', 'storage.apply.failed') -Save 'run2-apply'
  $res2 = $ev.data.result
  Check "apply: every outcome 'exists'" (@($res2.outcomes | Where-Object { $_.status -ne 'exists' }).Count -eq 0 -and -not $res2.error) (($res2.outcomes | ForEach-Object { "$($_.kind) $($_.name)=$($_.status)" }) -join '; ') | Out-Null
  $after2 = Snap-Templates (Wsapi-Read 'after-apply-2')
  Check 'WSAPI: template count unchanged (P-21)' ($after2.Count -eq $after1.Count) "before=$($after1.Count) after=$($after2.Count)" | Out-Null
  Check 'removal set empty' (@($res2.removals).Count -eq 0) ((@($res2.removals) | ForEach-Object { $_.command }) -join ' ; ') | Out-Null

  # ---------------------------------------------------------------- 3 Conflict
  Section '3 Conflict'
  $VolumesC = @(
    @{ name = $Vol1; size_gib = '2'; provisioning_type = 'tpvv'; cpg = $Cpg; vvset = $VvSet },
    @{ name = $Vol2; size_gib = '1'; provisioning_type = 'reduce'; cpg = $Cpg; vvset = $VvSet },
    @{ name = $Vol3; size_gib = '1'; provisioning_type = 'tpvv'; cpg = $Cpg }   # in no VV set, in no export: SPEC-008 R5 must say so
  )
  $SheetC = Compose $Targets $VolumesC $HostSets 'compose-C'
  $f3 = Start-Provisioning 'run3' $SheetC
  $plan3 = Compose-And-Preview $f3 $HostName 'run3'
  $row = @($plan3.actions | Where-Object { $_.kind -eq 'volume' -and $_.name -eq $Vol1 })[0]
  Check "plan: $Vol1 is 'conflict'" ($row -and $row.state -eq 'conflict') $(if ($row) { $row.reason } else { 'no row' }) | Out-Null
  Check 'plan: blockers non-empty' (@($plan3.blockers).Count -gt 0) (@($plan3.blockers) -join '; ') | Out-Null
  Check "plan: names the volume no export presents, $Vol3 (P-19)" (@($plan3.notes | Where-Object { $_ -eq "1 volume is not presented by this plan: $Vol3" }).Count -eq 1) (@($plan3.notes) -join ' | ') | Out-Null
  $refused = Api 'POST' "/runs/$($f3.RunId)/storage/apply" $null 'run3-apply-refused'
  Check 'POST /storage/apply refused (HTTP 4xx)' ($refused.Status -ge 400 -and $refused.Status -lt 500) "HTTP $($refused.Status): $($refused.Text)" | Out-Null
  $after3Snap = Wsapi-Read 'after-conflict'
  $after3 = Snap-Templates $after3Snap
  Check 'WSAPI unchanged' ($after3.Count -eq $after1.Count -and (Snap-Counts $after3Snap).volumes -eq (Snap-Counts $after1Snap).volumes) "templates=$($after3.Count) volumes=$((Snap-Counts $after3Snap).volumes)" | Out-Null

  # ---------------------------------------------------------------- 4 Blank members
  Section '4 Blank members'
  $f4 = Start-Provisioning 'run4' $SheetA
  $ev = Run-Step -RunId $f4.RunId -Path '/storage/preview' -Types @('storage.previewed', 'storage.preview.failed') -Save 'run4-preview'
  $plan4 = $ev.data.plan
  Check "plan: a blocker names $HostSet" (@($plan4.blockers | Where-Object { $_ -like "*$HostSet*" }).Count -gt 0) (@($plan4.blockers) -join '; ') | Out-Null
  Check 'plan: no host rows' (@($plan4.actions | Where-Object { $_.kind -eq 'host' }).Count -eq 0) '' | Out-Null
  Check 'plan: no vlun rows (SPEC-005)' (@($plan4.actions | Where-Object { $_.kind -eq 'vlun' }).Count -eq 0) '' | Out-Null

  # ---------------------------------------------------------------- 5 Documents (on run 1)
  Section '5 Documents'
  # SPEC-008 R2 (ADR 0013): no credential in the request - the run holds the sheet's; this run proves it.
  $detail = Api 'GET' "/runs/$Run1" $null 'run1-detail'
  $ac = $detail.Json.array_credential
  Check "run holds the sheet's array credential ($ArrayUser)" ($ac -and $ac.available -eq $true -and $ac.source -eq 'provisioning' -and $ac.username -eq $ArrayUser) $(if ($ac) { "source=$($ac.source) user=$($ac.username) host=$($ac.host)" } else { 'no array_credential in GET /runs/{id}' }) | Out-Null
  # S-13 (2026-09-16): `-notmatch 'password'` matched the JSON KEY names of masked fields. The test is
  # that no password-named field carries a real value and the array password itself is nowhere in the body.
  $pwValues = @([regex]::Matches($detail.Text, '"[^"]*password[^"]*"\s*:\s*"([^"]*)"') | ForEach-Object { $_.Groups[1].Value })
  $unmasked = @($pwValues | Where-Object { $_ -ne '' -and $_ -notmatch '^\*+$' })
  $leaks = if ($ArrayPw) { $detail.Text.Contains($ArrayPw) } else { $false }
  Check 'GET /runs/{id} carries no password value (keys are masked)' ($unmasked.Count -eq 0 -and -not $leaks) "password-named fields: $($pwValues.Count), unmasked: $($unmasked.Count), array password present: $leaks" | Out-Null
  $creds = @{}
  $ev = Run-Step -RunId $Run1 -Path '/verify' -Body $creds -Types @('verify.completed', 'verify.failed') -Save 'run1-verify'
  $rep = $ev.data.report
  # passed/mismatches/health_total are properties on the server model, not in the JSON: count them here.
  $passedN = @($rep.checks | Where-Object { $_.status -eq 'pass' }).Count
  $mismatchN = @($rep.checks | Where-Object { $_.status -eq 'mismatch' }).Count
  $healthN = 0; foreach ($i in @($rep.health_issues)) { $healthN += [int]$i.qty }
  Check 'verify: reachable, no mismatch' ($ev.event_type -eq 'verify.completed' -and $rep.reachable -eq $true -and $mismatchN -eq 0) "passed=$passedN mismatches=$mismatchN health=$healthN" | Out-Null
  # ---- rc.22 SPEC-011: verify says what to look at (R1 detail rows on every status row, R3 match rule on every check)
  $noMatch = @($rep.checks | Where-Object { -not $_.PSObject.Properties['match'] -or (@('exact', 'contains', 'includes') -notcontains $_.match) })
  Check 'verify: every check states its match rule (V-4)' ($noMatch.Count -eq 0) (($noMatch | ForEach-Object { $_.field }) -join ', ') | Out-Null
  $dns = @($rep.checks | Where-Object { $_.field -eq 'DNS servers' })[0]
  $contact = @($rep.checks | Where-Object { $_.field -eq 'Support contact' })[0]
  Check "verify: DNS servers is 'includes', Support contact is 'contains' (V-4)" (($dns -and $dns.match -eq 'includes') -and ((-not $contact) -or $contact.match -eq 'contains')) "dns=$(if ($dns) { $dns.match } else { 'no row' }) contact=$(if ($contact) { $contact.match } else { 'no row' })" | Out-Null
  $noDetails = @($rep.health_issues | Where-Object { -not $_.PSObject.Properties['details'] })
  $detailN = 0; foreach ($i in @($rep.health_issues)) { $detailN += @($i.details).Count }
  Check 'verify: every status row carries its detail rows (V-1)' ($noDetails.Count -eq 0) "status rows=$(@($rep.health_issues).Count) detail rows=$detailN" | Out-Null
  $ev = Run-Step -RunId $Run1 -Path '/asbuilt' -Body $creds -Types @('asbuilt.generated', 'asbuilt.failed') -Save 'run1-asbuilt'
  Check 'as-built generated' ($ev.event_type -eq 'asbuilt.generated') $ev.message | Out-Null
  $docxPath = Join-Path $Out 'asbuilt.docx'
  Invoke-WebRequest @Common -Method Get -Uri "$Api/runs/$Run1/asbuilt/download" -OutFile $docxPath
  $zip = [System.IO.Compression.ZipFile]::OpenRead($docxPath)
  try {
    $entry = $zip.GetEntry('word/document.xml')
    $sr = New-Object System.IO.StreamReader($entry.Open()); $xml = $sr.ReadToEnd(); $sr.Close()
  } finally { $zip.Dispose() }
  $text = (($xml -replace '</w:p>', "`n") -replace '<[^>]+>', '') -replace '\s+', ' '
  Write-Evidence 'asbuilt-text.txt' $text | Out-Null
  foreach ($needle in @($Vol1, $VvSet, "host set $HostSet", 'To remove what this run created')) {
    Check "docx names '$needle'" ($text -like "*$needle*") '' | Out-Null
  }
  foreach ($line in @($Run1Removals | Where-Object { $_.kind -eq 'vlun' } | ForEach-Object { $_.command })) {
    Check "docx carries '$line'" ($text -like "*$line*") '' | Out-Null
  }
  Check "docx does NOT say 'did not include the SAN zoning step' (A-3)" ($text -notlike '*did not include the SAN zoning step*') '' | Out-Null
  # ---- rc.23 SPEC-012 R3 (A-4): the two run sections share a page - the first breaks, the second flows on
  $pZon = [regex]::Match($xml, '<w:p\b(?:(?!</w:p>).)*?SAN zoning designed in this run(?:(?!</w:p>).)*?</w:p>', 'Singleline')
  $pProv = [regex]::Match($xml, '<w:p\b(?:(?!</w:p>).)*?Provisioning performed in this run(?:(?!</w:p>).)*?</w:p>', 'Singleline')
  $zBreak = $pZon.Success -and ($pZon.Value -match 'pageBreakBefore'); $pBreak = $pProv.Success -and ($pProv.Value -match 'pageBreakBefore')
  Check 'docx: the provisioning run section flows on from the zoning one (A-4)' ($pZon.Success -and $pProv.Success -and $zBreak -and -not $pBreak) "zoning heading breaks=$zBreak provisioning heading breaks=$pBreak" | Out-Null
}
catch {
  $script:Fail = $true
  Check "scenario aborted: $($_.Exception.Message)" $false '' | Out-Null
  Write-Evidence 'error.txt' ($_ | Out-String) | Out-Null
}

# ------------------------------------------------------------------ 6 Cleanup (always attempted when run 1 created anything)
Section '6 Cleanup'
if ($SkipCleanup) {
  Note "-SkipCleanup: leaving $Prefix objects on the array. Paste run1-removal-set.txt over SSH when done."
} elseif ($Run1Removals.Count -eq 0) {
  Note 'nothing to clean: run 1 created nothing'
} else {
  try {
    $cmdFile = Join-Path $Out 'cleanup-commands.txt'
    [System.IO.File]::WriteAllText($cmdFile, ((($Run1Removals | ForEach-Object { $_.command }) + 'exit') -join "`n") + "`n", [System.Text.UTF8Encoding]::new($false))
    Write-Host "  Pasting run 1's removal set over SSH to $ArrayUser@$ArrayHost (ssh will ask for the password once)."
    # 5.1 turns native stderr into terminating errors under EAP=Stop (ssh prints its known-hosts note there).
    $eap = $ErrorActionPreference; $ErrorActionPreference = 'Continue'
    try { $transcript = & cmd /c "ssh -T -o StrictHostKeyChecking=accept-new $ArrayUser@$ArrayHost < `"$cmdFile`" 2>&1" | Out-String }
    finally { $ErrorActionPreference = $eap }
    Write-Evidence 'cleanup.txt' $transcript | Out-Null
    $bad = @($transcript -split "`n" | Where-Object { $_ -match 'Error|error|does not exist|Invalid|cannot|Cannot|member of|in use|not allowed|failed|Failed' })
    Check 'the removal lines were accepted (no CLI error text)' ($bad.Count -eq 0) ($bad -join ' | ') | Out-Null
    if (-not $script:Wsapi) { Wsapi-Login $ArrayHost $ArrayUser $ArrayPw }
    $final = Wsapi-Read 'after-cleanup'
    $left = Snap-Prefixed $final
    Check "no $Prefix object left" ($left.Count -eq 0) ($left -join ', ') | Out-Null
    $b = Snap-Counts $Baseline; $f = Snap-Counts $final
    $same = $true; foreach ($k in $b.Keys) { if ($b[$k] -ne $f[$k]) { $same = $false } }
    Check 'counts equal the baseline' $same (($f.GetEnumerator() | ForEach-Object { "$($_.Key)=$($_.Value)/$($b[$_.Key])" }) -join ' ') | Out-Null
  } catch {
    Check "cleanup failed: $($_.Exception.Message)" $false "paste $Out\run1-removal-set.txt by hand" | Out-Null
  }
}
Wsapi-Logout
$ArrayPw = $null; $VcPw = $null; $SwPw = $null; $Targets = $null

# ------------------------------------------------------------------ report
$fails = @($script:Results | Where-Object { $_.Verdict -eq 'FAIL' }).Count
$passes = @($script:Results | Where-Object { $_.Verdict -eq 'PASS' }).Count
$lines = @(
  "# SPEC-006 session - $stamp",
  "",
  "- App version: $Version",
  "- Runner: PowerShell $($PSVersionTable.PSVersion); TLS callback: $($script:TlsCallback)",
  "- Array: $ArrayHost ($ArrayUser)  ; CPG: $Cpg  ; host: $HostName",
  "- Run 1: $Run1",
  "- Result: **$passes PASS, $fails FAIL**" + $(if ($SkipCleanup) { ' (cleanup skipped by request)' } else { '' }),
  "",
  "| Section | Verdict | Check | Detail |",
  "|---|---|---|---|"
)
foreach ($r in $script:Results) { $lines += "| $($r.Section) | $($r.Verdict) | $($r.What) | $(($r.Detail -replace '\|', '/') -replace "`r?`n", ' ') |" }
$lines += ""
$lines += "Evidence: every API response as NN-<step>.json, WSAPI reads as NN-wsapi-<what>-<when>.json, asbuilt.docx, cleanup.txt."
$lines += ""
$lines += "## Still needs eyes - UI-only changes, one screenshot each (open run 1 in the browser)"
$lines += "1. Verify step: the line 'Using the array credential from the sheet: ...' and the 'Use a different credential' button (SPEC-008 R4)."
$lines += "2. Provision step, Compose card: pick two members - the box shows the names, not 'multiple' (SPEC-008 R6)."
$lines += "3. Discovery step: 'Hosts in this run' above 'Other hosts on this array', one legend line, RCIP state column (SPEC-009)."
$lines += "4. Zoning step after Build plan: designer legend, an alias with a space typed -> 'Use ...' button, blocks 1/2/3 (SPEC-010)."
$lines += "5. Verify step: one Array status row expanded to its detail rows; a Match row with 'contains the expected value' (SPEC-011)."
$lines += "6. Provision step: Result card Detail column with ids/WWNs; Continue label; 'To remove what this run created' (SPEC-012, SPEC-007)."
[System.IO.File]::WriteAllText((Join-Path $Out 'report.md'), ($lines -join "`r`n") + "`r`n", [System.Text.UTF8Encoding]::new($false))
Write-Host ""
Write-Host ("Session complete: {0} PASS, {1} FAIL  ->  {2}\report.md" -f $passes, $fails, $Out) -ForegroundColor $(if ($fails -eq 0) { 'Green' } else { 'Red' })
if ($fails -gt 0) { exit 1 }
exit 0
