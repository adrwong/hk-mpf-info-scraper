#!/bin/bash
# run_scraper.sh - Automatic MPF data scraper for Unix/Linux/macOS
# This script installs dependencies and runs the scraper without requiring admin rights

set -e  # Exit on error

echo "=== MPF Data Scraper - Setup and Run ==="
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed. Please install Python 3.11 or later."
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Found Python: $PYTHON_VERSION"
echo ""

# Install dependencies without admin rights
echo "=== Installing dependencies (user mode, no admin required) ==="
echo ""

# Install using pip with --user flag (no admin needed)
echo "Installing: pandas requests beautifulsoup4 lxml"
if python3 -m pip install --user --quiet pandas requests beautifulsoup4 lxml; then
    echo "✓ Dependencies installed successfully"
else
    echo "Warning: pip install encountered issues. Checking if dependencies are available..."
    # Check if we can at least import the critical modules
    if python3 -c "import pandas, requests, bs4, lxml" 2>/dev/null; then
        echo "✓ Required modules are available (may have been already installed)"
    else
        echo "ERROR: Failed to install or find required dependencies."
        echo "Please install manually: pip3 install --user pandas requests beautifulsoup4 lxml"
        exit 1
    fi
fi
echo ""

# Run the scraper
echo "=== Running MPF data scraper ==="
echo ""

python3 mpf_scrape_json.py processed_data.json

echo ""
echo "=== Complete! ==="
echo "Output file: processed_data.json"
