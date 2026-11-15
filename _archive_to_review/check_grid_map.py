import pickle

with open('temp_district_grid_map.pkl', 'rb') as f:
    dgm = pickle.load(f)
print(f'Districts with grid cells: {len(dgm)}')
print('Sample:', list(dgm.items())[:5])

import geopandas as gpd
districts = gpd.read_file('india_districts.geojson')
print(f'\nTotal districts in GeoJSON: {len(districts)}')
if 'district_name' in districts.columns and 'state_name' in districts.columns:
    districts['canonical_key'] = districts['district_name'].str.strip().str.upper() + '_' + districts['state_name'].str.strip().str.upper()
    canonical_keys = set(districts['canonical_key'].values)
    print(f'Canonical keys in GeoJSON: {len(canonical_keys)}')
    mapped_keys = set(dgm.keys())
    missing = canonical_keys - mapped_keys
    print(f'Missing districts: {len(missing)}')
    for m in sorted(missing):
        print(f'  {m}')