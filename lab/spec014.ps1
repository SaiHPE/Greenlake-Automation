<#
.SYNOPSIS
  SPEC-014 offline, read-only lab check (Windows PowerShell 5.1).

.DESCRIPTION
  Starts PROVISION_ONLY runs from disposable copies of one workbook, replacing only its Hosts tab.
  Calls Discovery, a read-only zoning plan, and provisioning preview. NEVER calls storage/apply,
  array write methods, switch writes, or a host write command. The app persists the new runs.
  No workbook, credentials, or full API responses are written to the evidence folder.

.EXAMPLE
  powershell -NoProfile -ExecutionPolicy Bypass -File .\spec014.ps1 -BaseSheet "C:\path\Initialisation_sheet.xlsx"
.EXAMPLE
  powershell -NoProfile -ExecutionPolicy Bypass -File .\spec014.ps1 -BaseSheet "C:\path\Initialisation_sheet.xlsx" -WindowsUser administrator -WindowsAddress 10.132.30.137
#>
[CmdletBinding()]
param(
  [Parameter(Mandatory = $true)][string]$BaseSheet,
  [string]$Api = 'http://127.0.0.1:8765',
  [string]$WindowsHost = 'arcus-win137',
  [string]$WindowsAddress = '10.132.30.137',
  [string]$WindowsUser = '',
  [string]$LinuxHost = '',
  [string]$LinuxAddress = '',
  [string]$LinuxUser = '',
  [ValidateSet('linux', 'vme')][string]$LinuxOs = 'linux',
  [string]$OutRoot = ''
)
$ErrorActionPreference = 'Stop'
if (-not $OutRoot) {
  $OutRoot = if ($PSScriptRoot) { $PSScriptRoot } else { Split-Path -Parent $MyInvocation.MyCommand.Path }
  if (-not $OutRoot) { $OutRoot = (Get-Location).Path }
}
$Out = Join-Path $OutRoot ('spec014-' + (Get-Date -Format 'yyyyMMdd-HHmmss'))
New-Item -ItemType Directory -Path $Out -Force | Out-Null
$script:Checks = New-Object System.Collections.ArrayList
$script:Facts = New-Object System.Collections.ArrayList
$script:Notes = New-Object System.Collections.ArrayList
$script:Section = ''
$script:Runs = New-Object System.Collections.ArrayList
$script:Counter = 0

function Check([string]$label, [bool]$ok, [string]$detail = '') {
  $result = if ($ok) { 'PASS' } else { 'FAIL' }
  [void]$script:Checks.Add([pscustomobject]@{ Section = $script:Section; Result = $result; Check = $label; Detail = $detail })
  Write-Host "  [$result] $label $(if ($detail) { "- $detail" })" -ForegroundColor $(if ($ok) { 'Green' } else { 'Red' })
}
function Skip([string]$label, [string]$detail) {
  [void]$script:Checks.Add([pscustomobject]@{ Section = $script:Section; Result = 'SKIP'; Check = $label; Detail = $detail })
  Write-Host "  [SKIP] $label - $detail" -ForegroundColor Yellow
}
function Section([string]$label) { $script:Section = $label; Write-Host "`n== $label" -ForegroundColor Cyan }
function Request([string]$method, [string]$path, $body = $null) {
  $options = @{ Uri = "$Api$path"; Method = $method; UseBasicParsing = $true; TimeoutSec = 120 }
  if ($null -ne $body) {
    $options.ContentType = 'application/json'
    $options.Body = $body | ConvertTo-Json -Depth 15 -Compress
  }
  try {
    $response = Invoke-WebRequest @options
    # 5.1 decodes a charset-less JSON body as Latin-1 (em dashes arrive as mojibake).
    return ([System.Text.Encoding]::UTF8.GetString($response.RawContentStream.ToArray()) | ConvertFrom-Json)
  }
  catch { throw "$method $path failed (HTTP $([int]$_.Exception.Response.StatusCode)). Check the app console; do not paste credentials." }
}
function EventCount([string]$runId) { return @((Request 'GET' "/runs/$runId/events").events).Count }
function Step([string]$runId, [string]$path, [string[]]$done) {
  $since = EventCount $runId
  Request 'POST' "/runs/$runId$path" | Out-Null
  $deadline = (Get-Date).AddMinutes(5)
  while ((Get-Date) -lt $deadline) {
    Start-Sleep -Seconds 2
    $events = @((Request 'GET' "/runs/$runId/events").events)
    for ($index = $events.Count - 1; $index -ge $since; $index--) {
      if ($events[$index].event_type -eq 'step.crashed') { throw "Step $path crashed: $($events[$index].message)" }
      if ($done -contains $events[$index].event_type) { return $events[$index] }
    }
  }
  throw "Timed out waiting for $path; see the app's Events view for run $runId"
}
function MakeRun([string]$label, $hosts, $hostsets = $null) {
  # The compose endpoint writes a copy of the base workbook in memory; the base file is untouched.
  $body = @{ base_b64 = $script:BaseB64; targets = $script:Targets; hosts = @($hosts) }
  if ($null -ne $hostsets) { $body.hostsets = @($hostsets) }
  $composed = Request 'POST' '/init-sheet/compose' $body
  $upload = Request 'POST' '/init-sheet/upload' @{ content_b64 = $composed.content_b64 }
  $id = (Request 'POST' '/runs/from-sheet' @{ token = $upload.token; mode = 'PROVISION_ONLY' }).run.run_id
  [void]$script:Runs.Add("$label=$id")
  Write-Host "  $label run $id"
  return $id
}
function FindHost($report, [string]$name) { return @($report.hosts | Where-Object { $_.name -eq $name })[0] }
function Explain($report) {
  # What discovery itself said: the first thing to read when it reached nothing.
  if ($report.error) { Write-Host "  Discovery error: $($report.error)" -ForegroundColor Red; [void]$script:Notes.Add("error: $($report.error)") }
  foreach ($n in @($report.notes)) { Write-Host "  note: $n" -ForegroundColor DarkGray; [void]$script:Notes.Add($n) }
}
function ProbeHost([string]$label, $row) {
  Section $label
  $id = MakeRun $label @($row)
  $event = Step $id '/discover' @('discover.completed')
  $report = $event.data.report
  Check 'Discovery reached the array' (@($report.array_ports).Count -gt 0 -and -not $report.error) "ports=$(@($report.array_ports).Count)"
  if (@($report.array_ports).Count -eq 0 -or $report.error) { Explain $report }
  $foundHost = FindHost $report $row.name
  Check 'Sheet host stays visible' ($null -ne $foundHost -and $foundHost.in_run) $(if ($foundHost) { "lookup=$($foundHost.lookup)" } else { 'no row' })
  if ($foundHost) {
    $read = @($report.host_reads | Where-Object { $_.host_name -eq $row.name })[0]
    Check 'Host read carries no password field' (-not $read -or -not $read.PSObject.Properties['password']) ''
    Write-Host "  Host: $($foundHost.name) OS=$($foundHost.os) serial=$($foundHost.serial_number) WWPNs=$(@($foundHost.wwpns).Count) IQNs=$(@($foundHost.iqns).Count)"
    Write-Host "  Lookup: $($foundHost.lookup) / $($foundHost.host_read)"
    if ($read) { Write-Host "  Server read: method=$($read.method) serial=$($read.serial_number) WWPNs=$(@($read.wwpns).Count) IQNs=$(@($read.iqns).Count) multipath=$($read.multipath) error=$($read.error)" }
    [void]$script:Facts.Add([pscustomobject]@{
      Section = $label; Name = $foundHost.name; OS = $foundHost.os; Serial = $foundHost.serial_number
      WWPNs = @($foundHost.wwpns) -join ', '; IQNs = @($foundHost.iqns) -join ', '
      Lookup = $foundHost.lookup; HostRead = $foundHost.host_read; Multipath = $foundHost.multipath
    })
    if ($row.username -and (-not $read -or $read.error)) {
      Check 'Host-side read succeeded' $false $(if ($read) { $read.error } else { 'no host read in discovery report' })
    } elseif ($read) {
      Check 'Host-side read succeeded' $true $read.method
      Check 'Host-side serial returned' ([bool]$read.serial_number) ''
      Check 'Host-side FC WWPN or iSCSI IQN returned' (@($read.wwpns).Count -gt 0 -or @($read.iqns).Count -gt 0) ''
    }
  }
  $detail = Request 'GET' "/runs/$id"
  Check 'Run detail does not echo host password' (-not $script:HostPassword -or -not (($detail | ConvertTo-Json -Depth 20 -Compress).Contains($script:HostPassword))) ''
  if ($script:HostPassword) {
    $events = Request 'GET' "/runs/$id/events"
    Check 'Events do not echo host password' (-not (($events | ConvertTo-Json -Depth 30 -Compress).Contains($script:HostPassword))) ''
  }
  return @{ Id = $id; Report = $report; Host = $foundHost }
}

Write-Host "SPEC-014 read-only runner -> $Out"
$script:HostPassword = ''
$exitCode = 0
try {
  Section 'Environment'
  $health = Request 'GET' '/health'
  Write-Host "  App version: $($health.version) (version alone does not prove the SPEC-014 bundle is running)"
  $file = [System.IO.File]::Open((Resolve-Path $BaseSheet).Path, 'Open', 'Read', 'ReadWrite')
  try { $mem = New-Object System.IO.MemoryStream; $file.CopyTo($mem); $script:BaseB64 = [Convert]::ToBase64String($mem.ToArray()) }
  finally { $file.Dispose() }
  $arrayPassword = Read-Host 'Array admin password (Enter = the one in the sheet)' -AsSecureString
  $vcenterPassword = Read-Host 'vCenter password (Enter = the one in the sheet)' -AsSecureString
  $switchPassword = Read-Host 'Switch password, both fabrics (Enter = the ones in the sheet)' -AsSecureString
  $plain = { param($secret) [System.Net.NetworkCredential]::new('', $secret).Password }
  $script:Targets = @{}
  foreach ($pair in @(@('prov_array_password', $arrayPassword), @('prov_vcenter_password', $vcenterPassword),
                      @('prov_sw1_password', $switchPassword), @('prov_sw2_password', $switchPassword))) {
    $value = & $plain $pair[1]
    if ($value) { $script:Targets[$pair[0]] = $value }
  }

  Section 'ESXi via vCenter'
  $baseId = MakeRun 'vcenter' @()
  $base = (Step $baseId '/discover' @('discover.completed')).data.report
  $esxi = @($base.host_identities | Where-Object { $_.host_name })
  Check 'Baseline discovery reached the array' (@($base.array_ports).Count -gt 0 -and -not $base.error) "ports=$(@($base.array_ports).Count)"
  Check 'vCenter reports host identities (SPEC-014 R2)' ($esxi.Count -gt 0) "hosts=$($esxi.Count) HBAs=$(@($base.host_hbas).Count)"
  if (@($base.array_ports).Count -eq 0 -or $base.error -or $esxi.Count -eq 0) { Explain $base }
  if ($esxi.Count) {
    $sample = @($esxi | Where-Object { $name = $_.host_name; @($base.host_hbas | Where-Object { $_.host_name -eq $name }).Count -gt 0 -or @($_.iqns).Count -gt 0 })[0]
    if (-not $sample) { $sample = $esxi[0] }
    Write-Host "  $($sample.host_name) serial=$($sample.serial_number) IQNs=$(@($sample.iqns).Count)"
    Check 'ESXi serial from vCenter' ([bool]$sample.serial_number) ''
    $lookup = ProbeHost 'No-ID ESXi sheet lookup' @{ name = $sample.host_name; os = 'esxi'; address = $sample.host_name }
    Check 'No-ID sheet row resolved by vCenter' ($lookup.Host -and $lookup.Host.lookup -like 'found in vCenter*' -and (@($lookup.Host.wwpns).Count -gt 0 -or @($lookup.Host.iqns).Count -gt 0)) $(if ($lookup.Host) { $lookup.Host.lookup } else { 'missing' })

    # A Host sets member typed with the sheet's own name for a host vCenter calls something else.
    Section 'Host-set member under a sheet name (preview only)'
    $aliasId = MakeRun 'sheet-name member' @(@{ name = 'zz_s14_alias'; os = 'esxi'; address = $sample.host_name }) @(@{ name = 'zz_s14_alias_hs'; members = 'zz_s14_alias, zz_s14_nobody' })
    Step $aliasId '/discover' @('discover.completed') | Out-Null
    Step $aliasId '/zoning/preview' @('zoning.proper', 'zoning.previewed') | Out-Null
    $aliasPlan = (Step $aliasId '/storage/preview' @('storage.previewed', 'storage.preview.failed')).data.plan
    $renamed = "Host set zz_s14_alias_hs: sheet host 'zz_s14_alias' is the same server as '$($sample.host_name)' and is planned under that name."
    Check 'Sheet-name member planned under the vCenter name' (@($aliasPlan.notes) -contains $renamed) $(if (@($aliasPlan.notes) -contains $renamed) { $renamed } else { (@($aliasPlan.notes) -join ' / ') })
    Check 'Unknown member is named in the plan notes' (@($aliasPlan.notes | Where-Object { $_ -like "*member 'zz_s14_nobody' is not a host this run can name*" }).Count -gt 0) ''
    $setRow = @($aliasPlan.actions | Where-Object { $_.kind -eq 'hostset' -and $_.name -eq 'zz_s14_alias_hs' })[0]
    if ($setRow) { Check 'Host set row lists the vCenter name' (@($setRow.detail.members) -contains $sample.host_name) (@($setRow.detail.members) -join ', ') }
    elseif ($aliasPlan.error) { Skip 'Host set row lists the vCenter name' "Plan stopped before the set rows: $($aliasPlan.error)" }
  }

  Section 'No-ID sheet host not found'
  $unknown = ProbeHost 'Unresolved host' @{ name = 'zz_spec014_unknown'; os = 'linux'; address = '192.0.2.123' }
  Check 'Unresolved sheet host has a discovery note' (@($unknown.Report.notes | Where-Object { $_ -like 'Sheet host zz_spec014_unknown: not found*' }).Count -gt 0) ''
  $vcenterDown = @($unknown.Report.notes | Where-Object { $_ -like 'vCenter discovery failed*' }).Count -gt 0
  $wording = $(if ($vcenterDown) { '*vCenter was not reached*' } else { '*not in vCenter*' })
  Check "Not-found wording matches vCenter state (vCenter down=$vcenterDown)" ($unknown.Host -and $unknown.Host.lookup -like $wording) $(if ($unknown.Host) { $unknown.Host.lookup } else { 'missing' })

  $vcenterNames = @($base.host_identities | ForEach-Object { $_.host_name })
  $arrayCandidate = @($base.array_hosts | Where-Object {
    $_.name -and $vcenterNames -notcontains $_.name -and $_.name -ne $WindowsHost -and
    (@($_.wwpns.PSObject.Properties).Count -gt 0 -or @($_.iqns.PSObject.Properties).Count -gt 0)
  })[0]
  if ($arrayCandidate) {
    $fromArray = ProbeHost 'No-ID array host lookup' @{ name = $arrayCandidate.name; os = '' }
    Check 'Array host object supplies initiators' ($fromArray.Host -and $fromArray.Host.lookup -like 'found on the array as host*' -and (@($fromArray.Host.wwpns).Count -gt 0 -or @($fromArray.Host.iqns).Count -gt 0)) $(if ($fromArray.Host) { $fromArray.Host.lookup } else { 'missing' })
    $fqdn = "$($arrayCandidate.name).spec014.local"
    $fromShort = ProbeHost 'Short-name array host lookup' @{ name = $fqdn; os = '' }
    Check "Sheet FQDN $fqdn matched array host $($arrayCandidate.name)" ($fromShort.Host -and $fromShort.Host.lookup -like "found on the array as host $($arrayCandidate.name) (short-name match)" -and (@($fromShort.Host.wwpns).Count -gt 0 -or @($fromShort.Host.iqns).Count -gt 0)) $(if ($fromShort.Host) { $fromShort.Host.lookup } else { 'missing' })
  } else { Section 'Array host lookup'; Skip 'No-ID array host lookup' 'No array host with initiators outside the Windows/vCenter candidates' }

  $win = ProbeHost 'Windows no-ID lookup' @{ name = $WindowsHost; os = 'windows'; address = $WindowsAddress }
  if ($win.Host -and $win.Host.lookup -like 'not found*') { Skip 'Array/initiator lookup' "No lab identity for $WindowsHost; it should remain visible" }
  elseif ($win.Host) { Check 'Array/initiator lookup found IDs' (@($win.Host.wwpns).Count -gt 0 -or @($win.Host.iqns).Count -gt 0) $win.Host.lookup }

  if ($WindowsUser) {
    $script:HostPassword = & $plain (Read-Host "WinRM password for $WindowsUser on $WindowsAddress" -AsSecureString)
    $winRow = @{ name = $WindowsHost; os = 'windows'; address = $WindowsAddress; username = $WindowsUser; password = $script:HostPassword }
    $checked = ProbeHost 'Windows server read (WinRM)' $winRow
    $read = @($checked.Report.host_reads | Where-Object { $_.host_name -eq $WindowsHost })[0]
    if ($read -and -not $read.error -and @($read.wwpns).Count) {
      Section 'Typed-vs-read blocker (no apply)'
      $wrong = $winRow.Clone()
      $wrong.wwpns = '1000000000000001'
      $badId = MakeRun 'wrong-wwpn' @($wrong)
      Step $badId '/discover' @('discover.completed') | Out-Null
      Step $badId '/zoning/preview' @('zoning.proper', 'zoning.previewed') | Out-Null
      $plan = (Step $badId '/storage/preview' @('storage.previewed', 'storage.preview.failed')).data.plan
      Check 'Typed WWPN mismatch blocks the plan' (@($plan.blockers | Where-Object { $_ -like "*1000000000000001*not on the server*" }).Count -gt 0) (($plan.blockers | Where-Object { $_ -like "*1000000000000001*" }) -join '; ')
    } else { Skip 'Typed-vs-read blocker' 'WinRM did not return an FC WWPN; no mismatch comparison possible' }
    $script:HostPassword = ''
  } else { Skip 'Windows host login and mismatch' 'Pass -WindowsUser after confirming WinRM 5985/5986 and local admin access' }

  if ($LinuxHost -and $LinuxAddress -and $LinuxUser) {
    $script:HostPassword = & $plain (Read-Host "SSH password for $LinuxUser on $LinuxAddress" -AsSecureString)
    ProbeHost 'Linux server read (SSH)' @{ name = $LinuxHost; os = $LinuxOs; address = $LinuxAddress; username = $LinuxUser; password = $script:HostPassword } | Out-Null
    $script:HostPassword = ''
  } else { Section 'Linux'; Skip 'Linux host login' 'No Linux host/address/login provided' }
} catch {
  Check 'Runner stopped' $false $_.Exception.Message
  $exitCode = 1
} finally {
  $script:BaseB64 = $null; $script:Targets = $null; $script:HostPassword = $null
  $lines = @('# SPEC-014 read-only lab check', '', "- Run IDs: $($script:Runs -join '; ')",
    "- Result: $(@($script:Checks | Where-Object { $_.Result -eq 'PASS' }).Count) PASS, $(@($script:Checks | Where-Object { $_.Result -eq 'FAIL' }).Count) FAIL, $(@($script:Checks | Where-Object { $_.Result -eq 'SKIP' }).Count) SKIP", '',
    '| Section | Result | Check | Detail |', '|---|---|---|---|')
  foreach ($c in $script:Checks) { $lines += "| $($c.Section) | $($c.Result) | $($c.Check) | $(($c.Detail -replace '\|', '/') -replace "`r?`n", ' ') |" }
  $lines += @('', '## Discovered host facts', '', '| Section | Host / OS | Serial | WWPNs | IQNs | Lookup / read | Multipath |', '|---|---|---|---|---|---|---|')
  foreach ($fact in $script:Facts) {
    $lines += "| $($fact.Section) | $($fact.Name) / $($fact.OS) | $($fact.Serial) | $($fact.WWPNs) | $($fact.IQNs) | $($fact.Lookup); $($fact.HostRead) | $($fact.Multipath) |"
  }
  if ($script:Notes.Count) {
    $lines += @('', '## What discovery said (errors and notes)', '')
    foreach ($n in ($script:Notes | Select-Object -Unique)) { $lines += "- $($n -replace "`r?`n", ' ')" }
  }
  [System.IO.File]::WriteAllText((Join-Path $Out 'report.md'), ($lines -join "`r`n") + "`r`n", [System.Text.UTF8Encoding]::new($false))
  Write-Host "`nReport: $Out\report.md"
}
if ($exitCode -or @($script:Checks | Where-Object { $_.Result -eq 'FAIL' }).Count -gt 0) { exit 1 }
exit 0