import pandas as pd
import xarray as xr
import geopandas as gpd
import numpy as np
import json
from shapely.geometry import box
import warnings
warnings.filterwarnings('ignore')

# ============================================================
# 2. LOAD AND PROCESS NETCDF (2025 GRIDDED DATA)
# ============================================================
print("Loading NetCDF (2025 gridded rainfall)...")
ds = xr.open_dataset('RF25_ind2025_rfp25.nc')
rainfall = ds['RAINFALL']  # (time: 365, lat: 129, lon: 135)

# Get coordinates
lats = ds['LATITUDE'].values  # 6.5 to 38.5, step 0.25
lons = ds['LONGITUDE'].values  # 66.5 to 100.0, step 0.25
times = pd.to_datetime(ds['TIME'].values)

print(f"Grid: {len(lats)} lat x {len(lons)} lon")
print(f"Lat range: {lats.min()} to {lats.max()}")
print(f"Lon range: {lons.min()} to {lons.max()}")
print(f"Time range: {times.min()} to {times.max()}")
print(f"Rainfall units: {rainfall.attrs.get('units', 'unknown')}")

# Load districts
districts = pd.read_pickle('temp_districts.pkl')
print(f"Loaded {len(districts)} districts from pickle")

# Create a grid of polygons for spatial join
print("\nCreating grid polygons...")
grid_polys = []
grid_indices = []
for i, lat in enumerate(lats):
    for j, lon in enumerate(lons):
        # Each grid cell is 0.25 x 0.25 degrees
        poly = box(lon - 0.125, lat - 0.125, lon + 0.125, lat + 0.125)
        grid_polys.append(poly)
        grid_indices.append((i, j))

grid_gdf = gpd.GeoDataFrame({'grid_idx': grid_indices}, geometry=grid_polys, crs='EPSG:4326')
print(f"Created {len(grid_gdf)} grid polygons")

# Spatial join: assign each grid cell to district(s)
print("Performing spatial join...")
joined = gpd.sjoin(grid_gdf, districts[['canonical_key', 'geometry']], how='left', predicate='intersects')
print(f"Joined shape: {joined.shape}")
print(f"Grid cells with district match: {joined['canonical_key'].notna().sum()}")
print(f"Grid cells without match: {joined['canonical_key'].isna().sum()}")

# For each district, collect its grid cell indices
district_grid_map = {}
for idx, row in joined.dropna(subset=['canonical_key']).iterrows():
    key = row['canonical_key']
    grid_idx = row['grid_idx']
    if key not in district_grid_map:
        district_grid_map[key] = []
    district_grid_map[key].append(grid_idx)

print(f"Districts with grid cells: {len(district_grid_map)}")

# Save district_grid_map for next part
import pickle
with open('temp_district_grid_map.pkl', 'wb') as f:
    pickle.dump(district_grid_map, f)
print("Saved temp_district_grid_map.pkl")

# Also save rainfall data array info
np.save('temp_rainfall_data.npy', rainfall.values)
np.save('temp_times.npy', times.values)
print("Saved temp_rainfall_data.npy and temp_times.npy")