
import re
import sys
import time
from datetime import datetime
from typing import Optional

import pandas as pd
import requests
from bs4 import BeautifulSoup

URL = "https://mfp.mpfa.org.hk/eng/mpp_list.jsp"

def fetch_html(url: str, timeout: int = 30, max_retries: int = 3) -> str:
    """Fetch page HTML with a browser-like User-Agent and basic retries."""
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0 Safari/537.36"
        )
    }
    last_exc = None
    for attempt in range(1, max_retries + 1):
        try:
            resp = requests.get(url, headers=headers, timeout=timeout)
            resp.raise_for_status()
            resp.encoding = resp.apparent_encoding or "utf-8"
            return resp.text
        except Exception as exc:
            last_exc = exc
            time.sleep(1.5 * attempt)  # backoff
    raise RuntimeError(f"Failed to fetch HTML after {max_retries} attempts: {last_exc}")

def extract_update_date(html: str) -> Optional[str]:
    """
    Extracts the 'Latest information as of ...' date text.
    Returns the raw date string (e.g., '31 Oct 2025') or None if not found.
    """
    soup = BeautifulSoup(html, "lxml")

    # Strategy 1: look for an element containing the phrase
    PHRASES = [
        "Latest information as of",
        "最新資料截至",   # Traditional Chinese (fallback)
    ]
    text_candidates = []

    # Collect text from common containers
    for tag in soup.find_all(string=True):
        t = tag.strip()
        if not t:
            continue
        if any(p.lower() in t.lower() for p in PHRASES):
            text_candidates.append(t)

    # If found, parse with regex to isolate the date portion
    for t in text_candidates:
        # English date like '31 Oct 2025' or '31 October 2025'
        m_en = re.search(r"Latest information as of\s*:\s*(\d{1,2}\s+[A-Za-z]+(?:[a-z]+)?\s+\d{4})", t, re.IGNORECASE)
        if m_en:
            return m_en.group(1).strip()

        # Another common English pattern without colon
        m_en2 = re.search(r"Latest information as of\s*(\d{1,2}\s+[A-Za-z]+(?:[a-z]+)?\s+\d{4})", t, re.IGNORECASE)
        if m_en2:
            return m_en2.group(1).strip()

        # Chinese pattern example: '最新資料截至 2025年10月31日'
        m_zh = re.search(r"最新資料截至[:：]?\s*(\d{4}年\d{1,2}月\d{1,2}日)", t)
        if m_zh:
            return m_zh.group(1).strip()

    # Strategy 2: fallback—search the raw HTML text
    m_raw = re.search(r"Latest information as of[^<]*?(\d{1,2}\s+[A-Za-z]+(?:[a-z]+)?\s+\d{4})", html, re.IGNORECASE)
    if m_raw:
        return m_raw.group(1).strip()

    return None

def parse_main_table(html: str) -> pd.DataFrame:
    """
    Parse the fund information table with multi-level headers.
    The page is server-rendered (JSP), so pandas.read_html should work.
    Returns a DataFrame with cleaned, properly labeled columns and no duplicates.
    """
    from io import StringIO
    
    # read_html returns a list of DataFrames
    tables = pd.read_html(StringIO(html), flavor="lxml")
    if not tables:
        raise ValueError("No HTML tables were found on the page.")

    # Find the table with the most rows (main data table)
    df = max(tables, key=lambda t: len(t))
    
    # The table has 3-level MultiIndex columns due to HTML colspan/rowspan
    # We need to identify which columns are the "real" data columns vs duplicates
    
    columns_to_keep = []
    column_names = []
    seen_return_periods = {}  # Track which return period columns we've already added
    
    for idx, col_tuple in enumerate(df.columns):
        level_0, level_1, level_2 = col_tuple
        
        # Clean up the strings
        level_0 = str(level_0).strip()
        level_1 = str(level_1).strip()
        level_2 = str(level_2).strip()
        
        # Strategy: Keep columns where level_1 or level_2 has meaningful names
        # Skip unnamed spacer columns
        
        # Skip columns that are all unnamed (spacers)
        if 'Unnamed' in level_0 and 'Unnamed' in level_1 and 'Unnamed' in level_2:
            continue
        
        # For basic info columns, keep the one with proper label in level_1
        if 'Scheme' in level_1:
            columns_to_keep.append(idx)
            column_names.append('Scheme')
        elif 'Constituent' in level_1 and 'Fund' in level_1:
            columns_to_keep.append(idx)
            column_names.append('Constituent Fund')
        elif 'MPF Trustee' in level_1 or 'MPFTrustee' in level_1:
            columns_to_keep.append(idx)
            column_names.append('MPF Trustee')
        elif 'Fund  Type' in level_1 or 'Fund Type' in level_1:
            columns_to_keep.append(idx)
            column_names.append('Fund Type')
        elif 'Launch Date' in level_1:
            columns_to_keep.append(idx)
            column_names.append('Launch Date')
        elif "Fund size (HKD' m)" in level_1:
            columns_to_keep.append(idx)
            column_names.append("Fund Size (HKD'm)")
        elif 'Risk  Class' in level_1 or 'Risk Class' in level_1:
            columns_to_keep.append(idx)
            column_names.append('Risk Class')
        elif 'Latest FER' in level_1:
            columns_to_keep.append(idx)
            column_names.append('FER (%)')
        elif 'Details' in level_1:
            columns_to_keep.append(idx)
            column_names.append('Details')
        
        # For return columns, we need to identify them by time period
        # The key is that Pandas adds .1, .2, .3 suffixes to duplicate column names
        # Due to HTML colspan, there are true duplicates - we only want the FIRST of each type
        
        elif '1 Year' in level_2:
            if '.1' not in level_2 and '.2' not in level_2 and '.3' not in level_2:
                # First occurrence - Annualized Return
                if '1Y_ann' not in seen_return_periods:
                    columns_to_keep.append(idx)
                    column_names.append('Annualized Return (% p.a.) - 1 Year')
                    seen_return_periods['1Y_ann'] = True
            elif level_2 == '1 Year.1':
                # Second occurrence - Cumulative Return
                if '1Y_cum' not in seen_return_periods:
                    columns_to_keep.append(idx)
                    column_names.append('Cumulative Return (%) - 1 Year')
                    seen_return_periods['1Y_cum'] = True
            elif level_2 == '1 Year.2':
                # Third - Calendar Year 2024
                if '1Y_cy2024' not in seen_return_periods:
                    columns_to_keep.append(idx)
                    column_names.append('Calendar Year Return (%) - 2024')
                    seen_return_periods['1Y_cy2024'] = True
            elif level_2 == '1 Year.3':
                # Fourth - Calendar Year 2023
                if '1Y_cy2023' not in seen_return_periods:
                    columns_to_keep.append(idx)
                    column_names.append('Calendar Year Return (%) - 2023')
                    seen_return_periods['1Y_cy2023'] = True
                
        elif '5 Year' in level_2:
            if level_2 == '5 Year' and '5Y_ann' not in seen_return_periods:
                # First occurrence - Annualized Return
                columns_to_keep.append(idx)
                column_names.append('Annualized Return (% p.a.) - 5 Year')
                seen_return_periods['5Y_ann'] = True
            elif level_2 == '5 Year.1' and '5Y_cum' not in seen_return_periods:
                # Second occurrence - Cumulative Return
                columns_to_keep.append(idx)
                column_names.append('Cumulative Return (%) - 5 Year')
                seen_return_periods['5Y_cum'] = True
                
        elif '10 Year' in level_2:
            # All 10 Year columns are duplicates due to colspan, keep only first two
            if '10Y_ann' not in seen_return_periods:
                columns_to_keep.append(idx)
                column_names.append('Annualized Return (% p.a.) - 10 Year')
                seen_return_periods['10Y_ann'] = True
            elif '10Y_cum' not in seen_return_periods:
                # Second unique one is cumulative
                columns_to_keep.append(idx)
                column_names.append('Cumulative Return (%) - 10 Year')
                seen_return_periods['10Y_cum'] = True
                
        elif 'Since' in level_2 and 'Launch' in level_2:
            # All Since Launch columns are duplicates due to colspan, keep only first two
            if 'SL_ann' not in seen_return_periods:
                columns_to_keep.append(idx)
                column_names.append('Annualized Return (% p.a.) - Since Launch')
                seen_return_periods['SL_ann'] = True
            elif 'SL_cum' not in seen_return_periods:
                columns_to_keep.append(idx)
                column_names.append('Cumulative Return (%) - Since Launch')
                seen_return_periods['SL_cum'] = True
    
    # Select only the columns we want to keep
    df_clean = df.iloc[:, columns_to_keep].copy()
    df_clean.columns = column_names
    
    # Drop rows that are completely empty
    df_clean = df_clean.dropna(how='all')
    
    # Reset index
    df_clean = df_clean.reset_index(drop=True)
    
    return df_clean

def main(save_to_csv: Optional[str] = None, save_to_excel: Optional[str] = None):
    html = fetch_html(URL)
    update_date_raw = extract_update_date(html)
    df = parse_main_table(html)

    print("\n=== Latest data update date ===")
    if update_date_raw:
        print(update_date_raw)
        # Optional: try to normalize to ISO date if it's English
        try:
            dt = datetime.strptime(update_date_raw, "%d %b %Y")
            print(f"(ISO) {dt.date().isoformat()}")
        except Exception:
            # Could be Chinese format or full month name; keep raw.
            pass
    else:
        print("Not found")

    print("\n=== Table preview (first 10 rows) ===")
    print(df.head(10))

    # Save outputs if requested
    if save_to_csv:
        df.to_csv(save_to_csv, index=False, encoding="utf-8-sig")
        print(f"\nSaved CSV to: {save_to_csv}")
    if save_to_excel:
        # Use openpyxl engine explicitly if you prefer (requires openpyxl installed)
        df.to_excel(save_to_excel, index=False, engine="openpyxl")
        print(f"Saved Excel to: {save_to_excel}")

if __name__ == "__main__":
    # Optional: pass output file names via CLI args
    # Example: python script.py funds.csv funds.xlsx
    csv_path = sys.argv[1] if len(sys.argv) > 1 else None
    xlsx_path = sys.argv[2] if len(sys.argv) > 2 else None
    main(save_to_csv=csv_path, save_to_excel=xlsx_path)
