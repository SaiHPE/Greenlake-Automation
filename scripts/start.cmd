@echo off
REM Double-click launcher for Alletra Onboard.
REM   - Bypasses the PowerShell execution policy (release scripts are unsigned and carry the
REM     "downloaded from the internet" mark, which Restricted/RemoteSigned policies block).
REM   - Self-elevates so the in-app "Sync system clock" button can set the clock.
REM Pass-through args (e.g. -Proxy http://proxy:8080) are forwarded to start.ps1.
setlocal
cd /d "%~dp0"

net session >nul 2>&1
if %errorlevel% NEQ 0 (
  echo Requesting administrator access...
  powershell -NoProfile -ExecutionPolicy Bypass -Command "Start-Process -FilePath '%~f0' -ArgumentList '%*' -Verb RunAs"
  exit /b
)

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0start.ps1" %*
echo.
echo (window stays open so you can read any messages above)
pause
