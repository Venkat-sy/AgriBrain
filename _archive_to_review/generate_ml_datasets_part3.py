#!/usr/bin/env python
"""
Generate ML-ready datasets from master_agri_dataset_v2.csv - Part 3: Yield Prediction
"""
import pandas as pd
import numpy as np
from pathlib import Path

DATASETS_DIR = Path(__file__).parent

# Load fixed master
df = pd.read_csv(DATASETS_DIR / "master_agri_dataset_v2_fixed.csv", low_memory=False)
print(f"Loaded fixed master: {df.shape}")

# Load rainfall climatology
rain_climatology = pd.read_csv(DATASETS_DIR / "rainfall_climatology.csv")

# ============================================================
# DATASET 2: HISTORICAL YIELD PREDICTION
# ============================================================
print("\n" + "="*80)
print("DATASET 2: HISTORICAL YIELD PREDICTION")
print("="*80)

# Target: yield_tons_per_ha
# Features: district, crop, year, soil, rainfall (climatology), agronomy
# Only use records with genuine yield data

yield_df = df[(df['yield_tons_per_ha'].notna()) & (df['area_ha'].notna())].copy()
print(f"   Base genuine yield records: {len(yield_df):,}")

# Merge rainfall climatology
yield_df = yield_df.merge(rain_climatology, on='canonical_key', how='left')
print(f"   With rainfall climatology: {yield_df['rainfall_mean_mm'].notna().sum():,}")

yield_features = [
    'canonical_key', 'district_name', 'state_name', 'district_id',
    'crop', 'year',
    'area_ha', 'production_tonnes',
    'yield_tons_per_ha',  # TARGET
    'rainfall_mean_mm', 'rainfall_std_mm', 'rainfall_min_mm', 'rainfall_max_mm',
    'soil_ph', 'soil_organic_carbon_percent', 'soil_nitrogen_kg_per_ha',
    'soil_phosphorus_kg_per_ha', 'soil_potassium_kg_per_ha', 'soil_texture',
    'season', 'duration_days', 'n_kg_per_ha', 'p_kg_per_ha', 'k_kg_per_ha',
    'water_requirement_mm', 'optimal_temp_c', 'soil_ph_range',
    'cultivation_cost_inr_per_ha', 'market_price_inr_per_ton',
    'yield_range_tons_per_ha', 'suitable_soils',
    'crop_data_source', 'rainfall_data_source'
]

yield_ready = yield_df[yield_features].copy()

# Check yield distribution
print(f"   Yield range: {yield_ready['yield_tons_per_ha'].min():.2f} - {yield_ready['yield_tons_per_ha'].max():.2f}")
print(f"   Yield mean: {yield_ready['yield_tons_per_ha'].mean():.2f}, median: {yield_ready['yield_tons_per_ha'].median():.2f}")

# Flag potential outliers (yield > 99th percentile)
yield_99 = yield_ready['yield_tons_per_ha'].quantile(0.99)
outliers = yield_ready['yield_tons_per_ha'] > yield_99
print(f"   Potential outliers (>{yield_99:.2f} t/ha): {outliers.sum()}")

output_path = DATASETS_DIR / "ml_ready_yield_prediction.csv"
yield_ready.to_csv(output_path, index=False)
print(f"   Saved: {output_path} ({yield_ready.shape})")

usable_yield = yield_ready[yield_ready['rainfall_mean_mm'].notna()]
print(f"   Usable training rows (with rainfall climatology): {len(usable_yield):,}")
print(f"   NOTE: No year-specific rainfall available (zero temporal overlap)")

print("\nPart 3 complete. Run part 4 for rainfall forecasting dataset.")