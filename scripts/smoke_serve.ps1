<#
.SYNOPSIS
  Serve-path smoke test for the packaged .exe - proves it actually boots and serves the web UI.

.DESCRIPTION
  CI's selftest only launches Chromium; it never imports the FastAPI app or runs the startup proxy
  resolution, so the frozen SERVE path was never exercised in CI - which is how the v0.9.1
  heap-corruption crash (STATUS_HEAP_CORRUPTION on a machine WITH a system proxy) shipped.

  This starts the built exe WITH a system proxy configured (the exact condition that crash needed),
  waits for uvicorn, and asserts HTTP 200 on /app/profile. Any failure produces a non-zero exit so the
  release build fails loudly. The HKCU proxy is saved and restored so the runner/box is left clean.

.PARAMETER ExePath     Path to the built exe (default: the PyInstaller onedir output).
.PARAMETER TimeoutSec  How long to wait for the app to start serving.
#>
param(
  [string]$ExePath = 'dist\AlletraOnboard\AlletraOnboard.exe',
  [int]$TimeoutSec = 45
)
$ErrorActionPreference = 'Stop'
if (-not (Test-Path $ExePath)) { throw "serve smoke-test: exe not found at $ExePath" }

# Launch WITH a system proxy set: the v0.9.1 crash only fired when the WinHTTP out-strings were
# non-null (i.e. a proxy exists). Save + restore so we leave the machine untouched.
$key = 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Internet Settings'
$saved = Get-ItemProperty -Path $key -ErrorAction SilentlyContinue
$oldEnable = $saved.ProxyEnable
$oldServer = $saved.ProxyServer
Set-ItemProperty -Path $key -Name ProxyEnable -Value 1
Set-ItemProperty -Path $key -Name ProxyServer -Value '127.0.0.1:8080'

$out = Join-Path $env:TEMP 'alletra_smoke_serve.out.log'
$err = Join-Path $env:TEMP 'alletra_smoke_serve.err.log'
Remove-Item $out, $err -ErrorAction SilentlyContinue
$proc = $null
$served = $false
$port = $null
try {
  $proc = Start-Process -FilePath $ExePath -RedirectStandardOutput $out -RedirectStandardError $err -PassThru -WindowStyle Hidden
  $deadline = (Get-Date).AddSeconds($TimeoutSec)
  while ((Get-Date) -lt $deadline) {
    Start-Sleep -Milliseconds 500
    if ($proc.HasExited) {
      $log = (Get-Content $out, $err -Raw -ErrorAction SilentlyContinue) -join "`n"
      throw "serve smoke-test: the app exited (code $($proc.ExitCode)) before serving - a startup crash.`n$log"
    }
    if (-not $port -and (Test-Path $out)) {
      $m = Select-String -Path $out -Pattern 'http://127\.0\.0\.1:(\d+)' -ErrorAction SilentlyContinue | Select-Object -First 1
      if ($m) { $port = [int]$m.Matches[0].Groups[1].Value }
    }
    if ($port) {
      try {
        $resp = Invoke-WebRequest -Uri "http://127.0.0.1:$port/app/profile" -UseBasicParsing -TimeoutSec 3
        if ($resp.StatusCode -eq 200) { $served = $true; break }
      } catch { }
    }
  }
}
finally {
  if ($proc -and -not $proc.HasExited) { Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue }
  if ($null -eq $oldEnable) { $oldEnable = 0 }
  Set-ItemProperty -Path $key -Name ProxyEnable -Value $oldEnable
  if ($null -ne $oldServer) { Set-ItemProperty -Path $key -Name ProxyServer -Value $oldServer }
  else { Remove-ItemProperty -Path $key -Name ProxyServer -ErrorAction SilentlyContinue }
}
if (-not $served) {
  $log = (Get-Content $out, $err -Raw -ErrorAction SilentlyContinue) -join "`n"
  throw "serve smoke-test FAILED: no HTTP 200 on /app/profile within $TimeoutSec s (port=$port).`n$log"
}
Write-Host "serve smoke-test OK: HTTP 200 on http://127.0.0.1:$port/app/profile (with a system proxy set)"
