@echo off
REM Launcher for the SPEC-014 read-only lab check (spec014.ps1). Bypasses the execution policy.
REM Usage:  spec014.cmd -BaseSheet C:\path\Initialisation_sheet.xlsx [-WindowsUser administrator -WindowsAddress 10.132.30.137]
setlocal
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0spec014.ps1" %*
echo.
pause
