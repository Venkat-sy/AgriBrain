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
# PROCESS IMD GRIDDED RAINFALL NETCDF FOR YEARS 2021-2024
# Using same methodology as 2025 processing
# ============================================================

YEARS = [2021, 2022, 2023, 2024]

# Load canonical districts
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

# Create grid polygons (same as 2025)
print("\nCreating grid polygons (0.25° x 0.25°)...")
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

# Save district_grid_map for reuse
with open('temp_district_grid_map.pkl', 'wb') as f:
    pickle.dump(district_grid_map, f)
print("Saved temp_district_grid_map.pkl")

# ============================================================
# PROCESS EACH YEAR
# ============================================================
all_year_dfs = []

for year in YEARS:
    print(f"\n{'='*60}")
    print(f"PROCESSING YEAR {year}")
    print(f"{'='*60}")
    
    nc_file = f'RF25_ind{year}_rfp25.nc'
    print(f"Loading {nc_file}...")
    ds = xr.open_dataset(nc_file)
    rainfall = ds['RAINFALL']
    times = pd.to_datetime(ds['TIME'].values)
    
    print(f"  Shape: {rainfall.shape}")
    print(f"  Time range: {times[0]} to {times[-1]}")
    print(f"  Units: {rainfall.attrs.get('units', 'unknown')}")
    print(f"  Days: {len(times)}")
    
    rainfall_data = rainfall.values
    
    # Compute daily rainfall for each district
    print(f"  Computing daily rainfall per district...")
    district_daily = {}
    for key, grid_cells in district_grid_map.items():
        district_rainfall = []
        for lat_idx, lon_idx in grid_cells:
            district_rainfall.append(rainfall_data[:, lat_idx, lon_idx])
        district_rainfall = np.array(district_rainfall)
        daily_avg = np.nanmean(district_rainfall, axis=0)
        district_daily[key] = daily_avg
    
    # Create DataFrame
    nc_rows = []
    for key, daily_vals in district_daily.items():
        for t, val in enumerate(daily_vals):
            nc_rows.append({
                'canonical_key': key,
                'date': times[t],
                'rainfall_mm': float(val),
                'source': 'netcdf_grid_derived'
            })
    
    nc_df = pd.DataFrame(nc_rows)
    print(f"  District-daily records: {len(nc_df)}")
    print(f"  Districts covered: {nc_df['canonical_key'].nunique()}")
    print(f"  Date range: {nc_df['date'].min()} to {nc_df['date'].max()}")
    
    nc_df['year'] = year
    all_year_dfs.append(nc_df)
    
    nc_df.to_pickle(f'temp_nc_df_{year}.pkl')
    print(f"  Saved temp_nc_df_{year}.pkl")