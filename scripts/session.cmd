@echo off
REM Launcher for the SPEC-006 session runner (session.ps1).
REM   Bypasses the PowerShell execution policy: release scripts are unsigned and carry the
REM   "downloaded from the internet" mark, which RemoteSigned blocks (seen on the jump box 2026-09-15).
REM   No elevation - the runner only talks to the app's API, WSAPI and ssh.
REM Usage:  session.cmd -BaseSheet C:\path\to\Initialisation_sheet.xlsx
setlocal
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0session.ps1" %*
echo.
echo (window stays open so you can read the summary above)
pause
