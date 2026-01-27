# MPF Fund Data Scraper

A Python scraper for extracting Mandatory Provident Fund (MPF) data from the MPFA website.

## Quick Start (Recommended)

### Using Pre-built Executables (No Python Required)

Download the latest pre-compiled executable for your platform from the [Releases](../../releases) page:

- **Linux/macOS**: `mpf-scraper-linux`
- **Windows**: `mpf-scraper-windows.exe`

Then run:

**For Unix/Linux/macOS:**
```bash
chmod +x mpf-scraper-linux
./mpf-scraper-linux
```

**For Windows:**
```cmd
mpf-scraper-windows.exe
```

The executable will:
1. Scrape data from all three language versions (English, Traditional Chinese, Simplified Chinese)
2. Combine all data into a single `processed_data.json` file

No Python installation or dependencies required!

### Using Python Script

If you prefer to run the Python script directly:

```bash
# Install dependencies
pip install pandas requests beautifulsoup4 lxml

# Run the scraper
python mpf_scrape_json.py
```

The output JSON file contains all fund information from all three languages with a `_language` field indicating the source language for each record.

## Features

- **Standalone executables**: Pre-compiled binaries for Linux and Windows (no Python installation required)
- **Multi-language support**: Scrape data in English, Traditional Chinese, or Simplified Chinese
- **Single-command execution**: One executable file does everything
- Scrapes comprehensive MPF fund information from the MPFA website
- Extracts and properly labels all fund data including:
  - Basic fund information (Scheme, Fund Name, Trustee, Type, Launch Date, Fund Size, Risk Class)
  - Fee information (Fund Expense Ratio - FER)
  - Performance returns for multiple time periods:
    - 1 Year: Annualized, Cumulative, and Calendar Year returns (2024, 2023)
    - 5 Year: Annualized and Cumulative returns
    - 10 Year: Annualized and Cumulative returns
    - Since Launch: Annualized and Cumulative returns
- Handles complex HTML table structure with multi-level headers and colspan attributes
- Removes duplicate columns caused by HTML structure
- Extracts data update date from the page

## Building Executables

The GitHub Actions workflow automatically builds executables for both Linux and Windows on every push and pull request. 

To build executables manually:

```bash
# Install PyInstaller
pip install pyinstaller pandas requests beautifulsoup4 lxml

# Build for your current platform
pyinstaller --onefile --name mpf-scraper mpf_scrape_json.py

# The executable will be in the dist/ directory
```

## Requirements (for Python script only)

```
pandas
requests
beautifulsoup4
lxml
openpyxl (optional, for Excel export)
```

## Installation (for Python script only)

Install dependencies using pip:

```bash
pip install pandas requests beautifulsoup4 lxml openpyxl
```

Or using uv:

```bash
uv pip install pandas requests beautifulsoup4 lxml openpyxl
```

## Usage

### Using Pre-built Executables

Simply run the downloaded executable:

```bash
# Linux/macOS
./mpf-scraper-linux

# Windows
mpf-scraper-windows.exe
```

### Using Python Script - Combined JSON Output (All Languages)

To get data from all three languages in a single JSON file:

```bash
# Uses default output file: processed_data.json
python mpf_scrape_json.py

# Or specify custom output file
python mpf_scrape_json.py output.json
```

The output JSON contains:
- `data_update_date`: Latest data update date from MPFA
- `table_data`: Array of fund records from all languages
- `columns`: List of column names
- `available_languages`: List of available languages

Each record in `table_data` has a `_language` field with value `"english"`, `"traditional_chinese"`, or `"simplified_chinese"`.

### CSV/Excel Output (Single Language)

### Basic usage (prints to console):

```bash
# English (default)
python mpf_scrape.py

# Traditional Chinese
python mpf_scrape.py --lang zh

# Simplified Chinese
python mpf_scrape.py --lang cn
```

### Save to CSV:

```bash
python mpf_scrape.py --lang en mpf_funds.csv
python mpf_scrape.py --lang zh mpf_funds_zh.csv
python mpf_scrape.py --lang cn mpf_funds_cn.csv
```

### Save to both CSV and Excel:

```bash
python mpf_scrape.py --lang en mpf_funds.csv mpf_funds.xlsx
```

### Command-line options:

```bash
python mpf_scrape.py --help
```

**Options:**
- `--lang` or `-l`: Language to scrape (choices: `zh`, `cn`, `en`, default: `en`)
  - `zh` = Traditional Chinese (繁體中文)
  - `cn` = Simplified Chinese (简体中文)
  - `en` = English
- First positional argument: CSV output file path (optional)
- Second positional argument: Excel output file path (optional)

## Output Format

### Combined JSON Format

The `mpf_scrape_json.py` script produces a JSON file with the following structure:

```json
{
  "data_update_date": "Latest information as of 30 Nov 2025",
  "table_data": [
    {
      "Scheme": "AIA MPF - Prime Value Choice",
      "Constituent Fund": "Age 65 Plus Fund",
      "MPF Trustee": "AIAT",
      "Fund Type": "Mixed Assets Fund - Default Investment Strategy - Age 65 Plus Fund",
      "Launch Date": "01-04-2017",
      "Fund size (HKD' m)": "2,496.08",
      "Risk Class": "4",
      "Latest FER (%)": "0.78633",
      "Calendar Year Return (%)\n-  2024": "3.09",
      "Calendar Year Return (%)\n-  2023": "7.10",
      "Calendar Year Return (%)\n-  2022": "-14.78",
      "Calendar Year Return (%)\n-  2021": "0.89",
      "Calendar Year Return (%)\n-  2020": "8.12",
      "_language": "english"
    },
    {
      "Scheme": "友邦強積金優選計劃",
      "Constituent Fund": "65歲後基金",
      "MPF Trustee": "友邦信託",
      ...
      "_language": "traditional_chinese"
    },
    {
      "Scheme": "友邦强积金优选计划",
      "Constituent Fund": "65岁后基金",
      ...
      "_language": "simplified_chinese"
    }
  ],
  "columns": [
    "Scheme",
    "Constituent Fund",
    "MPF Trustee",
    "Fund Type",
    "Launch Date",
    "Fund size (HKD' m)",
    "Risk Class",
    "Latest FER (%)",
    "Calendar Year Return (%)\n-  2024",
    "Calendar Year Return (%)\n-  2023",
    "Calendar Year Return (%)\n-  2022",
    "Calendar Year Return (%)\n-  2021",
    "Calendar Year Return (%)\n-  2020"
  ],
  "available_languages": [
    "english",
    "traditional_chinese",
    "simplified_chinese"
  ]
}
```

### CSV/Excel Format

The single-language scraper (`mpf_scrape.py`) produces a clean CSV/Excel file with 19 columns:

1. **Scheme** - MPF scheme name
2. **Constituent Fund** - Fund name
3. **MPF Trustee** - Trustee managing the fund
4. **Fund Type** - Category of fund (e.g., Equity Fund, Bond Fund, Mixed Assets Fund)
5. **Launch Date** - Fund launch date
6. **Fund Size (HKD'm)** - Fund size in millions of HKD
7. **Risk Class** - Risk rating (1-7)
8. **FER (%)** - Fund Expense Ratio percentage
9. **Annualized Return (% p.a.) - 1 Year** - 1-year annualized return
10. **Cumulative Return (%) - 1 Year** - 1-year cumulative return
11. **Calendar Year Return (%) - 2024** - Calendar year 2024 return
12. **Calendar Year Return (%) - 2023** - Calendar year 2023 return
13. **Annualized Return (% p.a.) - 5 Year** - 5-year annualized return
14. **Cumulative Return (%) - 5 Year** - 5-year cumulative return
15. **Annualized Return (% p.a.) - 10 Year** - 10-year annualized return
16. **Cumulative Return (%) - 10 Year** - 10-year cumulative return
17. **Annualized Return (% p.a.) - Since Launch** - Since launch annualized return
18. **Cumulative Return (%) - Since Launch** - Since launch cumulative return
19. **Details** - Additional details link (if available)

## Data Source

Data is scraped from the official MPFA (Mandatory Provident Fund Schemes Authority) website:
- **English**: https://mfp.mpfa.org.hk/eng/mpp_list.jsp
- **Traditional Chinese**: https://mfp.mpfa.org.hk/tch/mpp_list.jsp
- **Simplified Chinese**: https://mfp.mpfa.org.hk/sch/mpp_list.jsp
- Data as of: 30 Nov 2025 (check the output for current date)

## Technical Details

### How it works

1. **Select Language**: Choose from English (en), Traditional Chinese (zh), or Simplified Chinese (cn)
2. **Fetch HTML**: Uses `requests` with browser-like headers to fetch the page
3. **Parse Table**: Uses `pandas.read_html()` to parse the complex HTML table structure
4. **Handle Multi-level Headers**: The table has 3-level headers with colspan/rowspan attributes
5. **Detect Column Headers**: Recognizes column names in all three languages
6. **Remove Duplicates**: Identifies and removes duplicate columns caused by HTML colspan
7. **Label Columns**: Applies clear, descriptive English column names (regardless of source language)
8. **Extract Date**: Uses BeautifulSoup to find the "Latest information as of" date
9. **Export**: Saves to CSV or Excel format

### Key Functions

- `fetch_html(url)`: Fetches page HTML with retry logic
- `extract_update_date(html)`: Extracts the data update date
- `parse_main_table(html)`: Parses the main fund table and cleans columns
- `main()`: Orchestrates the scraping process

## Example Output

### English version:
```
=== Scraping from EN version ===
URL: https://mfp.mpfa.org.hk/eng/mpp_list.jsp

=== Latest data update date ===
30 Nov 2025
(ISO) 2025-11-30

=== Table preview (first 10 rows) ===
                         Scheme  Constituent Fund MPF Trustee  ...
0  AIA MPF - Prime Value Choice  Age 65 Plus Fund        AIAT  ...
1  AIA MPF - Prime Value Choice     American Fund        AIAT  ...
...

Saved CSV to: mpf_funds.csv
```

### Traditional Chinese version:
```
=== Scraping from ZH version ===
URL: https://mfp.mpfa.org.hk/tch/mpp_list.jsp

=== Latest data update date ===
2025年11月30日

=== Table preview (first 10 rows) ===
      Scheme Constituent Fund MPF Trustee  ...
0  友邦強積金優選計劃           65歲後基金       友邦信託  ...
1  友邦強積金優選計劃             美洲基金       友邦信託  ...
...

Saved CSV to: mpf_funds_zh.csv
```

## Notes

- The scraper includes retry logic with exponential backoff for robustness
- **All output files use English column headers** regardless of the source language for consistency
- The actual fund names, scheme names, and other data content will be in the language of the selected source
- Columns with "n.a." values indicate data not available for that time period
- All return percentages are as reported by MPFA
- The script handles both English and Chinese date formats

## License

This is a data scraping utility. Please respect the MPFA website's terms of service and use responsibly.
