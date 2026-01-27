@echo off
REM run_scraper.bat - Automatic MPF data scraper for Windows
REM This script installs dependencies and runs the scraper without requiring admin rights

echo === MPF Data Scraper - Setup and Run ===
echo.

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH.
    echo Please install Python 3.11 or later from https://www.python.org/
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo. Found %PYTHON_VERSION%
echo.

REM Install dependencies without admin rights
echo === Installing dependencies (user mode, no admin required) ===
echo.

REM Install using pip with --user flag (no admin needed)
python -m pip install --user --quiet pandas requests beautifulsoup4 lxml 2>nul
if %errorlevel% neq 0 (
    echo Warning: pip install had some issues, but continuing...
)

echo. Dependencies installed
echo.

REM Run the scraper
echo === Running MPF data scraper ===
echo.

python mpf_scrape_json.py processed_data.json

echo.
echo === Complete! ===
echo Output file: processed_data.json
echo.
pause
