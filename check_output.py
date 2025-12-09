import pandas as pd

df = pd.read_csv('mpf_funds_final.csv')
print(f'Shape: {df.shape}')
print(f'\nColumns:')
for i, col in enumerate(df.columns):
    print(f'{i+1}. {col}')

print(f'\nFirst 3 rows:')
print(df.head(3).to_string())
