import pandas as pd
import json

# Load existing crop data
prod = pd.read_csv('raw/crop_production_district.csv')
yield_df = pd.read_csv('raw/crop_yield_district.csv')

print('=== PRODUCTION DATA ===')
print(f'Records: {len(prod)}')
print(f'Districts: {prod["DISTRICT"].nunique()}')
print(f'States: {prod["STATE"].nunique()}')
print(f'Crops: {prod["CROP"].nunique()}')
print(f'Crops list: {sorted(prod["CROP"].unique())}')
print(f'Years: {sorted(prod["YEAR"].unique())}')
print(f'Year range: {prod["YEAR"].min()}-{prod["YEAR"].max()}')
print()

print('=== YIELD DATA ===')
print(f'Records: {len(yield_df)}')
print(f'Districts: {yield_df["DISTRICT"].nunique()}')
print(f'States: {yield_df["STATE"].nunique()}')
print(f'Crops: {yield_df["CROP"].nunique()}')
print(f'Crops list: {sorted(yield_df["CROP"].unique())}')
print(f'Years: {sorted(yield_df["YEAR"].unique())}')
print(f'Year range: {yield_df["YEAR"].min()}-{yield_df["YEAR"].max()}')
print()

# Load canonical versions
prod_c = pd.read_csv('raw/crop_production_district_canonical.csv')
yield_c = pd.read_csv('raw/crop_yield_district_canonical.csv')

print('=== CANONICAL PRODUCTION DATA ===')
print(f'Records: {len(prod_c)}')
print(f'Districts: {prod_c["district_name"].nunique()}')
print(f'States: {prod_c["state_name"].nunique()}')
print(f'Crops: {prod_c["crop"].nunique()}')
print(f'Years: {sorted(prod_c["year"].unique())}')
print(f'Year range: {prod_c["year"].min()}-{prod_c["year"].max()}')
print(f'Has district_id: {"district_id" in prod_c.columns}')
print()

print('=== CANONICAL YIELD DATA ===')
print(f'Records: {len(yield_c)}')
print(f'Districts: {yield_c["district_name"].nunique()}')
print(f'States: {yield_c["state_name"].nunique()}')
print(f'Crops: {yield_c["crop"].nunique()}')
print(f'Years: {sorted(yield_c["year"].unique())}')
print(f'Year range: {yield_c["year"].min()}-{yield_c["year"].max()}')
print()

# Check columns
print('=== COLUMNS ===')
print(f'Production columns: {prod.columns.tolist()}')
print(f'Yield columns: {yield_df.columns.tolist()}')
print(f'Canonical production columns: {prod_c.columns.tolist()}')
print(f'Canonical yield columns: {yield_c.columns.tolist()}')
print()

# Check for NaN values
print('=== NaN COUNTS ===')
print('Production:')
print(prod.isnull().sum())
print()
print('Yield:')
print(yield_df.isnull().sum())
print()

# Check production vs yield relationship
print('=== YIELD CALCULATION CHECK ===')
for i in range(min(10, len(prod))):
    row = prod.iloc[i]
    calc_yield = row['PRODUCTION_TONNES'] / row['AREA_HA'] if row['AREA_HA'] > 0 else 0
    diff = abs(row['YIELD_TONNES_PER_HA'] - calc_yield)
    if diff > 0.001:
        print(f'  MISMATCH: {row["CROP"]} {row["YEAR"]}: given={row["YIELD_TONNES_PER_HA"]:.3f}, calc={calc_yield:.3f}, diff={diff:.3f}')
    else:
        print(f'  OK: {row["CROP"]} {row["YEAR"]}: {row["YIELD_TONNES_PER_HA"]:.3f}')

# Check district coverage per crop
print()
print('=== DISTRICT COVERAGE PER CROP (PRODUCTION) ===')
for crop in sorted(prod['CROP'].unique()):
    crop_data = prod[prod['CROP'] == crop]
    districts = crop_data['DISTRICT'].nunique()
    states = crop_data['STATE'].nunique()
    years = crop_data['YEAR'].nunique()
    print(f'  {crop}: {districts} districts, {states} states, {years} years')

print()
print('=== DISTRICT COVERAGE PER CROP (YIELD) ===')
for crop in sorted(yield_df['CROP'].unique()):
    crop_data = yield_df[yield_df['CROP'] == crop]
    districts = crop_data['DISTRICT'].nunique()
    states = crop_data['STATE'].nunique()
    years = crop_data['YEAR'].nunique()
    print(f'  {crop}: {districts} districts, {states} states, {years} years')

# Check canonical district keys
print()
print('=== CANONICAL KEY CHECK ===')
prod_c['canonical_key'] = prod_c['district_name'].str.strip().str.upper() + '_' + prod_c['state_name'].str.strip().str.upper()
canonical_keys = set(prod_c['canonical_key'].unique())
print(f'Canonical keys in production data: {len(canonical_keys)}')

# Load district registry
import geopandas as gpd
districts = gpd.read_file('india_districts.geojson')
districts['canonical_key'] = districts['district_name'].str.strip().str.upper() + '_' + districts['state_name'].str.strip().str.upper()
registry_keys = set(districts['canonical_key'].unique())
print(f'Canonical keys in registry: {len(registry_keys)}')

matched = canonical_keys & registry_keys
unmatched = canonical_keys - registry_keys
missing = registry_keys - canonical_keys

print(f'Matched: {len(matched)}')
print(f'Unmatched (in data but not registry): {len(unmatched)}')
print(f'Missing (in registry but not data): {len(missing)}')

if unmatched:
    print(f'Sample unmatched: {sorted(list(unmatched))[:10]}')

# Year coverage per district
print()
print('=== YEAR COVERAGE SUMMARY ===')
year_coverage = prod.groupby(['DISTRICT', 'STATE'])['YEAR'].agg(['min', 'max', 'count']).reset_index()
print(f'Districts with data: {len(year_coverage)}')
print(f'Year count distribution:')
print(year_coverage['count'].value_counts().sort_index())

# Check latest 5 years
target_years = [2019, 2020, 2021, 2022, 2023]
print()
print('=== TARGET YEARS (2019-2023) AVAILABILITY ===')
for year in target_years:
    count = len(prod[prod['YEAR'] == year])
    print(f'  {year}: {count} records')

# Check crops per district
print()
print('=== CROPS PER DISTRICT ===')
crops_per_district = prod.groupby(['DISTRICT', 'STATE'])['CROP'].nunique().reset_index()
crops_per_district.columns = ['DISTRICT', 'STATE', 'num_crops']
print(crops_per_district['num_crops'].value_counts().sort_index())