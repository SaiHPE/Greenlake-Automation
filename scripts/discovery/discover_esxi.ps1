<#
  Read-only ESXi / host discovery via vCenter (PowerCLI). It only READS - no changes.

  Install once:  Install-Module VMware.PowerCLI -Scope CurrentUser
  Run:           .\discover_esxi.ps1 -VCenter 10.54.154.226 -User Administrator@vsphere.local
                 (you are prompted for the password)

  Captures: ESXi OS/version (-> array host persona), FC HBA WWPNs (-> zoning + createhost),
  iSCSI IQNs, existing datastores, and any HPE/3PARdata LUNs already presented.
#>
param(
  [Parameter(Mandatory = $true)][string]$VCenter,
  [Parameter(Mandatory = $true)][string]$User,
  [string]$Password
)

if (-not $Password) {
  $secure = Read-Host "Password for $User@$VCenter" -AsSecureString
  $Password = [Runtime.InteropServices.Marshal]::PtrToStringAuto(
    [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secure))
}

Set-PowerCLIConfiguration -InvalidCertificateAction Ignore -Confirm:$false | Out-Null
Connect-VIServer -Server $VCenter -User $User -Password $Password | Out-Null

"`n=== ESXi hosts (OS / version) - picks the array host persona ==="
Get-VMHost | Select-Object Name, Version, Build, Model, ConnectionState, PowerState | Format-Table -AutoSize

"`n=== FC HBA WWPNs (for zoning + createhost) ==="
Get-VMHost | Get-VMHostHBA -Type FibreChannel | Select-Object VMHost, Device, Model,
  @{ N = 'WWPN'; E = { ('{0:x}' -f $_.PortWorldWideName) -replace '(..)(?=.)', '$1:' } },
  Status | Format-Table -AutoSize

"`n=== iSCSI IQNs (only if iSCSI is used instead of FC) ==="
Get-VMHost | Get-VMHostHBA -Type iScsi | Select-Object VMHost, Device,
  @{ N = 'IQN'; E = { $_.IScsiName } } | Format-Table -AutoSize

"`n=== Existing datastores ==="
Get-Datastore | Select-Object Name, Type,
  @{ N = 'CapacityGB'; E = { [math]::Round($_.CapacityGB, 1) } },
  @{ N = 'FreeGB'; E = { [math]::Round($_.FreeSpaceGB, 1) } } | Format-Table -AutoSize

"`n=== HPE / 3PARdata SAN LUNs already seen by the hosts ==="
Get-VMHost | Get-ScsiLun -LunType disk | Where-Object { $_.Vendor -match '3PARdata' } |
  Select-Object VMHost, CanonicalName,
    @{ N = 'GB'; E = { [math]::Round($_.CapacityGB, 1) } }, MultipathPolicy | Format-Table -AutoSize

Disconnect-VIServer -Confirm:$false
