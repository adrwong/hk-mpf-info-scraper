from mpf_scrape import fetch_html
from bs4 import BeautifulSoup
import pandas as pd

html = fetch_html('https://mfp.mpfa.org.hk/eng/mpp_list.jsp')
soup = BeautifulSoup(html, 'lxml')
tables = soup.find_all('table')
print(f'Found {len(tables)} tables')

for table_idx, table in enumerate(tables):
    rows = table.find_all('tr')
    print(f'\n=== Table {table_idx}: {len(rows)} rows ===')
    
    if len(rows) > 50:  # This is likely the main data table
        print(f'This looks like the main table!')
        # Print first few rows to understand structure
        for i, row in enumerate(rows[:10]):
            cells = row.find_all(['th', 'td'])
            print(f'\nRow {i}: {len(cells)} cells')
            for j, cell in enumerate(cells[:10]):
                rowspan = cell.get('rowspan', 1)
                colspan = cell.get('colspan', 1)
                text = cell.get_text(strip=True)
                print(f'  Cell {j}: rowspan={rowspan}, colspan={colspan}, text="{text[:50]}"')
        break

# Also try pandas
print('\n\n=== Pandas read_html ===')
from io import StringIO
dfs = pd.read_html(StringIO(html))
print(f'Found {len(dfs)} dataframes')
for i, df in enumerate(dfs):
    print(f'\nDataFrame {i}: Shape {df.shape}')
    if df.shape[0] > 100:  # Likely the main table
        print('This looks like the main data table!')
        print(f'Columns: {df.columns.tolist()[:10]}')
        print(f'First row sample:')
        print(df.iloc[0, :10])
