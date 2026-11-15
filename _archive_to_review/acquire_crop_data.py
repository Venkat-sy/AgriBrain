#!/usr/bin/env python
"""
Acquire Genuine District-Wise Crop Production & Yield Data

Pipeline for acquiring, processing, and integrating genuine DES district-wise 
crop production and yield data for all 641 districts and 21 major crops 
for the latest 5 agricultural years (2019-2023).

CRITICAL: Requires manual data acquisition from:
1. data.gov.in API (requires API key registration)
2. DES publications (https://eands.dacnet.nic.in - may need institutional access)
3. MOSPI data portal (https://mospi.gov.in)

Author: AgriSim Data Pipeline
Date: 2026-11-07
"""

import os
import json
import pandas as pd
import geopandas as gpd
from pathlib import Path
from datetime import datetime

DATASETS_DIR = Path(__file__).parent
RAW_DIR = DATASETS_DIR / "raw"
PROCESSED_DIR = DATASETS_DIR / "processed"
PROCESSED_DIR.mkdir(exist_ok=True)

TARGET_CROPS = [
    "Rice", "Wheat", "Maize", "Barley", "Sorghum", "Pearl Millet", "Finger Millet",
    "Chickpea", "Pigeon Pea", "Moong", "Urad", "Lentil", "Pea",
    "Groundnut", "Soybean", "Sesame", "Rapeseed & Mustard", "Sunflower", "Safflower",
    "Cotton", "Sugarcane"
]

TARGET_YEARS = [2019, 2020, 2021, 2022, 2023]
DISTRICT_REGISTRY = DATASETS_DIR / "india_districts.geojson"

# =============================================================================
# STEP 1: DATA ACQUISITION GUIDE
# =============================================================================
def print_acquisition_guide():
    """Print detailed manual acquisition instructions."""
    print("=" * 80)
    print("MANUAL DATA ACQUISITION REQUIRED")
    print("=" * 80)
    print()
    print("SOURCE: Directorate of Economics & Statistics (DES), Ministry of Agriculture")
    print()
    print("METHOD 1: data.gov.in API (RECOMMENDED)")
    print("-" * 40)
    print("1. Register for API key at https://data.gov.in/apis")
    print("2. Search for datasets:")
    print("   - 'District-wise crop production' (Dataset ID likely: 9ef84268-d588-465a-a308-a864a43d0070)")
    print("   - 'District-wise crop yield'")
    print("   - 'District-wise area under crops'")
    print("3. Use CKAN API: https://api.data.gov.in/resource/<dataset_id>?format=json&limit=100000")
    print("4. Download full datasets as CSV/Excel")
    print()
    print("METHOD 2: DES Publications (ANNUAL)")
    print("-" * 40)
    print("1. Visit https://eands.dacnet.nic.in (may require VPN/institutional access)")
    print("2. Navigate to 'Publications' -> 'Agricultural Statistics at a Glance'")
    print("3. Download 'District-wise Crop Production Statistics' Excel files")
    print("4. Available for years: 2019-20, 2020-21, 2021-22, 2022-23, 2023-24")
    print()
    print("METHOD 3: MOSPI Data Portal")
    print("-" * 40)
    print("1. Visit https://mospi.gov.in")
    print("2. Search for 'district-wise crop production'")
    print("3. Download relevant datasets")
    print()
    print("REQUIRED COLUMNS IN SOURCE DATA:")
    print("-" * 40)
    print("For PRODUCTION data:")
    print("  District, State, Crop, Year, Area (ha), Production (tonnes)")
    print("  (Yield = Production / Area will be calculated)")
    print()
    print("For YIELD data:")
    print("  District, State, Crop, Year, Yield (tonnes/ha)")
    print()
    print("EXPECTED OUTPUT FILES:")
    print("-" * 40)
    print("1. raw/crop_production_district_GENUINE.csv")
    print("2. raw/crop_yield_district_GENUINE.csv")
    print("3. processed/crop_production_district.csv (canonical)")
    print("4. processed/crop_yield_district.csv (canonical)")
    print("5. processed/crop_data_coverage.csv")
    print("6. processed/dataset_source_manifest.json (updated)")
    print("7. processed/CROP_DATA_COVERAGE_REPORT.md")
    print()


# =============================================================================
# STEP 2: CANONICAL NAME MATCHING
# =============================================================================
def load_canonical_districts():
    """Load and prepare canonical district registry."""
    gdf = gpd.read_file(DISTRICT_REGISTRY)
    gdf['canonical_key'] = gdf['district_name'].str.strip().str.upper() + '_' + gdf['state_name'].str.strip().str.upper()
    gdf['district_only'] = gdf['district_name'].str.strip().str.upper()
    gdf['state_only'] = gdf['state_name'].str.strip().str.upper()
    return gdf


def create_name_mapping(source_districts, source_states, canonical_gdf):
    """Map source district/state names to canonical names."""
    mapping = {}
    canonical_keys = set(canonical_gdf['canonical_key'].values)
    
    for s_dist, s_state in zip(source_districts, source_states):
        s_key = s_dist.strip().upper() + '_' + s_state.strip().upper()
        
        if s_key in canonical_keys:
            match = canonical_gdf[canonical_gdf['canonical_key'] == s_key].iloc[0]
            mapping[(s_dist, s_state)] = (match['district_name'], match['state_name'], match['district_id'])
            continue
        
        district_matches = canonical_gdf[
            (canonical_gdf['state_only'] == s_state.strip().upper()) &
            (canonical_gdf['district_only'].str.contains(s_dist.strip().upper(), regex=False))
        ]
        if len(district_matches) == 1:
            match = district_matches.iloc[0]
            mapping[(s_dist, s_state)] = (match['district_name'], match['state_name'], match['district_id'])
            continue
        
        state_matches = canonical_gdf[
            (canonical_gdf['district_only'] == s_dist.strip().upper()) &
            (canonical_gdf['state_only'].str.contains(s_state.strip().upper(), regex=False))
        ]
        if len(state_matches) == 1:
            match = state_matches.iloc[0]
            mapping[(s_dist, s_state)] = (match['district_name'], match['state_name'], match['district_id'])
            continue
        
        mapping[(s_dist, s_state)] = (None, None, None)
    
    return mapping
SOURCE_INFO = {
    "source_name": "Directorate of Economics & Statistics (DES), Ministry of Agriculture",
    "portal_url": "https://eands.dacnet.nic.in",
    "alternative_portal": "https://mospi.gov.in",
    "data_gov_in": "https://data.gov.in",
    "available_formats": "Excel, CSV via data.gov.in API or DES annual publications",
    "years_available": "Latest agricultural years typically 2019-2023 (varies by state)",
    "status": "MANUAL_DOWNLOAD_REQUIRED",
    "notes": "District-wise crop production and yield data for 21 major crops. Requires data.gov.in API registration or manual download from DES publications."
}