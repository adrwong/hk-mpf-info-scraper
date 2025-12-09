# MPF Fund Data Scraper

A Python scraper for extracting Mandatory Provident Fund (MPF) data from the MPFA website.

## Features

- Scrapes comprehensive MPF fund information from https://mfp.mpfa.org.hk/eng/mpp_list.jsp
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

## Requirements

```
pandas
requests
beautifulsoup4
lxml
openpyxl (optional, for Excel export)
```

## Installation

Install dependencies using uv:

```bash
uv pip install pandas requests beautifulsoup4 lxml openpyxl
```

## Usage

### Basic usage (prints to console):

```bash
python mpf_scrape.py
```

### Save to CSV:

```bash
python mpf_scrape.py mpf_funds.csv
```

### Save to both CSV and Excel:

```bash
python mpf_scrape.py mpf_funds.csv mpf_funds.xlsx
```

## Output Format

The scraper produces a clean CSV/Excel file with 19 columns:

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
- URL: https://mfp.mpfa.org.hk/eng/mpp_list.jsp
- Data as of: 31 Oct 2025 (check the output for current date)

## Technical Details

### How it works

1. **Fetch HTML**: Uses `requests` with browser-like headers to fetch the page
2. **Parse Table**: Uses `pandas.read_html()` to parse the complex HTML table structure
3. **Handle Multi-level Headers**: The table has 3-level headers with colspan/rowspan attributes
4. **Remove Duplicates**: Identifies and removes duplicate columns caused by HTML colspan
5. **Label Columns**: Applies clear, descriptive column names
6. **Extract Date**: Uses BeautifulSoup to find the "Latest information as of" date
7. **Export**: Saves to CSV or Excel format

### Key Functions

- `fetch_html(url)`: Fetches page HTML with retry logic
- `extract_update_date(html)`: Extracts the data update date
- `parse_main_table(html)`: Parses the main fund table and cleans columns
- `main()`: Orchestrates the scraping process

## Example Output

```
=== Latest data update date ===
31 Oct 2025
(ISO) 2025-10-31

=== Table preview (first 10 rows) ===
                          Scheme  Constituent Fund MPF Trustee  ...
0  AIA MPF - Prime Value Choice  Age 65 Plus Fund        AIAT  ...
1  AIA MPF - Prime Value Choice     American Fund        AIAT  ...
...

Saved CSV to: mpf_funds.csv
```

## Notes

- The scraper includes retry logic with exponential backoff for robustness
- Columns with "n.a." values indicate data not available for that time period
- All return percentages are as reported by MPFA
- The script handles both English and Chinese date formats

## License

This is a data scraping utility. Please respect the MPFA website's terms of service and use responsibly.
