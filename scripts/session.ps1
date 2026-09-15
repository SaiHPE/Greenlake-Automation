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
$Vol1 = "${Prefix}vol01"; $Vol2 = "${Prefix}vol02"; $VvSet = "${Prefix}vvs"; $HostSet = "${Prefix}hs"
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

if ($PSVersionTable.PSVersion.Major -lt 6) {
  [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.SecurityProtocolType]::Tls12
  # A script-block callback ({ $true }) runs only on the FIRST handshake; later handshakes happen on
  # a .NET thread with no runspace and fail with "An unexpected error occurred on a send" (S-12 FAIL 4,
  # and every read on 2026-09-15 once keep-alive was off). The callback must be compiled code.
  try {
    Add-Type -TypeDefinition @'
#pragma warning disable SYSLIB0014
using System.Net;
public static class SessionTrustArrayCert {
  public static void Enable() { ServicePointManager.ServerCertificateValidationCallback = delegate { return true; }; }
}
'@ -ErrorAction Stop
    [SessionTrustArrayCert]::Enable()
  } catch {
    Write-Warning "Add-Type failed ($($_.Exception.Message)); falling back to a script-block callback (WSAPI may drop after the first request)"
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
    $reader = New-Object System.IO.StreamReader($r.GetResponseStream(), [System.Text.Encoding]::UTF8); $text = $reader.ReadToEnd(); $reader.Close()
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
    @{ name = $Vol2; size_gib = '1'; provisioning_type = 'reduce'; cpg = $Cpg; vvset = $VvSet }
  )
  $SheetC = Compose $Targets $VolumesC $HostSets 'compose-C'
  $f3 = Start-Provisioning 'run3' $SheetC
  $plan3 = Compose-And-Preview $f3 $HostName 'run3'
  $row = @($plan3.actions | Where-Object { $_.kind -eq 'volume' -and $_.name -eq $Vol1 })[0]
  Check "plan: $Vol1 is 'conflict'" ($row -and $row.state -eq 'conflict') $(if ($row) { $row.reason } else { 'no row' }) | Out-Null
  Check 'plan: blockers non-empty' (@($plan3.blockers).Count -gt 0) (@($plan3.blockers) -join '; ') | Out-Null
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
  $creds = @{ username = $ArrayUser; password = $ArrayPw }
  $ev = Run-Step -RunId $Run1 -Path '/verify' -Body $creds -Types @('verify.completed', 'verify.failed') -Save 'run1-verify'
  $rep = $ev.data.report
  # passed/mismatches/health_total are properties on the server model, not in the JSON: count them here.
  $passedN = @($rep.checks | Where-Object { $_.status -eq 'pass' }).Count
  $mismatchN = @($rep.checks | Where-Object { $_.status -eq 'mismatch' }).Count
  $healthN = 0; foreach ($i in @($rep.health_issues)) { $healthN += [int]$i.qty }
  Check 'verify: reachable, no mismatch' ($ev.event_type -eq 'verify.completed' -and $rep.reachable -eq $true -and $mismatchN -eq 0) "passed=$passedN mismatches=$mismatchN health=$healthN" | Out-Null
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
[System.IO.File]::WriteAllText((Join-Path $Out 'report.md'), ($lines -join "`r`n") + "`r`n", [System.Text.UTF8Encoding]::new($false))
Write-Host ""
Write-Host ("Session complete: {0} PASS, {1} FAIL  ->  {2}\report.md" -f $passes, $fails, $Out) -ForegroundColor $(if ($fails -eq 0) { 'Green' } else { 'Red' })
if ($fails -gt 0) { exit 1 }
exit 0
