@echo off
REM run_scraper.bat - Automatic MPF data scraper for Windows

echo === MPF Data Scraper ===
echo.

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH.
    echo Please install Python 3.11 or later from https://www.python.org/
    pause
    exit /b 1
)

REM Run the scraper
python mpf_scrape_json.py processed_data.json

echo.
echo === Complete! ===
echo Output file: processed_data.json
echo.
pause
