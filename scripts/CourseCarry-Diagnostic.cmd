@echo off
setlocal
cd /d "%~dp0"

powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0CourseCarry-Diagnostic.ps1"
if errorlevel 1 (
  echo.
  echo CourseCarry could not create the diagnostic report.
  pause
  exit /b 1
)

echo.
echo Diagnostic complete. Please send startup-diagnostic.txt from:
echo %LOCALAPPDATA%\CourseCarry
pause
