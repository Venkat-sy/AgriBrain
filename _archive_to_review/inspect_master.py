import pandas as pd

df = pd.read_csv('master_agri_dataset.csv')
print(f'Records: {len(df)}')
print(f'Columns: {df.columns.tolist()}')
if 'district_name' in df.columns:
    print(f'Districts: {df["district_name"].nunique()}')
if 'crop' in df.columns:
    print(f'Crops: {df["crop"].nunique()}')
    print(f'Crop list: {sorted(df["crop"].unique())}')
if 'year' in df.columns:
    print(f'Years: {sorted(df["year"].unique())}')
print()
print('Sample:')
print(df.head(5).to_string())