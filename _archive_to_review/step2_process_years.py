import pandas as pd
import xarray as xr
import numpy as np
import json
import pickle
import warnings
warnings.filterwarnings('ignore')

# ============================================================
# STEP 2: Process each year 2021-2024
# ============================================================

YEARS = [2021, 2022, 2023, 2024]

# Load district grid map
with open('temp_district_grid_map.pkl', 'rb') as f:
    district_grid_map = pickle.load(f)
print(f"Loaded district_grid_map: {len(district_grid_map)} districts")

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

# Save all year dfs
with open('temp_all_year_dfs.pkl', 'wb') as f:
    pickle.dump(all_year_dfs, f)
print("\nSaved temp_all_year_dfs.pkl")