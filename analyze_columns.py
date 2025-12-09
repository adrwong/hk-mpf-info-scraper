from mpf_scrape import fetch_html
from bs4 import BeautifulSoup
import pandas as pd
from io import StringIO

html = fetch_html('https://mfp.mpfa.org.hk/eng/mpp_list.jsp')
dfs = pd.read_html(StringIO(html))

# Get the main table (DataFrame 5)
df = dfs[5]

print(f'Shape: {df.shape}')
print(f'\nAll column names:')
for i, col in enumerate(df.columns):
    print(f'{i}: {col}')

print(f'\n\nFirst row data:')
for i, (col, val) in enumerate(df.iloc[0].items()):
    print(f'{i}: {col} = {val}')
