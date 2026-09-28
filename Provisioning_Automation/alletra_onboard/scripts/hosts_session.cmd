@echo off
REM Launcher for the SPEC-014 hosts session (hosts_session.ps1) - READ-ONLY, safe on any array.
REM   Bypasses the execution policy (release scripts are unsigned and carry the download mark).
REM Usage:  hosts_session.cmd -BaseSheet C:\path\Initialisation_sheet.xlsx -HostsFile C:\path\hosts.csv
setlocal
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0hosts_session.ps1" %*
echo.
echo (window stays open so you can read the summary above)
pause
