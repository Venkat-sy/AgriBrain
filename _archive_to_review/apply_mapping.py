#!/usr/bin/env python
"""
Apply the mapping with manual corrections for unmatched ICRISAT districts.
"""
import pandas as pd
import geopandas as gpd
import json
from pathlib import Path

DATASETS_DIR = Path(__file__).parent
PROCESSED_DIR = DATASETS_DIR / "processed"
DISTRICT_REGISTRY = DATASETS_DIR / "india_districts.geojson"

# Load canonical districts
gdf = gpd.read_file(DISTRICT_REGISTRY)
gdf['canonical_key'] = gdf['district_name'].str.strip().str.upper() + '_' + gdf['state_name'].str.strip().str.upper()
gdf['district_only'] = gdf['district_name'].str.strip().str.upper()
gdf['state_only'] = gdf['state_name'].str.strip().str.upper()

# Load mapping
with open(PROCESSED_DIR / 'icrisat_mapping.json', 'r') as f:
    mapping = json.load(f)

# Convert back to tuple keys (use uppercase for consistent lookup)
mapping_dict = {}
for k, v in mapping.items():
    parts = k.split('|')
    mapping_dict[(parts[0].strip().upper(), parts[1].strip().upper())] = (v['canonical_district'], v['canonical_state'], v['district_id'])

# Manual corrections for unmatched districts
from manual_corrections import MANUAL_CORRECTIONS

# Apply manual corrections
corrected = 0
for (src_dist, src_state), (canon_dist, canon_state) in MANUAL_CORRECTIONS.items():
    matches = gdf[(gdf['district_name'] == canon_dist) & (gdf['state_name'] == canon_state)]
    if len(matches) == 1:
        dist_id = matches.iloc[0]['district_id']
        mapping_dict[(src_dist, src_state)] = (canon_dist, canon_state, dist_id)
        corrected += 1
    else:
        print(f"Warning: No unique match for {canon_dist}, {canon_state}: {len(matches)} matches")

print(f"Applied {corrected} manual corrections")

# Check remaining unmatched
unmatched = [(k[0], k[1]) for k, v in mapping_dict.items() if v[0] is None]
print(f"Remaining unmatched: {len(unmatched)}")
for d, s in unmatched:
    print(f"  {d}, {s}")

# Now apply to long format data
long_df = pd.read_csv(PROCESSED_DIR / "icrisat_long_format.csv")
print(f"Long format records: {len(long_df)}")

def get_canonical(row):
    key = (row['DISTRICT'].strip().upper(), row['STATE'].strip().upper())
    if key in mapping_dict:
        canon_dist, canon_state, dist_id = mapping_dict[key]
        return pd.Series({'district_name': canon_dist, 'state_name': canon_state, 'district_id': dist_id})
    return pd.Series({'district_name': None, 'state_name': None, 'district_id': None})

canonical_cols = long_df.apply(get_canonical, axis=1)
long_df = pd.concat([long_df, canonical_cols], axis=1)

mapped = long_df['district_id'].notna().sum()
unmapped = long_df['district_id'].isna().sum()
print(f"Mapped: {mapped} records ({mapped/len(long_df)*100:.1f}%)")
print(f"Unmapped: {unmapped} records ({unmapped/len(long_df)*100:.1f}%)")

# Keep only mapped records
mapped_df = long_df[long_df['district_id'].notna()].copy()
mapped_df['district_id'] = mapped_df['district_id'].astype(int)
mapped_df['source'] = 'icrisat_district_observation'
mapped_df['data_year'] = '2026-11-07'

# Rename columns
mapped_df = mapped_df.rename(columns={
    'crop': 'crop',
    'YEAR': 'year',
    'area_ha': 'area_ha',
    'production_tonnes': 'production_tonnes',
    'yield_tons_per_ha': 'yield_tons_per_ha'
})

final_cols = ['district_name', 'state_name', 'crop', 'year', 'area_ha', 
              'production_tonnes', 'yield_tons_per_ha', 'district_id', 'source', 'data_year']
mapped_df = mapped_df[final_cols]

# Save
mapped_df.to_csv(PROCESSED_DIR / "crop_production_district_icrisat.csv", index=False)
print(f"Production: {len(mapped_df)} records -> crop_production_district_icrisat.csv")

# Yield data
yield_df = mapped_df[['district_name', 'state_name', 'crop', 'year', 'yield_tons_per_ha', 'district_id', 'source', 'data_year']].copy()
yield_df.to_csv(PROCESSED_DIR / "crop_yield_district_icrisat.csv", index=False)
print(f"Yield: {len(yield_df)} records -> crop_yield_district_icrisat.csv")

# Mapping summary
mapping_df = pd.DataFrame([
    {'source_district': k[0], 'source_state': k[1], 
     'canonical_district': v[0], 'canonical_state': v[1], 'district_id': v[2]}
    for k, v in mapping_dict.items()
])
mapping_df.to_csv(PROCESSED_DIR / "icrisat_district_mapping.csv", index=False)
print(f"Mapping: {len(mapping_df)} entries -> icrisat_district_mapping.csv")

# Coverage summary
coverage = mapped_df.groupby(['district_name', 'state_name', 'crop', 'year']).size().reset_index(name='records')
pivot = coverage.pivot_table(
    index=['district_name', 'state_name'],
    columns='crop',
    values='records',
    aggfunc='count',
    fill_value=0
).reset_index()
pivot.to_csv(PROCESSED_DIR / "icrisat_coverage_matrix.csv", index=False)
print(f"Coverage matrix: {len(pivot)} districts x {len([c for c in pivot.columns if c not in ['district_name', 'state_name']])} crops")

# Summary
print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
print(f"Source: ICRISAT District Level Data (1978-2017)")
print(f"Production records: {len(mapped_df)}")
print(f"Unique districts: {mapped_df['district_id'].nunique()}")
print(f"Unique crops: {mapped_df['crop'].nunique()}")
print(f"Year range: {mapped_df['year'].min()}-{mapped_df['year'].max()}")
print(f"Crops: {sorted(mapped_df['crop'].unique())}")
print("\nNote: ICRISAT data covers 1978-2017. Target years 2019-2023 require separate acquisition.")