import pandas as pd
import numpy as np
import json
import pickle
import warnings
warnings.filterwarnings('ignore')

# ============================================================
# 3. COMPUTE DAILY RAINFALL PER DISTRICT FROM NETCDF
# ============================================================
print("Computing daily rainfall per district from NetCDF...")

# Load saved data
with open('temp_district_grid_map.pkl', 'rb') as f:
    district_grid_map = pickle.load(f)

rainfall_data = np.load('temp_rainfall_data.npy')  # (365, 129, 135)
times = pd.to_datetime(np.load('temp_times.npy', allow_pickle=True))

print(f"Rainfall data shape: {rainfall_data.shape}")
print(f"Times shape: {times.shape}")
print(f"Districts in grid map: {len(district_grid_map)}")

# Now compute daily rainfall for each district by averaging its grid cells
district_daily = {}
for key, grid_cells in district_grid_map.items():
    # Extract rainfall for all grid cells for this district across all time
    # rainfall_data shape: (time, lat, lon)
    # grid_cells: list of (lat_idx, lon_idx)
    district_rainfall = []
    for lat_idx, lon_idx in grid_cells:
        district_rainfall.append(rainfall_data[:, lat_idx, lon_idx])
    district_rainfall = np.array(district_rainfall)  # (n_cells, 365)
    # Average across grid cells
    daily_avg = np.nanmean(district_rainfall, axis=0)
    district_daily[key] = daily_avg

# Create DataFrame from district_daily
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
print(f"NetCDF derived district-daily records: {len(nc_df)}")
print(f"Districts covered: {nc_df['canonical_key'].nunique()}")
print(f"Date range: {nc_df['date'].min()} to {nc_df['date'].max()}")

# Save for next part
nc_df.to_pickle('temp_nc_df.pkl')
print("Saved temp_nc_df.pkl")