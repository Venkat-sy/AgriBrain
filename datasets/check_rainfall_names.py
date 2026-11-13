import pandas as pd

df = pd.read_pickle('temp_annual.pkl')
print(f'Unique district_name count: {df["district_name"].nunique()}')
print(f'Unique state_name count: {df["state_name"].nunique()}')
print('\nDistrict-state combinations (first 20):')
for d in sorted(df['district_name'].unique())[:20]:
    print(f'  {d}')