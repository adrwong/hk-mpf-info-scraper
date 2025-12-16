import requests
import pandas as pd
from io import StringIO

def test_url(url, lang):
    print(f"\n{'='*60}")
    print(f"Testing {lang} - {url}")
    print('='*60)
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    resp = requests.get(url, headers=headers, timeout=30)
    resp.encoding = resp.apparent_encoding or "utf-8"
    html = resp.text
    
    tables = pd.read_html(StringIO(html), flavor="lxml")
    print(f"Found {len(tables)} tables")
    
    if tables:
        df = max(tables, key=lambda t: len(t))
        print(f"\nMain table shape: {df.shape}")
        print(f"\nColumn structure (all columns):")
        for i, col in enumerate(df.columns):
            level_0, level_1, level_2 = col
            print(f"{i}: L0={level_0} | L1={level_1} | L2={level_2}")

# Test all three languages
test_url("https://mfp.mpfa.org.hk/eng/mpp_list.jsp", "English")
test_url("https://mfp.mpfa.org.hk/tch/mpp_list.jsp", "Traditional Chinese")
test_url("https://mfp.mpfa.org.hk/sch/mpp_list.jsp", "Simplified Chinese")
