#!/usr/bin/env python
import json
import pandas as pd
import numpy as np
from pathlib import Path

print('VERIFICATION CHECKS')
print('=' * 60)

DATASETS_DIR = Path('c:/Users/USER/Downloads/FinalYearProject/datasets')
issues = []

# 1. GeoJSON validation
with open(DATASETS_DIR / 'india_districts.geojson', 'r') as f:
    gj = json.load(f)

district_names = [f['properties']['district_name'] for f in gj['features']]
if len(district_names) != len(set(district_names)):
    issues.append('Duplicate district names in GeoJSON')

if len(gj['features']) != 641:
    issues.append('Expected 641 districts, got ' + str(len(gj['features'])))

print('GeoJSON: ' + str(len(gj['features'])) + ' features, ' + str(len(set(district_names))) + ' unique names')

# 2. Check all output files exist
outputs = {
    'district_metadata': DATASETS_DIR / 'district_metadata.json',
    'district_rainfall_summary': DATASETS_DIR / 'district_rainfall_summary.json',
    'crop_agronomy_base': DATASETS_DIR / 'crop_agronomy_base.json',
    'master_agri_dataset': DATASETS_DIR / 'master_agri_dataset.csv',
    'district_rainfall_history': DATASETS_DIR / 'district_rainfall_history.csv',
    'district_name_mapping': DATASETS_DIR / 'district_name_mapping.csv',
    'dataset_source_manifest': DATASETS_DIR / 'dataset_source_manifest.json',
    'data_coverage_report': DATASETS_DIR / 'DATA_COVERAGE_REPORT.md',
}

for name, path in outputs.items():
    if path.exists():
        size = path.stat().st_size
        print(name + ': ' + str(size) + ' bytes')
    else:
        issues.append('Missing output file: ' + name + ' at ' + str(path))

# 3. Master dataset validation
master = pd.read_csv(DATASETS_DIR / 'master_agri_dataset.csv')
dup = master.duplicated(subset=['district_name', 'crop', 'year']).sum()
if dup > 0:
    issues.append('Master dataset has ' + str(dup) + ' duplicate (district, crop, year) rows')

# Check yield ranges
with open(DATASETS_DIR / 'crop_agronomy_base.json', 'r') as f:
    crop_ag = json.load(f)

for crop in master['crop'].unique():
    if crop in crop_ag:
        y_min, y_max = crop_ag[crop]['yield_range_tons_per_ha']
        crop_yields = master[master['crop'] == crop]['yield_tons_per_ha']
        if crop_yields.min() < y_min * 0.5 or crop_yields.max() > y_max * 1.5:
            issues.append('Crop ' + crop + ' yields outside expected range: ' + str(crop_yields.min()) + '-' + str(crop_yields.max()) + ' vs ' + str(y_min) + '-' + str(y_max))

# Check null handling
null_soil = master['soil_N_kg_per_ha'].isna().sum()
if null_soil == 0 and master['soil_data_availability'].str.contains('missing').any():
    issues.append('Soil data marked missing but no null values in NPK columns')

print('Master dataset: ' + str(len(master)) + ' rows, ' + str(dup) + ' duplicates')
print('Null soil values: ' + str(null_soil))

# 4. District coverage verification
with open(DATASETS_DIR / 'district_rainfall_summary.json', 'r') as f:
    rain_summary = json.load(f)

missing_in_rain = set(district_names) - set(rain_summary.keys())
if missing_in_rain:
    issues.append('Districts missing from rainfall summary: ' + str(len(missing_in_rain)))

with open(DATASETS_DIR / 'district_metadata.json', 'r') as f:
    meta = json.load(f)

missing_in_meta = set(district_names) - set(meta.keys())
if missing_in_meta:
    issues.append('Districts missing from metadata: ' + str(len(missing_in_meta)))

print('Rainfall summary coverage: ' + str(len(rain_summary)) + '/' + str(len(district_names)))
print('Metadata coverage: ' + str(len(meta)) + '/' + str(len(district_names)))

if issues:
    print('\nVERIFICATION ISSUES FOUND:')
    for issue in issues:
        print('  - ' + issue)
else:
    print('\nALL VERIFICATION CHECKS PASSED')