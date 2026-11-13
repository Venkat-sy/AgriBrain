#!/usr/bin/env python
"""
Generate ML-ready datasets from master_agri_dataset_v2.csv - Part 1: Setup and fixes
"""
import pandas as pd
import numpy as np
from pathlib import Path

DATASETS_DIR = Path(__file__).parent

print("=" * 80)
print("GENERATING ML-READY DATASETS")
print("=" * 80)

# Load master dataset
df = pd.read_csv(DATASETS_DIR / "master_agri_dataset_v2.csv", low_memory=False)
print(f"Loaded master: {df.shape}")

# ============================================================
# Fix known data issues
# ============================================================
print("\n1. FIXING KNOWN DATA ISSUES")

# Fix 1: yield=0 with positive area and production -> set to NaN
mask_yield_zero = (df['yield_tons_per_ha'] == 0) & (df['area_ha'].notna()) & (df['production_tonnes'].notna()) & (df['area_ha'] > 0) & (df['production_tonnes'] > 0)
df.loc[mask_yield_zero, 'yield_tons_per_ha'] = np.nan
print(f"   Fixed {mask_yield_zero.sum()} yield=0 records (set to NaN)")

# Fix 2: rainfall=0 for NICOBAR from netcdf_grid_derived -> set to NaN
mask_rain_zero = (df['annual_rainfall_mm'] == 0) & (df['rainfall_data_source'] == 'netcdf_grid_derived')
df.loc[mask_rain_zero, 'annual_rainfall_mm'] = np.nan
print(f"   Fixed {mask_rain_zero.sum()} rainfall=0 records from netcdf (set to NaN)")

# ============================================================
# Compute district-level rainfall climatology
# ============================================================
rain_climatology = df[df['annual_rainfall_mm'].notna()].groupby('canonical_key')['annual_rainfall_mm'].agg(['mean', 'std', 'min', 'max']).reset_index()
rain_climatology.columns = ['canonical_key', 'rainfall_mean_mm', 'rainfall_std_mm', 'rainfall_min_mm', 'rainfall_max_mm']
print(f"\n   District rainfall climatology: {len(rain_climatology)} districts")

# Save fixed master
df.to_csv(DATASETS_DIR / "master_agri_dataset_v2_fixed.csv", index=False)
print(f"   Saved fixed master: master_agri_dataset_v2_fixed.csv")

print("\nPart 1 complete. Run part 2 for crop recommendation dataset.")