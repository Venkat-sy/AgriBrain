#!/usr/bin/env python
import json
import pandas as pd
import numpy as np
from pathlib import Path

DATASETS_DIR = Path(__file__).parent
RAW_DIR = DATASETS_DIR / 'raw'
GEOJSON_PATH = DATASETS_DIR / 'india_districts.geojson'

mapping = pd.read_csv('district_name_mapping.csv')

print("STEP 3: Building crop production & yield datasets with canonical names")

production = pd.read_csv(RAW_DIR / "crop_production_district.csv")
yield_df = pd.read_csv(RAW_DIR / "crop_yield_district.csv")

# Apply mapping to production
prod_mapped = production.merge(
    mapping[['source_district', 'source_state', 'canonical_district', 'canonical_state', 'district_id']],
    left_on=['DISTRICT', 'STATE'],
    right_on=['source_district', 'source_state'],
    how='left'
)

# Apply mapping to yield
yield_mapped = yield_df.merge(
    mapping[['source_district', 'source_state', 'canonical_district', 'canonical_state', 'district_id']],
    left_on=['DISTRICT', 'STATE'],
    right_on=['source_district', 'source_state'],
    how='left'
)

matched_prod = prod_mapped[prod_mapped['canonical_district'].notna()].copy()
matched_yield = yield_mapped[yield_mapped['canonical_district'].notna()].copy()

print(f"Mapped production records: {len(matched_prod)}/{len(production)}")
print(f"Mapped yield records: {len(matched_yield)}/{len(yield_df)}")

# Save with canonical names
prod_out = matched_prod[['canonical_district', 'canonical_state', 'CROP', 'YEAR', 
                          'AREA_HA', 'PRODUCTION_TONNES', 'YIELD_TONNES_PER_HA', 'district_id']].copy()
prod_out.columns = ['district_name', 'state_name', 'crop', 'year', 
                     'area_ha', 'production_tonnes', 'yield_tons_per_ha', 'district_id']
prod_out.to_csv(RAW_DIR / "crop_production_district_canonical.csv", index=False)

yield_out = matched_yield[['canonical_district', 'canonical_state', 'CROP', 'YEAR', 
                            'YIELD_TONNES_PER_HA', 'district_id']].copy()
yield_out.columns = ['district_name', 'state_name', 'crop', 'year', 
                      'yield_tons_per_ha', 'district_id']
yield_out.to_csv(RAW_DIR / "crop_yield_district_canonical.csv", index=False)

print(f"Saved canonical crop datasets")
print(f"Production columns: {list(prod_out.columns)}")
print(f"Yield columns: {list(yield_out.columns)}")
print(f"Unique crops in production: {prod_out['crop'].unique()}")
print(f"Unique crops in yield: {yield_out['crop'].unique()}")