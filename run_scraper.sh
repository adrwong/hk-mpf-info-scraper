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
python3 -m pip install --user --quiet pandas requests beautifulsoup4 lxml 2>&1 || {
    echo "Warning: pip install had some issues, but continuing..."
}

echo "✓ Dependencies installed"
echo ""

# Run the scraper
echo "=== Running MPF data scraper ==="
echo ""

python3 mpf_scrape_json.py processed_data.json

echo ""
echo "=== Complete! ==="
echo "Output file: processed_data.json"
