#!/usr/bin/env python
"""
Generate ML-ready datasets from master_agri_dataset_v2.csv - Part 4: Rainfall Forecasting
"""
import pandas as pd
import numpy as np
from pathlib import Path

DATASETS_DIR = Path(__file__).parent

# Load fixed master
df = pd.read_csv(DATASETS_DIR / "master_agri_dataset_v2_fixed.csv", low_memory=False)
print(f"Loaded fixed master: {df.shape}")

# ============================================================
# DATASET 3: RAINFALL FORECASTING
# ============================================================
print("\n" + "="*80)
print("DATASET 3: RAINFALL FORECASTING")
print("="*80)

# Target: annual_rainfall_mm (or daily/monthly)
# Features: district, year, lagged rainfall, spatial features
# Only use genuine rainfall records

rain_df = df[df['annual_rainfall_mm'].notna()].copy()
print(f"   Base genuine rainfall records: {len(rain_df):,}")

# This is a time series forecasting problem
# We have annual rainfall for 2021-2026 for 641 districts
# Can create lag features

rain_df = rain_df.sort_values(['canonical_key', 'year'])

# Create lag features
for lag in [1, 2, 3]:
    rain_df[f'rainfall_lag_{lag}'] = rain_df.groupby('canonical_key')['annual_rainfall_mm'].shift(lag)

# Create rolling statistics
rain_df['rainfall_rolling_mean_3'] = rain_df.groupby('canonical_key')['annual_rainfall_mm'].transform(lambda x: x.rolling(3, min_periods=1).mean())
rain_df['rainfall_rolling_std_3'] = rain_df.groupby('canonical_key')['annual_rainfall_mm'].transform(lambda x: x.rolling(3, min_periods=1).std())

rain_features = [
    'canonical_key', 'district_name', 'state_name', 'district_id',
    'year',
    'annual_rainfall_mm',  # TARGET
    'rainfall_lag_1', 'rainfall_lag_2', 'rainfall_lag_3',
    'rainfall_rolling_mean_3', 'rainfall_rolling_std_3',
    'rainfall_data_source'
]

rain_ready = rain_df[rain_features].copy()

# Remove rows where lag features are NaN (first years for each district)
rain_ready_with_lags = rain_ready.dropna(subset=['rainfall_lag_1'])
print(f"   Records with lag features: {len(rain_ready_with_lags):,}")

output_path = DATASETS_DIR / "ml_ready_rainfall_forecasting.csv"
rain_ready.to_csv(output_path, index=False)
print(f"   Saved: {output_path} ({rain_ready.shape})")

usable_rain = rain_ready_with_lags
print(f"   Usable training rows (with lags): {len(usable_rain):,}")

# ============================================================
# SUMMARY REPORT
# ============================================================
print("\n" + "="*80)
print("SUMMARY: USABLE TRAINING ROWS PER MODEL")
print("="*80)

# Load the other datasets to get counts
crop_rec = pd.read_csv(DATASETS_DIR / "ml_ready_crop_recommendation.csv")
yield_pred = pd.read_csv(DATASETS_DIR / "ml_ready_yield_prediction.csv")

print(f"\n1. CROP RECOMMENDATION")
print(f"   Total records: {len(crop_rec):,}")
print(f"   Usable (with rainfall climatology): {crop_rec['rainfall_mean_mm'].notna().sum():,}")
print(f"   Target: crop (23 classes)")
print(f"   Key limitation: NO soil data (all NaN)")
print(f"   Key limitation: Rainfall is climatology, not year-specific")

print(f"\n2. YIELD PREDICTION")
print(f"   Total records: {len(yield_pred):,}")
print(f"   Usable (with rainfall climatology): {yield_pred['rainfall_mean_mm'].notna().sum():,}")
print(f"   Target: yield_tons_per_ha (continuous)")
print(f"   Key limitation: NO year-specific rainfall (zero temporal overlap)")
print(f"   Key limitation: NO soil data (all NaN)")
print(f"   Potential outliers (>8.02 t/ha): {(yield_pred['yield_tons_per_ha'] > yield_pred['yield_tons_per_ha'].quantile(0.99)).sum()}")

print(f"\n3. RAINFALL FORECASTING")
print(f"   Total records: {len(rain_ready):,}")
print(f"   Usable (with lag features): {len(usable_rain):,}")
print(f"   Target: annual_rainfall_mm (continuous)")
print(f"   Status: ONLY dataset with genuine temporal data for training")
print(f"   Years: 2021-2026, Districts: 641")

print(f"\n4. OVERALL ASSESSMENT")
print(f"   Rainfall forecasting: READY for training (genuine temporal data)")
print(f"   Crop recommendation: LIMITED - needs soil data, no year-specific weather")
print(f"   Yield prediction: LIMITED - needs soil data, no year-specific weather")
print(f"   Irrigation demand / Crop failure risk: NOT READY - no soil, no failure labels")

print("\n" + "="*80)
print("FILES GENERATED:")
print(f"   - {DATASETS_DIR / 'ml_ready_crop_recommendation.csv'}")
print(f"   - {DATASETS_DIR / 'ml_ready_yield_prediction.csv'}")
print(f"   - {DATASETS_DIR / 'ml_ready_rainfall_forecasting.csv'}")
print(f"   - {DATASETS_DIR / 'master_agri_dataset_v2_fixed.csv'}")
print(f"   - {DATASETS_DIR / 'rainfall_climatology.csv'}")
print("="*80)