#!/usr/bin/env python
"""
Validate master_agri_dataset_v2.csv before Phase 3.
"""
import pandas as pd
import numpy as np
from pathlib import Path

DATASETS_DIR = Path(__file__).parent

print("=" * 80)
print("VALIDATION: master_agri_dataset_v2.csv")
print("=" * 80)

# Load dataset
df = pd.read_csv(DATASETS_DIR / "master_agri_dataset_v2.csv", low_memory=False)
print(f"\n1. BASIC SHAPE")
print(f"   Shape: {df.shape}")
print(f"   Columns: {df.columns.tolist()}")
print(f"   Memory: {df.memory_usage(deep=True).sum() / 1024**2:.1f} MB")

print(f"\n2. COLUMN TYPES")
for col in df.columns:
    dtype = df[col].dtype
    nunique = df[col].nunique()
    nulls = df[col].isna().sum()
    print(f"   {col:35s} {str(dtype):15s} nunique={nunique:8d} nulls={nulls:8d}")

print(f"\n3. DUPLICATE CHECK - district-crop-year combinations")
dup_mask = df.duplicated(subset=['canonical_key', 'crop', 'year'], keep=False)
n_dups = dup_mask.sum()
print(f"   Total duplicate rows: {n_dups}")
if n_dups > 0:
    dup_examples = df[dup_mask].head(10)
    print(f"   Example duplicates:")
    for _, row in dup_examples.iterrows():
        print(f"      {row['canonical_key']} | {row['crop']} | {row['year']}")
else:
    print(f"   ✓ No duplicate district-crop-year combinations")

print(f"\n4. GENUINE RECORD COUNTS")
gen_crop = df['area_ha'].notna().sum()
gen_rain = df['annual_rainfall_mm'].notna().sum()
gen_soil = df['soil_ph'].notna().sum()
print(f"   Genuine crop records (area_ha not null):  {gen_crop:,}")
print(f"   Genuine rainfall records (annual_rainfall_mm not null): {gen_rain:,}")
print(f"   Genuine soil records (soil_ph not null):  {gen_soil:,}")

print(f"\n5. MISSING vs ZERO VALUES CHECK")
# Check if any missing values were converted to zero
for col in ['area_ha', 'production_tonnes', 'yield_tons_per_ha', 'annual_rainfall_mm']:
    if col in df.columns:
        zeros = (df[col] == 0).sum()
        nulls = df[col].isna().sum()
        print(f"   {col}: zeros={zeros:,} nulls={nulls:,}")
        if zeros > 0 and nulls > 0:
            print(f"      ⚠ WARNING: Both zeros and nulls present - check if zeros are genuine")

print(f"\n6. PROVENANCE COLUMNS")
for col in ['crop_data_source', 'rainfall_data_source', 'soil_data_source']:
    if col in df.columns:
        print(f"   {col}:")
        for val, cnt in df[col].value_counts().items():
            print(f"      {val}: {cnt:,}")

print(f"\n7. YEAR RANGES BY DATA TYPE")
print(f"   All years: {sorted(df['year'].unique())}")
crop_years = sorted(df[df['area_ha'].notna()]['year'].unique())
rain_years = sorted(df[df['annual_rainfall_mm'].notna()]['year'].unique())
print(f"   Crop data years: {crop_years}")
print(f"   Rainfall data years: {rain_years}")
print(f"   Overlap years: {set(crop_years) & set(rain_years)}")

print(f"\n8. DISTRICT COVERAGE")
print(f"   Unique districts (canonical): {df['canonical_key'].nunique()}")
print(f"   Unique districts (name): {df['district_name'].nunique()}")
districts_with_crop = df[df['area_ha'].notna()]['canonical_key'].nunique()
districts_with_rain = df[df['annual_rainfall_mm'].notna()]['canonical_key'].nunique()
print(f"   Districts with crop data: {districts_with_crop}")
print(f"   Districts with rainfall data: {districts_with_rain}")

print(f"\n9. CROP COVERAGE")
print(f"   Unique crops: {df['crop'].nunique()}")
print(f"   Crops: {sorted(df['crop'].unique())}")

# Check crop distribution in genuine data
if gen_crop > 0:
    print(f"\n   Genuine crop records by crop:")
    crop_counts = df[df['area_ha'].notna()]['crop'].value_counts()
    for crop, cnt in crop_counts.items():
        print(f"      {crop}: {cnt:,}")

print(f"\n10. VALUE RANGES (genuine data only)")
for col in ['area_ha', 'production_tonnes', 'yield_tons_per_ha', 'annual_rainfall_mm']:
    if col in df.columns:
        genuine = df[df[col].notna()][col]
        if len(genuine) > 0:
            print(f"   {col}: min={genuine.min():.2f}, max={genuine.max():.2f}, mean={genuine.mean():.2f}, median={genuine.median():.2f}")

print(f"\n11. SOIL DATA CHECK")
soil_cols = ['soil_ph', 'soil_organic_carbon_percent', 'soil_nitrogen_kg_per_ha',
             'soil_phosphorus_kg_per_ha', 'soil_potassium_kg_per_ha', 'soil_texture']
for col in soil_cols:
    if col in df.columns:
        non_null = df[col].notna().sum()
        print(f"   {col}: non-null={non_null:,}")

print(f"\n12. AGRONOMY DATA CHECK")
agronomy_cols = ['season', 'duration_days', 'n_kg_per_ha', 'p_kg_per_ha', 'k_kg_per_ha',
                 'water_requirement_mm', 'optimal_temp_c', 'soil_ph_range',
                 'cultivation_cost_inr_per_ha', 'market_price_inr_per_ton',
                 'yield_range_tons_per_ha', 'suitable_soils', 'data_source']
for col in agronomy_cols:
    if col in df.columns:
        non_null = df[col].notna().sum()
        print(f"   {col}: non-null={non_null:,}")

print("\n" + "=" * 80)
print("VALIDATION COMPLETE")
print("=" * 80)