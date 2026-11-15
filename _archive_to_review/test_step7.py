#!/usr/bin/env python
import json
import pandas as pd
import numpy as np
from pathlib import Path

DATASETS_DIR = Path('c:/Users/USER/Downloads/FinalYearProject/datasets')
OUTPUTS = {
    'dataset_source_manifest': DATASETS_DIR / 'dataset_source_manifest.json',
    'data_coverage_report': DATASETS_DIR / 'DATA_COVERAGE_REPORT.md'
}

mapping = pd.read_csv('district_name_mapping.csv')

# Load geo_df
with open(DATASETS_DIR / 'india_districts.geojson', 'r') as f:
    gj = json.load(f)
geo_df = pd.DataFrame([{'district_name': f['properties']['district_name'].strip(), 'state_name': f['properties']['state_name'].strip(), 'district_id': f['properties'].get('district_id', '')} for f in gj['features']])

# Load metadata
with open(DATASETS_DIR / 'district_metadata.json', 'r') as f:
    metadata = json.load(f)

# Load master dataset
master_df = pd.read_csv('master_agri_dataset.csv')

# Load rainfall summary
with open(DATASETS_DIR / 'district_rainfall_summary.json', 'r') as f:
    rainfall_summary = json.load(f)

print('STEP 7: Building dataset source manifest')

manifest = {
    'generated_at': pd.Timestamp.now().isoformat(),
    'geojson_source': {
        'source': 'DataMeet/maps - Census 2011 Districts',
        'url': 'https://github.com/datameet/maps/tree/master/Districts/Census_2011',
        'license': 'CC BY 4.0',
        'districts_count': len(geo_df),
        'states_count': geo_df['state_name'].nunique(),
    },
    'rainfall_data': {
        'source': 'Synthetic/placeholder (IMD data.gov.in download failed)',
        'years_available': '2000-2019',
        'districts_with_data': 10,
        'note': 'Genuine IMD district-wise rainfall for 2021-2025 could not be automatically downloaded. Manual download required from https://www.imdpune.gov.in or data.gov.in'
    },
    'crop_production_data': {
        'source': 'Synthetic/placeholder (DES data.gov.in download failed)',
        'years_available': '2000-2019',
        'crops': 8,
        'districts_with_data': 10,
        'note': 'Genuine DES district-wise crop production could not be automatically downloaded. Manual download required from data.gov.in'
    },
    'crop_yield_data': {
        'source': 'Synthetic/placeholder (DES data.gov.in download failed)',
        'years_available': '2000-2019',
        'crops': 8,
        'districts_with_data': 10,
        'note': 'Genuine DES district-wise crop yield could not be automatically downloaded. Manual download required from data.gov.in'
    },
    'soil_data': {
        'source': 'Known data for 10 canonical districts + state-level defaults',
        'districts_with_actual_data': 10,
        'districts_with_estimated_data': sum(1 for v in metadata.values() if v['soil_data_availability'] == 'estimated'),
        'districts_missing_data': sum(1 for v in metadata.values() if v['soil_data_availability'] == 'missing'),
        'note': 'Genuine ICAR/NBSS&LUP district-wise soil data could not be automatically downloaded. Requires access to Soil Health Card portal or ICAR datasets.'
    },
    'crop_agronomy': {
        'source': 'ICAR Package of Practices for 21 major crops',
        'crops_count': 21,
        'data_type': 'Agronomic ranges (not district-specific measurements)'
    },
    'district_name_mapping': {
        'total_source_districts': len(mapping),
        'exact_matches': len(mapping[mapping['match_method'] == 'exact']),
        'fuzzy_state_matches': len(mapping[mapping['match_method'] == 'fuzzy_state']),
        'fuzzy_all_matches': len(mapping[mapping['match_method'] == 'fuzzy_all']),
        'no_matches': len(mapping[mapping['match_method'] == 'no_match']),
    },
    'master_dataset': {
        'total_rows': len(master_df),
        'unique_districts': master_df['district_name'].nunique(),
        'unique_crops': master_df['crop'].nunique(),
        'year_range': str(int(master_df['year'].min())) + '-' + str(int(master_df['year'].max())),
        'records_with_actual_soil': len(master_df[master_df['soil_data_availability'] == 'actual']),
        'records_with_estimated_soil': len(master_df[master_df['soil_data_availability'] == 'estimated']),
        'records_missing_soil': len(master_df[master_df['soil_data_availability'] == 'missing']),
    }
}

with open(OUTPUTS['dataset_source_manifest'], 'w') as f:
    json.dump(manifest, f, indent=2)

print('Saved dataset_source_manifest.json')