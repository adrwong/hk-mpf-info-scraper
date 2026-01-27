#!/usr/bin/env python3
"""
MPF Fund Data Scraper - JSON Output Version
Scrapes data from all three languages and outputs combined JSON.
"""

import argparse
import json
import re
import sys
import time
from datetime import datetime
from io import StringIO
from typing import Optional, Dict, List, Tuple

import pandas as pd
import requests
from bs4 import BeautifulSoup

# Language-specific URLs
URLS = {
    "zh": "https://mfp.mpfa.org.hk/tch/mpp_list.jsp",  # Traditional Chinese
    "cn": "https://mfp.mpfa.org.hk/sch/mpp_list.jsp",  # Simplified Chinese
    "en": "https://mfp.mpfa.org.hk/eng/mpp_list.jsp",  # English
}

LANGUAGE_LABELS = {
    "en": "english",
    "zh": "traditional_chinese",
    "cn": "simplified_chinese",
}

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
    Supports English, Traditional Chinese, and Simplified Chinese.
    Returns a DataFrame with cleaned, properly labeled columns and no duplicates.
    """
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
        # Multi-language support: en/zh/cn
        if 'Scheme' in level_1 or level_1 == '計劃' or level_1 == '计划':
            columns_to_keep.append(idx)
            column_names.append('Scheme')
        elif ('Constituent' in level_1 and 'Fund' in level_1) or level_1 == '成分基金':
            columns_to_keep.append(idx)
            column_names.append('Constituent Fund')
        elif 'MPF Trustee' in level_1 or 'MPFTrustee' in level_1 or level_1 == '受託人' or level_1 == '受托人':
            columns_to_keep.append(idx)
            column_names.append('MPF Trustee')
        elif 'Fund  Type' in level_1 or 'Fund Type' in level_1 or level_1 == '基金類別' or level_1 == '基金类别':
            columns_to_keep.append(idx)
            column_names.append('Fund Type')
        elif 'Launch Date' in level_1 or level_1 == '推出日期':
            columns_to_keep.append(idx)
            column_names.append('Launch Date')
        elif "Fund size (HKD' m)" in level_1 or '基金規模' in level_1 or '基金规模' in level_1:
            columns_to_keep.append(idx)
            column_names.append("Fund size (HKD' m)")
        elif 'Risk  Class' in level_1 or 'Risk Class' in level_1 or level_1 == '風險級別' or level_1 == '风险级别':
            columns_to_keep.append(idx)
            column_names.append('Risk Class')
        elif 'Latest FER' in level_1 or '最近期基金' in level_1 or '開支比率' in level_1 or '开支比率' in level_1:
            columns_to_keep.append(idx)
            column_names.append('Latest FER (%)')
        elif 'Details' in level_1 or level_1 == '詳細內容' or level_1 == '详细内容':
            columns_to_keep.append(idx)
            column_names.append('Details')
        
        # For Calendar Year returns, we look at level_0 which contains year info
        # Check if this is a calendar year column (2024, 2023, 2022, 2021, 2020)
        elif any(year in level_0 for year in ['2024', '2023', '2022', '2021', '2020']):
            # Extract the year from level_0
            year_match = re.search(r'(202[0-4])', level_0)
            if year_match:
                year = year_match.group(1)
                col_key = f'CY_{year}'
                if col_key not in seen_return_periods:
                    columns_to_keep.append(idx)
                    column_names.append(f'Calendar Year Return (%)\n-  {year}')
                    seen_return_periods[col_key] = True
    
    # Select only the columns we want to keep
    df_clean = df.iloc[:, columns_to_keep].copy()
    df_clean.columns = column_names
    
    # Drop rows that are completely empty
    df_clean = df_clean.dropna(how='all')
    
    # Reset index
    df_clean = df_clean.reset_index(drop=True)
    
    return df_clean

def scrape_language(language: str) -> Tuple[pd.DataFrame, str]:
    """
    Scrape data for a single language.
    Returns (dataframe, update_date)
    """
    url = URLS.get(language.lower(), URLS["en"])
    print(f"Scraping {LANGUAGE_LABELS[language]} from {url}...")
    
    html = fetch_html(url)
    update_date_raw = extract_update_date(html)
    df = parse_main_table(html)
    
    # Add language column
    df['_language'] = LANGUAGE_LABELS[language]
    
    return df, update_date_raw

def combine_all_languages() -> Dict:
    """
    Scrape all three languages and combine into a single data structure.
    Returns a dictionary matching the desired output format.
    """
    all_data = []
    update_date = None
    
    # Scrape all three languages
    for lang in ['en', 'zh', 'cn']:
        try:
            df, date_str = scrape_language(lang)
            
            # Use the English version's update date
            if lang == 'en' and date_str:
                update_date = f"Latest information as of {date_str}"
            
            # Convert DataFrame to list of dictionaries
            records = df.to_dict('records')
            all_data.extend(records)
            
            print(f"✓ Successfully scraped {len(df)} records from {LANGUAGE_LABELS[lang]}")
        except Exception as e:
            print(f"✗ Error scraping {LANGUAGE_LABELS[lang]}: {e}", file=sys.stderr)
            # Continue with other languages even if one fails
    
    # Get column names (excluding _language)
    if all_data:
        # Get all unique columns and sort them, with _language last
        all_columns = set()
        for record in all_data:
            all_columns.update(record.keys())
        
        # Remove _language from columns list
        all_columns.discard('_language')
        columns = sorted(all_columns)
    else:
        columns = []
    
    return {
        "data_update_date": update_date or "Unknown",
        "table_data": all_data,
        "columns": columns,
        "available_languages": ["english", "traditional_chinese", "simplified_chinese"]
    }

def main(output_file: str = "processed_data.json"):
    """
    Main function to scrape MPF fund data from all languages and output combined JSON.
    
    Args:
        output_file: Path to save JSON output (default: processed_data.json)
    """
    print("\n=== MPF Fund Data Scraper - Multi-language JSON Output ===\n")
    
    # Scrape all languages and combine
    combined_data = combine_all_languages()
    
    # Save to JSON file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(combined_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✓ Successfully saved combined data to: {output_file}")
    print(f"  Total records: {len(combined_data['table_data'])}")
    print(f"  Columns: {len(combined_data['columns'])}")
    print(f"  Languages: {', '.join(combined_data['available_languages'])}")
    print(f"  Data update date: {combined_data['data_update_date']}\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Scrape MPF fund information from all languages and output combined JSON",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python mpf_scrape_json.py                          # Output to processed_data.json
  python mpf_scrape_json.py output.json              # Output to custom file
        """
    )
    
    parser.add_argument(
        "output",
        nargs="?",
        default="processed_data.json",
        help="Output JSON file path (default: processed_data.json)"
    )
    
    args = parser.parse_args()
    
    main(output_file=args.output)
