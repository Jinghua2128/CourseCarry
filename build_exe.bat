@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
  echo Missing .venv. Run setup_windows.bat first.
  exit /b 1
)

".venv\Scripts\python.exe" -m pip install -r requirements-dev.txt
if errorlevel 1 exit /b 1

".venv\Scripts\python.exe" -m unittest discover -s tests
if errorlevel 1 exit /b 1

".venv\Scripts\python.exe" -m PyInstaller --noconfirm --clean PoliteLoad.spec
if errorlevel 1 exit /b 1

echo.
echo Build complete: dist\PoliteLoad\PoliteLoad.exe
