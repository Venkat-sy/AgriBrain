import pandas as pd
import xarray as xr
import geopandas as gpd
import numpy as np
import json
from shapely.geometry import box
import warnings
warnings.filterwarnings('ignore')

# ============================================================
# 1. LOAD CANONICAL DISTRICT POLYGONS (641 districts)
# ============================================================
print("Loading district polygons...")
districts = gpd.read_file('india_districts.geojson')
print(f"Loaded {len(districts)} districts")
print(f"CRS: {districts.crs}")

# Check district name column
if 'dtname' in districts.columns:
    name_col = 'dtname'
elif 'DISTRICT' in districts.columns:
    name_col = 'DISTRICT'
elif 'district' in districts.columns:
    name_col = 'district'
else:
    print("Columns:", districts.columns.tolist())
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

# Ensure CRS is WGS84 for consistency with NetCDF
if districts.crs != 'EPSG:4326':
    districts = districts.to_crs('EPSG:4326')
    print("Reprojected to EPSG:4326")

# Create canonical district key
districts['canonical_key'] = districts[name_col].str.strip().str.upper() + '_' + districts[state_col].str.strip().str.upper()
print(f"Sample canonical keys: {districts['canonical_key'].head(10).tolist()}")

# Save for next part
districts.to_pickle('temp_districts.pkl')
print("Saved temp_districts.pkl")