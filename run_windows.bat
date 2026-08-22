@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo PoliteLoad is not set up yet. Run setup_windows.bat first.
  pause
  exit /b 1
)
".venv\Scripts\python.exe" main.py
pause
