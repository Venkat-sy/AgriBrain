#!/usr/bin/env python
"""
Data Quality Upgrade - Part 2b: Rebuild rainfall datasets
"""
import json
import pandas as pd
import numpy as np
from pathlib import Path
import pickle
import warnings
warnings.filterwarnings('ignore')

DATASETS_DIR = Path(__file__).parent

OUTPUTS = {
    "district_rainfall_summary": DATASETS_DIR / "district_rainfall_summary.json",
    "district_rainfall_history": DATASETS_DIR / "district_rainfall_history.csv",
}

print("=" * 70)
print("PHASE 2 DATA QUALITY UPGRADE - Part 2b: Rebuild Rainfall")
print("=" * 70)

with open(DATASETS_DIR / 'intermediate_data.pkl', 'rb') as f:
    data = pickle.load(f)

geo_df = data['geo_df']
mapping = data['mapping']
rainfall_raw = data['rainfall_raw']

print("\n1. Rebuilding rainfall datasets (using synthetic data, clearly marked)...")

rain_mapped = rainfall_raw.merge(
    mapping[['source_district', 'source_state', 'canonical_district', 'canonical_state', 'district_id']],
    left_on=['DISTRICT', 'STATE'],
    right_on=['source_district', 'source_state'],
    how='left'
)

matched_rain = rain_mapped[rain_mapped['canonical_district'].notna()].copy()
print(f"   Mapped rainfall records: {len(matched_rain)}/{len(rainfall_raw)}")

# district_rainfall_history.csv - full history
history_cols = ['canonical_district', 'canonical_state', 'YEAR', 'ANNUAL_RAINFALL_mm']
history_df = matched_rain[history_cols].copy()
history_df.columns = ['district_name', 'state_name', 'year', 'annual_rainfall_mm']
history_df['data_source'] = 'synthetic_placeholder'
history_df = history_df.sort_values(['district_name', 'year']).reset_index(drop=True)
history_df.to_csv(OUTPUTS["district_rainfall_history"], index=False)
print(f"   Saved district_rainfall_history.csv: {len(history_df)} rows (all synthetic)")

# district_rainfall_summary.json - 5-year summary
summary = {}
for _, row in geo_df.iterrows():
    district = row['district_name']
    state = row['state_name']
    
    district_data = matched_rain[
        (matched_rain['canonical_district'] == district) & 
        (matched_rain['canonical_state'] == state)
    ]
    
    if len(district_data) == 0:
        summary[district] = {
            "annual_rainfall_mm": {},
            "mean_annual_rainfall_mm": None,
            "kharif_seasonal_avg_mm": None,
            "rabi_seasonal_avg_mm": None,
            "zaid_seasonal_avg_mm": None,
            "data_availability": "missing",
            "data_source": "none",
            "years_available": 0,
            "year_range": None
        }
        continue
    
    district_data = district_data.sort_values('YEAR', ascending=False)
    latest_years = district_data.head(5)
    
    annual = {}
    for _, r in latest_years.iterrows():
        annual[str(int(r['YEAR']))] = round(float(r['ANNUAL_RAINFALL_mm']), 1)
    
    mean_annual = round(district_data['ANNUAL_RAINFALL_mm'].mean(), 1)
    kharif = round(mean_annual * 0.65, 1)
    rabi = round(mean_annual * 0.25, 1)
    zaid = round(mean_annual * 0.10, 1)
    
    summary[district] = {
        "annual_rainfall_mm": annual,
        "mean_annual_rainfall_mm": mean_annual,
        "kharif_seasonal_avg_mm": kharif,
        "rabi_seasonal_avg_mm": rabi,
        "zaid_seasonal_avg_mm": zaid,
        "data_availability": "synthetic_placeholder",
        "data_source": "synthetic_placeholder_2000-2019",
        "years_available": len(district_data),
        "year_range": f"{int(district_data['YEAR'].min())}-{int(district_data['YEAR'].max())}"
    }

with open(OUTPUTS["district_rainfall_summary"], 'w') as f:
    json.dump(summary, f, indent=2)

actual_count = sum(1 for v in summary.values() if v['data_availability'] == 'actual')
synthetic_count = sum(1 for v in summary.values() if v['data_availability'] == 'synthetic_placeholder')
missing_count = sum(1 for v in summary.values() if v['data_availability'] == 'missing')
print(f"   Saved district_rainfall_summary.json: {len(summary)} districts")
print(f"   Actual: {actual_count}, Synthetic: {synthetic_count}, Missing: {missing_count}")

# Save summary for next part
with open(DATASETS_DIR / 'rainfall_summary.pkl', 'wb') as f:
    pickle.dump(summary, f)

print("\nPart 2b complete. Run Part 2c next.")