@echo off
setlocal
cd /d "%~dp0"
py -m venv .venv
".venv\Scripts\python.exe" -m pip install --upgrade pip
".venv\Scripts\python.exe" -m pip install -r requirements.txt
echo.
echo Setup complete.
echo PoliteLoad uses your locally installed Google Chrome.
echo Run: run_windows.bat
pause
