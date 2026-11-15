#!/usr/bin/env python
"""
Rebuild master dataset with correct alignment of:
- Canonical district IDs from GeoJSON
- Crop names (standardized)
- Years
- Rainfall data (from temp_annual.pkl)
- Crop data (from ICRISAT processed files)
- Soil data (marked as missing)
"""
import pandas as pd
import numpy as np
import geopandas as gpd
from pathlib import Path

DATASETS_DIR = Path(__file__).parent
PROCESSED_DIR = DATASETS_DIR / "processed"

# ============================================================
# 1. Load canonical districts
# ============================================================
districts = gpd.read_file(DATASETS_DIR / "india_districts.geojson")
districts['canonical_key'] = districts['district_name'].str.strip().str.upper() + '_' + districts['state_name'].str.strip().str.upper()
print(f"Canonical districts: {len(districts)}")

# ============================================================
# 2. Load ICRISAT crop data (processed, canonical)
# ============================================================
crop_prod = pd.read_csv(PROCESSED_DIR / "crop_production_district_icrisat.csv")
crop_yield = pd.read_csv(PROCESSED_DIR / "crop_yield_district_icrisat.csv")
print(f"ICRISAT production: {crop_prod.shape}")
print(f"ICRISAT yield: {crop_yield.shape}")
print(f"Crop years: {sorted(crop_prod['year'].unique())}")
print(f"Crop districts: {crop_prod['district_name'].nunique()}")
print(f"Crop crops: {crop_prod['crop'].nunique()}")
print(f"Crops: {sorted(crop_prod['crop'].unique())}")

# ============================================================
# 3. Load rainfall data (temp_annual.pkl)
# ============================================================
rainfall = pd.read_pickle(DATASETS_DIR / "temp_annual.pkl")
print(f"\nRainfall: {rainfall.shape}")
print(f"Rainfall years: {sorted(rainfall['year'].unique())}")
print(f"Rainfall district-state pairs: {rainfall.drop_duplicates(subset=['district_name', 'state_name']).shape[0]}")

# Create canonical key for rainfall
rainfall['canonical_key'] = rainfall['district_name'].str.strip().str.upper() + '_' + rainfall['state_name'].str.strip().str.upper()

# ============================================================
# 4. Create canonical crop data key
# ============================================================
crop_prod['canonical_key'] = crop_prod['district_name'].str.strip().str.upper() + '_' + crop_prod['state_name'].str.strip().str.upper()
crop_yield['canonical_key'] = crop_yield['district_name'].str.strip().str.upper() + '_' + crop_yield['state_name'].str.strip().str.upper()