import pandas as pd
import xarray as xr
import geopandas as gpd
import numpy as np
import json
import pickle
from shapely.geometry import box
import warnings
warnings.filterwarnings('ignore')

# ============================================================
# STEP 1: Create district grid map (same as 2025)
# ============================================================

print("Loading district polygons...")
districts = gpd.read_file('india_districts.geojson')
print(f"Loaded {len(districts)} districts")

if 'dtname' in districts.columns:
    name_col = 'dtname'
elif 'DISTRICT' in districts.columns:
    name_col = 'DISTRICT'
elif 'district' in districts.columns:
    name_col = 'district'
else:
    name_col = districts.columns[0]

if 'stname' in districts.columns:
    state_col = 'stname'
elif 'STATE' in districts.columns:
    state_col = 'STATE'
elif 'state' in districts.columns:
    state_col = 'state'
else:
    state_col = districts.columns[1] if len(districts.columns) > 1 else districts.columns[0]

print(f"District name column: {name_col}, State column: {state_col}")

if districts.crs != 'EPSG:4326':
    districts = districts.to_crs('EPSG:4326')
    print("Reprojected to EPSG:4326")

districts['canonical_key'] = districts[name_col].str.strip().str.upper() + '_' + districts[state_col].str.strip().str.upper()
print(f"Sample canonical keys: {districts['canonical_key'].head(10).tolist()}")

# Create grid polygons
print("\nCreating grid polygons...")
lats = np.arange(6.5, 38.5 + 0.25, 0.25)
lons = np.arange(66.5, 100.0 + 0.25, 0.25)
print(f"Grid: {len(lats)} lat x {len(lons)} lon")

grid_polys = []
grid_indices = []
for i, lat in enumerate(lats):
    for j, lon in enumerate(lons):
        poly = box(lon - 0.125, lat - 0.125, lon + 0.125, lat + 0.125)
        grid_polys.append(poly)
        grid_indices.append((i, j))

grid_gdf = gpd.GeoDataFrame({'grid_idx': grid_indices}, geometry=grid_polys, crs='EPSG:4326')
print(f"Created {len(grid_gdf)} grid polygons")

# Spatial join
print("Performing spatial join...")
joined = gpd.sjoin(grid_gdf, districts[['canonical_key', 'geometry']], how='left', predicate='intersects')
print(f"Joined shape: {joined.shape}")
print(f"Grid cells with district match: {joined['canonical_key'].notna().sum()}")
print(f"Grid cells without match: {joined['canonical_key'].isna().sum()}")

district_grid_map = {}
for idx, row in joined.dropna(subset=['canonical_key']).iterrows():
    key = row['canonical_key']
    grid_idx = row['grid_idx']
    if key not in district_grid_map:
        district_grid_map[key] = []
    district_grid_map[key].append(grid_idx)

print(f"Districts with grid cells: {len(district_grid_map)}")

with open('temp_district_grid_map.pkl', 'wb') as f:
    pickle.dump(district_grid_map, f)
print("Saved temp_district_grid_map.pkl")

# Also save districts for later use
districts.to_pickle('temp_districts.pkl')
print("Saved temp_districts.pkl")