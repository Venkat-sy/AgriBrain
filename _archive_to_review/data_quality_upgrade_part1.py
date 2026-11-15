#!/usr/bin/env python
"""
Data Quality Upgrade - Part 1: Load existing data and document genuine sources
"""
import json
import pandas as pd
import numpy as np
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

DATASETS_DIR = Path(__file__).parent
RAW_DIR = DATASETS_DIR / "raw"
GEOJSON_PATH = DATASETS_DIR / "india_districts.geojson"

OUTPUTS = {
    "district_rainfall_summary": DATASETS_DIR / "district_rainfall_summary.json",
    "district_rainfall_history": DATASETS_DIR / "district_rainfall_history.csv",
    "master_agri_dataset": DATASETS_DIR / "master_agri_dataset.csv",
    "dataset_source_manifest": DATASETS_DIR / "dataset_source_manifest.json",
    "data_coverage_report": DATASETS_DIR / "DATA_COVERAGE_REPORT.md",
}

print("=" * 70)
print("PHASE 2 DATA QUALITY UPGRADE - Part 1: Load & Document")
print("=" * 70)

print("\n1. Loading existing pipeline outputs...")
with open(GEOJSON_PATH, 'r') as f:
    gj = json.load(f)

geo_df = pd.DataFrame([{
    'district_name': f['properties']['district_name'].strip(),
    'state_name': f['properties']['state_name'].strip(),
    'district_id': f['properties'].get('district_id', ''),
} for f in gj['features']])

print(f"   GeoJSON: {len(geo_df)} districts, {geo_df['state_name'].nunique()} states")

mapping = pd.read_csv(DATASETS_DIR / "district_name_mapping.csv")
print(f"   District mapping: {len(mapping)} source districts")

with open(DATASETS_DIR / "district_metadata.json", 'r') as f:
    metadata = json.load(f)
print(f"   District metadata: {len(metadata)} districts")

with open(DATASETS_DIR / "crop_agronomy_base.json", 'r') as f:
    crop_agronomy = json.load(f)
print(f"   Crop agronomy: {len(crop_agronomy)} crops")

rainfall_raw = pd.read_csv(RAW_DIR / "rainfall_district_annual.csv")
production_raw = pd.read_csv(RAW_DIR / "crop_production_district.csv")
yield_raw = pd.read_csv(RAW_DIR / "crop_yield_district.csv")

print(f"\n2. Current synthetic data coverage:")
print(f"   Rainfall: {rainfall_raw.shape[0]} records, {rainfall_raw['DISTRICT'].nunique()} districts, years {rainfall_raw['YEAR'].min()}-{rainfall_raw['YEAR'].max()}")
print(f"   Production: {production_raw.shape[0]} records, {production_raw['DISTRICT'].nunique()} districts, {production_raw['CROP'].nunique()} crops")
print(f"   Yield: {yield_raw.shape[0]} records, {yield_raw['CROP'].nunique()} crops")

# Save intermediate data for next parts
import pickle
intermediate = {
    'geo_df': geo_df,
    'mapping': mapping,
    'metadata': metadata,
    'crop_agronomy': crop_agronomy,
    'rainfall_raw': rainfall_raw,
    'production_raw': production_raw,
    'yield_raw': yield_raw,
}
with open(DATASETS_DIR / 'intermediate_data.pkl', 'wb') as f:
    pickle.dump(intermediate, f)
print("\n   Saved intermediate data for next parts")

print("\n3. Genuine Data Source Investigation Results:")
print("-" * 70)

genuine_sources = {
    "rainfall": {
        "source_name": "India Meteorological Department (IMD) - Climate Research & Services, Pune",
        "portal_url": "https://www.imdpune.gov.in",
        "data_supply_portal": "https://mausam.imd.gov.in (Data Supply Portal referenced)",
        "contact": "Shri Ranjan Phukan, Scientist D, +91 9435669264, ranjan.phukan@imd.gov.in",
        "available_formats": "Gridded NetCDF (0.25x0.25), Binary, Merged Gauge+GPM",
        "district_wise_access": "Not directly downloadable via public URLs. Requires formal request through Data Supply Portal or email contact.",
        "years_available": "Historical archive available, but district-wise 2021-2025 requires manual request",
        "status": "MANUAL_DOWNLOAD_REQUIRED",
        "notes": "Gridded data can be aggregated to districts using GeoJSON boundaries. No public CSV/Excel download for district-wise annual rainfall 2021-2025."
    },
    "crop_production": {
        "source_name": "Directorate of Economics & Statistics (DES), Ministry of Agriculture",
        "portal_url": "https://eands.dacnet.nic.in (may require VPN/institutional access)",
        "alternative_portal": "https://mospi.gov.in (MOSPI data portal)",
        "data_gov_in": "https://data.gov.in (district-wise crop production datasets exist but require API key)",
        "available_formats": "Excel, CSV via data.gov.in API",
        "years_available": "Latest agricultural years typically 2019-2023 (varies by state)",
        "status": "MANUAL_DOWNLOAD_REQUIRED",
        "notes": "District-wise crop production and yield data for 21 major crops. Requires data.gov.in API registration or manual download from DES publications."
    },
    "soil_data": {
        "source_name": "ICAR-NBSS&LUP (National Bureau of Soil Survey & Land Use Planning) & Soil Health Card Scheme",
        "portal_url": "https://www.nbsslup.in",
        "soil_health_card": "https://soilhealth.dac.gov.in",
        "icar_portal": "https://icar.org.in",
        "available_formats": "PDF reports, district soil maps, database access (institutional)",
        "district_coverage": "Partial - detailed soil profiles for benchmark districts, state-level generalizations elsewhere",
        "status": "INSTITUTIONAL_ACCESS_REQUIRED",
        "notes": "Actual measured soil data (NPK, pH, EC, OC, micronutrients) available only for benchmark districts. Most districts have estimated/regional values. Soil Health Card data requires state-level access."
    }
}

for category, info in genuine_sources.items():
    print(f"\n   {category.upper()}:")
    for key, value in info.items():
        print(f"     {key}: {value}")

# Save genuine sources for next parts
with open(DATASETS_DIR / 'genuine_sources.json', 'w') as f:
    json.dump(genuine_sources, f, indent=2)
print("\n   Saved genuine_sources.json for next parts")

print("\nPart 1 complete. Run Part 2 next.")