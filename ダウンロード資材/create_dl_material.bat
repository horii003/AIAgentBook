@echo off
REM ============================================================
REM AIAgentBook download material zip creator (launcher)
REM
REM This batch calls create_dl_material.ps1 which performs the
REM actual work. The batch itself is kept ASCII-only to avoid
REM cmd parsing issues with multibyte characters.
REM ============================================================

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0create_dl_material.ps1"
set "RC=%ERRORLEVEL%"

exit /b %RC%
