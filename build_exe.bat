@echo off
setlocal
cd /d "%~dp0"

set "BUILD_PYTHON=%COURSECARRY_BUILD_PYTHON%"
if not defined BUILD_PYTHON set "BUILD_PYTHON=.venv\Scripts\python.exe"

if not exist "%BUILD_PYTHON%" (
  echo Missing Python 3.11 build environment. Run setup_windows.bat first.
  exit /b 1
)

"%BUILD_PYTHON%" -c "import sys; raise SystemExit(0 if sys.version_info[:2] == (3, 11) else 1)"
if errorlevel 1 (
  echo The Windows release must be built with Python 3.11.
  exit /b 1
)

"%BUILD_PYTHON%" -m pip install -r requirements-dev.txt
if errorlevel 1 exit /b 1

"%BUILD_PYTHON%" -m unittest discover -s tests
if errorlevel 1 exit /b 1

powershell -NoProfile -ExecutionPolicy Bypass -File "scripts\build_windows.ps1" -PythonPath "%BUILD_PYTHON%"
if errorlevel 1 exit /b 1

echo.
echo Build complete: dist\CourseCarry\CourseCarry.exe
