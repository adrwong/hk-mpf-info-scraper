#!/bin/bash
# run_scraper.sh - MPF data scraper for Unix/Linux/macOS
# Note: Python dependencies must be pre-installed (pandas, requests, beautifulsoup4, lxml)

set -e  # Exit on error

echo "=== MPF Data Scraper ==="
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed. Please install Python 3.11 or later."
    exit 1
fi

# Run the scraper
python3 mpf_scrape_json.py processed_data.json

echo ""
echo "=== Complete! ==="
echo "Output file: processed_data.json"
