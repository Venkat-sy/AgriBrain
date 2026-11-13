import pandas as pd
import geopandas as gpd

df = pd.read_pickle('temp_annual.pkl')
print(f'Shape: {df.shape}')
print(f'Districts: {df["district_name"].nunique()}')
print(f'Years: {sorted(df["year"].unique())}')
print(f'Sources: {df["source"].unique()}')

# Check which canonical districts are missing
districts = gpd.read_file('india_districts.geojson')
districts['canonical_key'] = districts['district_name'].str.strip().str.upper() + '_' + districts['state_name'].str.strip().str.upper()
canonical_keys = set(districts['canonical_key'].values)

rainfall_districts = set()
for _, row in df.iterrows():
    key = row['district_name'].strip().upper() + '_' + row['state_name'].strip().upper()
    rainfall_districts.add(key)

missing = canonical_keys - rainfall_districts
print(f'\nMissing districts from rainfall: {len(missing)}')
for m in sorted(missing):
    print(f'  {m}')