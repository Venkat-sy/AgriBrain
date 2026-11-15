#!/usr/bin/env python
"""
Rebuild master dataset - Step 2: Create grid and merge crop data
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
# 2. Load ICRISAT crop data
# ============================================================
crop_prod = pd.read_csv(PROCESSED_DIR / "crop_production_district_icrisat.csv")
crop_yield = pd.read_csv(PROCESSED_DIR / "crop_yield_district_icrisat.csv")
print(f"ICRISAT production: {crop_prod.shape}")
print(f"ICRISAT yield: {crop_yield.shape}")

# Create canonical key for crop data
crop_prod['canonical_key'] = crop_prod['district_name'].str.strip().str.upper() + '_' + crop_prod['state_name'].str.strip().str.upper()
crop_yield['canonical_key'] = crop_yield['district_name'].str.strip().str.upper() + '_' + crop_yield['state_name'].str.strip().str.upper()

# ============================================================
# 3. Standardize crop names
# ============================================================
crop_name_map = {
    'RICE': 'Rice', 'WHEAT': 'Wheat', 'MAIZE': 'Maize', 'SORGHUM': 'Sorghum',
    'PEARL MILLET': 'Pearl Millet', 'FINGER MILLET': 'Finger Millet', 'BARLEY': 'Barley',
    'KHARIF SORGHUM': 'Kharif Sorghum', 'RABI SORGHUM': 'Rabi Sorghum',
    'CHICKPEA': 'Chickpea', 'PIGEONPEA': 'Pigeonpea',
    'GREEN GRAM': 'Green Gram', 'BLACK GRAM': 'Black Gram',
    'LENTIL': 'Lentil', 'PEA': 'Pea',
    'GROUNDNUT': 'Groundnut', 'SOYABEAN': 'Soybean', 'SUNFLOWER': 'Sunflower',
    'SESAME': 'Sesame', 'SAFFLOWER': 'Safflower', 'LINSEED': 'Linseed',
    'CASTOR': 'Castor', 'RAPESEED AND MUSTARD': 'Rapeseed and Mustard',
    'COTTON': 'Cotton', 'JUTE': 'Jute', 'SUGARCANE': 'Sugarcane',
    'MINOR PULSES': 'Minor Pulses', 'OILSEEDS': 'Oilseeds',
    'BAJRA': 'Pearl Millet', 'RAGI': 'Finger Millet',
    'ARHAR': 'Pigeonpea', 'TUR': 'Pigeonpea',
    'GRAM': 'Chickpea', 'URAD': 'Black Gram', 'MOONG': 'Green Gram',
}

crop_prod['crop_standard'] = crop_prod['crop'].map(crop_name_map).fillna(crop_prod['crop'])
crop_yield['crop_standard'] = crop_yield['crop'].map(crop_name_map).fillna(crop_yield['crop'])

icrisat_years = sorted(crop_prod['year'].unique())
icrisat_crops = sorted(crop_prod['crop_standard'].unique())
print(f"\nYears: {len(icrisat_years)}, Crops: {len(icrisat_crops)}")
print(f"Crops: {icrisat_crops}")

# ============================================================
# 4. Merge crop production and yield
# ============================================================
crop_merged = pd.merge(
    crop_prod,
    crop_yield[['canonical_key', 'crop', 'year', 'yield_tons_per_ha']],
    on=['canonical_key', 'crop', 'year'],
    how='left',
    suffixes=('', '_yield')
)
print(f"\nCrop merged: {crop_merged.shape}")

# ============================================================
# 5. Create master dataset grid
# ============================================================
canonical_districts = districts[['canonical_key', 'district_name', 'state_name', 'district_id']].copy()

# Include both ICRISAT years AND rainfall years
# Rainfall years are 2021-2026 (from IMD NetCDF + observations)
rainfall_years = list(range(2021, 2027))  # 2021-2026 inclusive
all_years = sorted(set(icrisat_years) | set(rainfall_years))

print(f"\nICRISAT years: {len(icrisat_years)} ({icrisat_years[0]}-{icrisat_years[-1]})")
print(f"Rainfall years: {len(rainfall_years)} ({rainfall_years[0]}-{rainfall_years[-1]})")
print(f"Combined years: {len(all_years)} ({all_years[0]}-{all_years[-1]})")

print(f"\nCreating master grid: {len(canonical_districts)} districts x {len(icrisat_crops)} crops x {len(all_years)} years = {len(canonical_districts) * len(icrisat_crops) * len(all_years):,}")

master_rows = []
for _, dist in canonical_districts.iterrows():
    for crop in icrisat_crops:
        for year in all_years:
            master_rows.append({
                'canonical_key': dist['canonical_key'],
                'district_name': dist['district_name'],
                'state_name': dist['state_name'],
                'district_id': dist['district_id'],
                'crop': crop,
                'year': year
            })

master = pd.DataFrame(master_rows)
print(f"Master grid: {master.shape}")

# Save intermediate
master.to_pickle(DATASETS_DIR / 'temp_master_grid.pkl')
print("Saved temp_master_grid.pkl")