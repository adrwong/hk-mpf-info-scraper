from mpf_scrape import fetch_html
import pandas as pd
from io import StringIO

html = fetch_html('https://mfp.mpfa.org.hk/eng/mpp_list.jsp')
dfs = pd.read_html(StringIO(html))
df = dfs[5]

# Check a different row - maybe row 10
print('Checking row 10 for 10 Year columns:')
for idx, col in enumerate(df.columns):
    if '10 Year' in str(col[2]):
        print(f'{idx}: {col[2]}')
        print(f'   Row 0: {df.iloc[0, idx]}, Row 10: {df.iloc[10, idx]}')

print('\n\nChecking row 10 for Since Launch columns:')
for idx, col in enumerate(df.columns):
    if 'Since' in str(col[2]) and 'Launch' in str(col[2]):
        print(f'{idx}: {col[2]}')
        print(f'   Row 0: {df.iloc[0, idx]}, Row 10: {df.iloc[10, idx]}')

# Let's also check if values are actually different across columns in any row
print('\n\nChecking if 10 Year columns have different values anywhere:')
cols_10y = [idx for idx, col in enumerate(df.columns) if '10 Year' in str(col[2])]
for row_idx in range(min(20, len(df))):
    values = [df.iloc[row_idx, col] for col in cols_10y]
    if len(set(str(v) for v in values)) > 1:
        print(f'Row {row_idx}: {values}')
        break
else:
    print('All rows have identical values across 10 Year columns - these are TRUE duplicates from colspan!')

print('\n\nChecking if Since Launch columns have different values anywhere:')
cols_sl = [idx for idx, col in enumerate(df.columns) if 'Since' in str(col[2]) and 'Launch' in str(col[2])]
for row_idx in range(min(20, len(df))):
    values = [df.iloc[row_idx, col] for col in cols_sl]
    if len(set(str(v) for v in values)) > 1:
        print(f'Row {row_idx}: {values}')
        break
else:
    print('All rows have identical values across Since Launch columns - these are TRUE duplicates from colspan!')
