#!/usr/bin/env python
"""
Rebuild master dataset - Step 3: Merge crop data, rainfall, soil, agronomy
"""
import pandas as pd
import numpy as np
import geopandas as gpd
from pathlib import Path

DATASETS_DIR = Path(__file__).parent
PROCESSED_DIR = DATASETS_DIR / "processed"

# 1. Load master grid
master = pd.read_pickle(DATASETS_DIR / 'temp_master_grid.pkl')
print(f"Master grid: {master.shape}")

# 2. Recreate crop merged data
crop_prod = pd.read_csv(PROCESSED_DIR / "crop_production_district_icrisat.csv")
crop_yield = pd.read_csv(PROCESSED_DIR / "crop_yield_district_icrisat.csv")

crop_prod['canonical_key'] = crop_prod['district_name'].str.strip().str.upper() + '_' + crop_prod['state_name'].str.strip().str.upper()
crop_yield['canonical_key'] = crop_yield['district_name'].str.strip().str.upper() + '_' + crop_yield['state_name'].str.strip().str.upper()

crop_name_map = {'RICE': 'Rice', 'WHEAT': 'Wheat', 'MAIZE': 'Maize', 'SORGHUM': 'Sorghum',
    'PEARL MILLET': 'Pearl Millet', 'FINGER MILLET': 'Finger Millet', 'BARLEY': 'Barley',
    'KHARIF SORGHUM': 'Kharif Sorghum', 'RABI SORGHUM': 'Rabi Sorghum',
    'CHICKPEA': 'Chickpea', 'PIGEONPEA': 'Pigeonpea',
    'GREEN GRAM': 'Green Gram', 'BLACK GRAM': 'Black Gram',
    'LENTIL': 'Lentil', 'PEA': 'Pea',
    'GROUNDNUT': 'Groundnut', 'SOYABEAN': 'Soybean', 'SUNFLOWER': 'Sunflower',
    'SESAME': 'Sesame', 'SAFFLOWER': 'Safflower', 'LINSEED': 'Linseed',
    'CASTOR': 'Castor', 'RAPESEED AND MUSTARD': 'Rapeseed and Mustard',
    'COTTON': 'Cotton', 'JUTE': 'Jute', 'SUGARCANE': 'Sugarcane',
    'MINOR PULSES': 'Minor Pulses', 'OILSEEDS': 'Oilseeds',
    'BAJRA': 'Pearl Millet', 'RAGI': 'Finger Millet',
    'ARHAR': 'Pigeonpea', 'TUR': 'Pigeonpea',
    'GRAM': 'Chickpea', 'URAD': 'Black Gram', 'MOONG': 'Green Gram'}

crop_prod['crop_standard'] = crop_prod['crop'].map(crop_name_map).fillna(crop_prod['crop'])
crop_yield['crop_standard'] = crop_yield['crop'].map(crop_name_map).fillna(crop_yield['crop'])

crop_merged = pd.merge(crop_prod, crop_yield[['canonical_key', 'crop', 'year', 'yield_tons_per_ha']], on=['canonical_key', 'crop', 'year'], how='left', suffixes=('', '_yield'))
crop_merged_key = crop_merged[['canonical_key', 'crop_standard', 'year', 'area_ha', 'production_tonnes', 'yield_tons_per_ha', 'source', 'data_year']].copy()
crop_merged_key = crop_merged_key.rename(columns={'crop_standard': 'crop'})

# 3. Merge crop data
master = pd.merge(master, crop_merged_key, on=['canonical_key', 'crop', 'year'], how='left')
print(f"After crop merge: {master.shape}")

# 4. Load and merge rainfall
rainfall = pd.read_pickle(DATASETS_DIR / "temp_annual.pkl")
rainfall['canonical_key'] = rainfall['district_name'].str.strip().str.upper() + '_' + rainfall['state_name'].str.strip().str.upper()
rainfall_annual = rainfall.groupby(['canonical_key', 'year', 'source'])['annual_rainfall_mm'].sum().reset_index()
print(f"Rainfall annual records: {len(rainfall_annual)}")

master = pd.merge(master, rainfall_annual[['canonical_key', 'year', 'annual_rainfall_mm', 'source']], on=['canonical_key', 'year'], how='left')
print(f"After rainfall merge: {master.shape}")

# 5. Add soil data (add canonical_key to soil_df first)
soil_df = pd.read_csv(PROCESSED_DIR / "soil_features_district.csv")
soil_df['canonical_key'] = soil_df['district_name'].str.strip().str.upper() + '_' + soil_df['state_name'].str.strip().str.upper()
print(f"Soil data: {soil_df.shape}")
soil_cols = ['soil_ph', 'soil_organic_carbon_percent', 'soil_nitrogen_kg_per_ha',
    'soil_phosphorus_kg_per_ha', 'soil_potassium_kg_per_ha', 'soil_texture',
    'soil_data_source', 'soil_data_provenance', 'notes']
master = pd.merge(master, soil_df[['canonical_key'] + soil_cols], on='canonical_key', how='left')
print(f"After soil merge: {master.shape}")

# 6. Add crop agronomy
agronomy = pd.read_json(DATASETS_DIR / "crop_agronomy_base.json")
# Convert dict of dicts to DataFrame
agronomy_df = pd.DataFrame(agronomy).T
agronomy_df.index.name = 'crop'
agronomy_df = agronomy_df.reset_index()
print(f"Agronomy: {agronomy_df.shape}")
master = pd.merge(master, agronomy_df, on='crop', how='left')
print(f"After agronomy merge: {master.shape}")

# 7. Add provenance columns
# First check what columns exist
print("Columns before provenance:", master.columns.tolist())

# source_x is from crop merge, source_y is from rainfall merge
if 'source_x' in master.columns and 'source_y' in master.columns:
    master['crop_data_source'] = master.apply(lambda r: r['source_x'] if pd.notna(r.get('area_ha')) else 'MISSING - No ICRISAT data for this district/crop/year', axis=1)
    master['rainfall_data_source'] = master.apply(lambda r: r['source_y'] if pd.notna(r.get('annual_rainfall_mm')) else 'MISSING - No IMD rainfall for this district/year', axis=1)
elif 'source' in master.columns:
    master['crop_data_source'] = master.apply(lambda r: r['source'] if pd.notna(r.get('area_ha')) else 'MISSING - No ICRISAT data for this district/crop/year', axis=1)
    master['rainfall_data_source'] = master.apply(lambda r: r['source'] if pd.notna(r.get('annual_rainfall_mm')) else 'MISSING - No IMD rainfall for this district/year', axis=1)
else:
    master['crop_data_source'] = 'MISSING - No ICRISAT data for this district/crop/year'
    master['rainfall_data_source'] = 'MISSING - No IMD rainfall for this district/year'

master['soil_data_source'] = master['soil_data_provenance']
master = master.drop(columns=['source_x', 'source_y', 'data_year', 'soil_data_provenance', 'notes'], errors='ignore')

# 8. Save
output_path = DATASETS_DIR / "master_agri_dataset_v2.csv"
master.to_csv(output_path, index=False)
print(f"\nSaved master dataset: {output_path}")
print(f"Shape: {master.shape}")
master.to_pickle(DATASETS_DIR / "master_agri_dataset_v2.pkl")
print("Saved master_agri_dataset_v2.pkl")