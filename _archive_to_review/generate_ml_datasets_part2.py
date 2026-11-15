#!/usr/bin/env python
"""
Generate ML-ready datasets from master_agri_dataset_v2.csv - Part 2: Crop Recommendation
"""
import pandas as pd
import numpy as np
from pathlib import Path

DATASETS_DIR = Path(__file__).parent

# Load fixed master
df = pd.read_csv(DATASETS_DIR / "master_agri_dataset_v2_fixed.csv", low_memory=False)
print(f"Loaded fixed master: {df.shape}")

# Load rainfall climatology
rain_climatology = pd.read_csv(DATASETS_DIR / "rainfall_climatology.csv") if (DATASETS_DIR / "rainfall_climatology.csv").exists() else None

if rain_climatology is None:
    rain_climatology = df[df['annual_rainfall_mm'].notna()].groupby('canonical_key')['annual_rainfall_mm'].agg(['mean', 'std', 'min', 'max']).reset_index()
    rain_climatology.columns = ['canonical_key', 'rainfall_mean_mm', 'rainfall_std_mm', 'rainfall_min_mm', 'rainfall_max_mm']
    rain_climatology.to_csv(DATASETS_DIR / "rainfall_climatology.csv", index=False)

print(f"Rainfall climatology: {len(rain_climatology)} districts")

# ============================================================
# DATASET 1: CROP RECOMMENDATION
# ============================================================
print("\n" + "="*80)
print("DATASET 1: CROP RECOMMENDATION")
print("="*80)

# Target: crop (what to plant)
# Features: soil, climate, agronomy, district
# Only use records with genuine crop data

crop_rec_df = df[df['area_ha'].notna()].copy()
print(f"   Base genuine crop records: {len(crop_rec_df):,}")

# Merge rainfall climatology
crop_rec_df = crop_rec_df.merge(rain_climatology, on='canonical_key', how='left')
print(f"   After rainfall climatology merge: {crop_rec_df['rainfall_mean_mm'].notna().sum()} have rainfall climatology")

# Features for crop recommendation
crop_rec_features = [
    'canonical_key', 'district_name', 'state_name', 'district_id',
    'year', 'crop',  # target
    'rainfall_mean_mm', 'rainfall_std_mm', 'rainfall_min_mm', 'rainfall_max_mm',
    # Soil features (all NaN - will need to be filled later)
    'soil_ph', 'soil_organic_carbon_percent', 'soil_nitrogen_kg_per_ha',
    'soil_phosphorus_kg_per_ha', 'soil_potassium_kg_per_ha', 'soil_texture',
    # Agronomy features (crop-specific)
    'season', 'duration_days', 'n_kg_per_ha', 'p_kg_per_ha', 'k_kg_per_ha',
    'water_requirement_mm', 'optimal_temp_c', 'soil_ph_range',
    'cultivation_cost_inr_per_ha', 'market_price_inr_per_ton',
    'yield_range_tons_per_ha', 'suitable_soils',
    # Provenance
    'crop_data_source'
]

crop_rec_ready = crop_rec_df[crop_rec_features].copy()

print(f"   Records with rainfall climatology: {crop_rec_ready['rainfall_mean_mm'].notna().sum():,}")
print(f"   Records with soil data: {crop_rec_ready['soil_ph'].notna().sum():,}")
print(f"   Records with agronomy: {crop_rec_ready['season'].notna().sum():,}")

# Save
output_path = DATASETS_DIR / "ml_ready_crop_recommendation.csv"
crop_rec_ready.to_csv(output_path, index=False)
print(f"   Saved: {output_path} ({crop_rec_ready.shape})")

# Usable rows for training (with at least rainfall climatology)
usable_crop_rec = crop_rec_ready[crop_rec_ready['rainfall_mean_mm'].notna()]
print(f"   Usable training rows (with rainfall climatology): {len(usable_crop_rec):,}")

print("\nPart 2 complete. Run part 3 for yield prediction dataset.")