import pandas as pd
import geopandas as gpd
import numpy as np
from pathlib import Path
import json

# ============================================================
# TASK 5: Process SoilGrids raw files into district-level features
# ============================================================

# Since no SoilGrids raw files were found (the soil/ directory is empty),
# we need to document this and create a placeholder that marks model-derived estimates
# But first, let's check if there are any other soil files

DATASETS_DIR = Path(__file__).parent
RAW_DIR = DATASETS_DIR / "raw"
PROCESSED_DIR = DATASETS_DIR / "processed"

print("Checking for soil files...")
for f in DATASETS_DIR.rglob("*"):
    if "soil" in f.name.lower() and f.is_file():
        print(f"  Found: {f}")

# Check if we have soil_characteristics.csv
soil_char = DATASETS_DIR / "soil_characteristics.csv"
if soil_char.exists():
    df_soil = pd.read_csv(soil_char)
    print(f"\nsoil_characteristics.csv: {df_soil.shape}")
    print(df_soil.head())
    print(df_soil.columns.tolist())
else:
    print("\nNo soil_characteristics.csv found")

# ============================================================
# Create proper soil features from available data
# Since we have NO genuine district-level soil data, we must document this
# and create a placeholder with clear provenance marking
# ============================================================

# Load canonical districts
districts = gpd.read_file(DATASETS_DIR / "india_districts.geojson")
districts['canonical_key'] = districts['district_name'].str.strip().str.upper() + '_' + districts['state_name'].str.strip().str.upper()

# Create soil dataframe with clear synthetic provenance
soil_rows = []
for _, row in districts.iterrows():
    soil_rows.append({
        'district_name': row['district_name'],
        'state_name': row['state_name'],
        'district_id': row['district_id'],
        'soil_ph': np.nan,  # No genuine data
        'soil_organic_carbon_percent': np.nan,
        'soil_nitrogen_kg_per_ha': np.nan,
        'soil_phosphorus_kg_per_ha': np.nan,
        'soil_potassium_kg_per_ha': np.nan,
        'soil_texture': 'UNKNOWN',
        'soil_data_source': 'MISSING - No genuine district-level soil data available',
        'soil_data_provenance': 'NOT_AVAILABLE',
        'notes': 'SoilGrids raw files not found; NBSS&LUP/ICAR data not acquired'
    })

soil_df = pd.DataFrame(soil_rows)
output_path = PROCESSED_DIR / "soil_features_district.csv"
soil_df.to_csv(output_path, index=False)
print(f"\nCreated {output_path} with {len(soil_df)} districts")
print("All values NaN - clearly marked as MISSING genuine data")

# Also save a manifest
manifest = {
    "soil_data_status": "NO_GENUINE_DATA",
    "sources_checked": [
        "SoilGrids 250m rasters (ISRIC) - raw files not downloaded",
        "NBSS&LUP District Soil Profiles (ICAR) - no access",
        "ICAR-IISS Soil Health Cards - API not accessible"
    ],
    "current_file": str(output_path),
    "provenance": "All values NaN - explicitly marked as missing genuine data",
    "action_required": "Acquire SoilGrids rasters or NBSS&LUP profiles and aggregate to 641 districts"
}

with open(PROCESSED_DIR / "soil_data_manifest.json", 'w') as f:
    json.dump(manifest, f, indent=2)
print(f"Created soil_data_manifest.json")