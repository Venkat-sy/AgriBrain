import pandas as pd
rainfall = pd.read_pickle('temp_annual.pkl')
rainfall['canonical_key'] = rainfall['district_name'].str.strip().str.upper() + '_' + rainfall['state_name'].str.strip().str.upper()
rainfall_annual = rainfall.groupby(['canonical_key', 'year', 'source'])['annual_rainfall_mm'].sum().reset_index()
print(f'Rainfall annual: {rainfall_annual.shape}')
print(f'Rainfall years: {sorted(rainfall_annual["year"].unique())}')
print(f'Rainfall sample canonical_keys: {rainfall_annual["canonical_key"].unique()[:5]}')
print(f'Rainfall sources: {rainfall_annual["source"].unique()}')

# Check master grid canonical keys
master = pd.read_pickle('temp_master_grid.pkl')
print(f'\nMaster sample canonical_keys: {master["canonical_key"].unique()[:5]}')
print(f'Master years: {sorted(master["year"].unique())}')

# Check overlap
rain_keys = set(rainfall_annual['canonical_key'].unique())
master_keys = set(master['canonical_key'].unique())
print(f'\nOverlap keys: {len(rain_keys & master_keys)}')