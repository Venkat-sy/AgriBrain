#!/usr/bin/env python
import pandas as pd
import geopandas as gpd
from pathlib import Path

DATASETS_DIR = Path(__file__).parent
PROCESSED_DIR = DATASETS_DIR / "processed"
DISTRICT_REGISTRY = DATASETS_DIR / "india_districts.geojson"

gdf = gpd.read_file(DISTRICT_REGISTRY)
gdf['canonical_key'] = gdf['district_name'].str.strip().str.upper() + '_' + gdf['state_name'].str.strip().str.upper()
gdf['district_only'] = gdf['district_name'].str.strip().str.upper()
gdf['state_only'] = gdf['state_name'].str.strip().str.upper()
print('Canonical districts:', len(gdf))

long_df = pd.read_csv(PROCESSED_DIR / 'icrisat_long_format.csv')
print('Long format:', len(long_df))

unique_districts = long_df[['DISTRICT', 'STATE']].drop_duplicates()
print('Unique ICRISAT districts:', len(unique_districts))

canonical_keys = set(gdf['canonical_key'].values)
mapping = {}
exact = 0
fuzzy_state = 0
fuzzy_all = 0
nomatch = 0

for s_dist, s_state in zip(unique_districts['DISTRICT'].values, unique_districts['STATE'].values):
    s_key = s_dist.strip().upper() + '_' + s_state.strip().upper()
    if s_key in canonical_keys:
        match = gdf[gdf['canonical_key'] == s_key].iloc[0]
        mapping[(s_dist, s_state)] = (match['district_name'], match['state_name'], match['district_id'])
        exact += 1
        continue
    district_matches = gdf[(gdf['state_only'] == s_state.strip().upper()) & (gdf['district_only'].str.contains(s_dist.strip().upper(), regex=False))]
    if len(district_matches) == 1:
        match = district_matches.iloc[0]
        mapping[(s_dist, s_state)] = (match['district_name'], match['state_name'], match['district_id'])
        fuzzy_state += 1
        continue
    state_matches = gdf[(gdf['district_only'] == s_dist.strip().upper()) & (gdf['state_only'].str.contains(s_state.strip().upper(), regex=False))]
    if len(state_matches) == 1:
        match = state_matches.iloc[0]
        mapping[(s_dist, s_state)] = (match['district_name'], match['state_name'], match['district_id'])
        fuzzy_all += 1
        continue
    mapping[(s_dist, s_state)] = (None, None, None)
    nomatch += 1

print(f'Exact: {exact}, Fuzzy state: {fuzzy_state}, Fuzzy all: {fuzzy_all}, No match: {nomatch}')

# Show unmatched
unmatched = [(k[0], k[1]) for k, v in mapping.items() if v[0] is None]
print(f"\nUnmatched districts ({len(unmatched)}):")
for d, s in unmatched[:30]:
    print(f"  {d}, {s}")

# Save mapping
import json
mapping_serializable = {f"{k[0]}|{k[1]}": {"canonical_district": v[0], "canonical_state": v[1], "district_id": v[2]} for k, v in mapping.items()}
with open(PROCESSED_DIR / 'icrisat_mapping.json', 'w') as f:
    json.dump(mapping_serializable, f, indent=2)
print("\nMapping saved to icrisat_mapping.json")