@echo off
setlocal
cd /d "%~dp0"
py -3.11 -m venv .venv
if errorlevel 1 (
  echo CourseCarry source development requires Python 3.11.
  exit /b 1
)
".venv\Scripts\python.exe" -m pip install --upgrade pip
".venv\Scripts\python.exe" -m pip install -r requirements.txt
echo.
echo Setup complete.
echo CourseCarry uses your locally installed Google Chrome.
echo Run: run_windows.bat
pause
