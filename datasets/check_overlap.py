import pandas as pd
import geopandas as gpd

df = pd.read_csv('master_agri_dataset.csv')
print(f'Master shape: {df.shape}')
print(f'Years: {sorted(df["year"].unique())}')
print(f'Districts: {df["district_name"].nunique()}')
print(f'Crops: {df["crop"].nunique()}')
print(f'Crops: {sorted(df["crop"].unique())}')

# Check if crop data has district_name matching canonical
districts = gpd.read_file('india_districts.geojson')
districts['canonical_key'] = districts['district_name'].str.strip().str.upper() + '_' + districts['state_name'].str.strip().str.upper()
canonical_keys = set(districts['canonical_key'].values)

crop_keys = set()
for _, row in df.iterrows():
    key = row['district_name'].strip().upper() + '_' + row['state_name'].strip().upper()
    crop_keys.add(key)

missing = canonical_keys - crop_keys
print(f'\nCanonical districts missing from crop data: {len(missing)}')
# for m in sorted(missing): print(f'  {m}')

# Check which crop districts are in rainfall
rainfall_keys = set()
df_rf = pd.read_pickle('temp_annual.pkl')
for _, row in df_rf.iterrows():
    key = row['district_name'].strip().upper() + '_' + row['state_name'].strip().upper()
    rainfall_keys.add(key)

overlap = crop_keys & rainfall_keys
print(f'Districts with BOTH crop and rainfall: {len(overlap)}')
print(f'Crop-only districts: {len(crop_keys - rainfall_keys)}')
print(f'Rainfall-only districts: {len(rainfall_keys - crop_keys)}')

# Check year overlap
crop_years = set(df['year'].unique())
rainfall_years = set(df_rf['year'].unique())
print(f'\nCrop years: {sorted(crop_years)}')
print(f'Rainfall years: {sorted(rainfall_years)}')
print(f'Year overlap: {crop_years & rainfall_years}')