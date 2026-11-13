#!/usr/bin/env python
"""
Check zero values in yield and rainfall to determine if genuine or missing.
"""
import pandas as pd
import numpy as np
from pathlib import Path

DATASETS_DIR = Path(__file__).parent
df = pd.read_csv(DATASETS_DIR / "master_agri_dataset_v2.csv", low_memory=False)

print("=== ZERO VALUE INVESTIGATION ===\n")

# Check yield_tons_per_ha zeros
print("1. yield_tons_per_ha == 0 records:")
zero_yield = df[df['yield_tons_per_ha'] == 0]
print(f"   Count: {len(zero_yield)}")
if len(zero_yield) > 0:
    print(f"   Columns: {zero_yield.columns.tolist()}")
    print(f"   Sample:")
    for _, row in zero_yield.head(10).iterrows():
        print(f"      {row['canonical_key']} | {row['crop']} | {row['year']} | area_ha={row['area_ha']} | prod={row['production_tonnes']} | yield={row['yield_tons_per_ha']} | crop_src={row['crop_data_source']} | rain_src={row['rainfall_data_source']}")

# Check if these have genuine crop data
print(f"\n   Of zero yield records:")
print(f"      With area_ha: {zero_yield['area_ha'].notna().sum()}")
print(f"      With production: {zero_yield['production_tonnes'].notna().sum()}")
print(f"      crop_data_source: {zero_yield['crop_data_source'].value_counts().to_dict()}")

# Check if yield=0 but area>0 and production>0 (impossible, would mean zero yield)
gen_crop_zero_yield = zero_yield[zero_yield['area_ha'].notna()]
if len(gen_crop_zero_yield) > 0:
    print(f"\n   Genuine crop records with yield=0:")
    for _, row in gen_crop_zero_yield.head(10).iterrows():
        print(f"      {row['canonical_key']} | {row['crop']} | {row['year']} | area={row['area_ha']} | prod={row['production_tonnes']}")

print("\n" + "="*80)

# Check annual_rainfall_mm zeros
print("\n2. annual_rainfall_mm == 0 records:")
zero_rain = df[df['annual_rainfall_mm'] == 0]
print(f"   Count: {len(zero_rain)}")
if len(zero_rain) > 0:
    print(f"   Sample:")
    for _, row in zero_rain.head(10).iterrows():
        print(f"      {row['canonical_key']} | {row['year']} | rain={row['annual_rainfall_mm']} | rain_src={row['rainfall_data_source']}")

print(f"\n   Of zero rainfall records:")
print(f"      rainfall_data_source: {zero_rain['rainfall_data_source'].value_counts().to_dict()}")

# Check if any zero rainfall records have genuine crop data
zero_rain_with_crop = zero_rain[zero_rain['area_ha'].notna()]
print(f"\n   Zero rainfall + genuine crop: {len(zero_rain_with_crop)}")

# Also check: are there rainfall records with 0 but marked as genuine source?
gen_rain_zero = zero_rain[zero_rain['rainfall_data_source'] != 'MISSING - No IMD rainfall for this district/year']
print(f"\n   Zero rainfall with genuine source: {len(gen_rain_zero)}")
if len(gen_rain_zero) > 0:
    print(f"      Sources: {gen_rain_zero['rainfall_data_source'].value_counts().to_dict()}")
    for _, row in gen_rain_zero.head(5).iterrows():
        print(f"      {row['canonical_key']} | {row['year']} | {row['rainfall_data_source']}")

print("\n" + "="*80)

# Check if the 6 yield zeros and 460 rainfall zeros are problematic
print("\n3. SUMMARY")
print(f"   yield_tons_per_ha zeros: 6 (of 179,283 genuine crop records)")
print(f"   annual_rainfall_mm zeros: 460 (of 83,766 genuine rainfall records)")
print(f"   These could be genuine zeros (e.g., crop failure, no rain) or data issues")
print(f"   Need to decide: keep as-is, set to NaN, or impute")