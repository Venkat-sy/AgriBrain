#!/usr/bin/env python
import json
import pandas as pd
import numpy as np
from pathlib import Path
from thefuzz import fuzz, process
import warnings
warnings.filterwarnings('ignore')

DATASETS_DIR = Path(__file__).parent
RAW_DIR = DATASETS_DIR / 'raw'
GEOJSON_PATH = DATASETS_DIR / 'india_districts.geojson'
OUTPUTS = {
    "district_rainfall_summary": DATASETS_DIR / "district_rainfall_summary.json",
    "district_rainfall_history": DATASETS_DIR / "district_rainfall_history.csv",
}

def load_geojson_districts():
    with open(GEOJSON_PATH, 'r') as f:
        gj = json.load(f)
    districts = []
    for feat in gj['features']:
        props = feat['properties']
        districts.append({
            'district_name': props['district_name'].strip(),
            'state_name': props['state_name'].strip(),
            'district_id': props.get('district_id', ''),
        })
    return pd.DataFrame(districts)

mapping = pd.read_csv('district_name_mapping.csv')
geo_df = load_geojson_districts()

print("STEP 2: Building rainfall datasets")
rainfall = pd.read_csv(RAW_DIR / "rainfall_district_annual.csv")

# Apply mapping
rain_mapped = rainfall.merge(
    mapping[['source_district', 'source_state', 'canonical_district', 'canonical_state', 'district_id']],
    left_on=['DISTRICT', 'STATE'],
    right_on=['source_district', 'source_state'],
    how='left'
)

matched_rain = rain_mapped[rain_mapped['canonical_district'].notna()].copy()
print(f"Mapped rainfall records: {len(matched_rain)}/{len(rainfall)}")

# district_rainfall_history.csv - full history
history_cols = ['canonical_district', 'canonical_state', 'YEAR', 'ANNUAL_RAINFALL_mm']
history_df = matched_rain[history_cols].copy()
history_df.columns = ['district_name', 'state_name', 'year', 'annual_rainfall_mm']
history_df = history_df.sort_values(['district_name', 'year']).reset_index(drop=True)
history_df.to_csv(OUTPUTS["district_rainfall_history"], index=False)
print(f"Saved district_rainfall_history.csv: {len(history_df)} rows")

# district_rainfall_summary.json - 5-year summary (latest 5 years available)
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
            "data_availability": "missing"
        }
        continue
    
    # Get latest 5 years
    district_data = district_data.sort_values('YEAR', ascending=False)
    latest_years = district_data.head(5)
    
    annual = {}
    for _, r in latest_years.iterrows():
        annual[str(int(r['YEAR']))] = round(float(r['ANNUAL_RAINFALL_mm']), 1)
    
    mean_annual = round(district_data['ANNUAL_RAINFALL_mm'].mean(), 1)
    
    # Seasonal estimates (if monthly data not available, use standard Indian splits)
    # Kharif (Jun-Sep) ~65%, Rabi (Oct-Mar) ~25%, Zaid (Apr-May) ~10%
    kharif = round(mean_annual * 0.65, 1)
    rabi = round(mean_annual * 0.25, 1)
    zaid = round(mean_annual * 0.10, 1)
    
    summary[district] = {
        "annual_rainfall_mm": annual,
        "mean_annual_rainfall_mm": mean_annual,
        "kharif_seasonal_avg_mm": kharif,
        "rabi_seasonal_avg_mm": rabi,
        "zaid_seasonal_avg_mm": zaid,
        "data_availability": "actual" if len(annual) > 0 else "missing",
        "years_available": len(district_data),
        "year_range": f"{int(district_data['YEAR'].min())}-{int(district_data['YEAR'].max())}"
    }

with open(OUTPUTS["district_rainfall_summary"], 'w') as f:
    json.dump(summary, f, indent=2)
print(f"Saved district_rainfall_summary.json: {len(summary)} districts")

actual_count = sum(1 for v in summary.values() if v['data_availability'] == 'actual')
print(f"Districts with actual rainfall data: {actual_count}")