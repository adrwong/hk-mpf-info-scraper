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
echo Installing: pandas requests beautifulsoup4 lxml
python -m pip install --user --quiet pandas requests beautifulsoup4 lxml
if %errorlevel% equ 0 (
    echo. Dependencies installed successfully
) else (
    echo Warning: pip install encountered issues. Checking if dependencies are available...
    REM Check if we can at least import the critical modules
    python -c "import pandas, requests, bs4, lxml" >nul 2>&1
    if %errorlevel% equ 0 (
        echo. Required modules are available ^(may have been already installed^)
    ) else (
        echo ERROR: Failed to install or find required dependencies.
        echo Please install manually: python -m pip install --user pandas requests beautifulsoup4 lxml
        pause
        exit /b 1
    )
)
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
