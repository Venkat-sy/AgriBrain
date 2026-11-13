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

def fuzzy_match_districts(source_df, target_districts, source_name_col='DISTRICT', 
                          source_state_col='STATE', threshold=85):
    target_names = target_districts['district_name'].tolist()
    target_states = target_districts['state_name'].tolist()
    mappings = []
    for _, row in source_df.iterrows():
        src_name = str(row[source_name_col]).strip()
        src_state = str(row[source_state_col]).strip()
        exact_matches = target_districts[
            (target_districts['district_name'].str.lower() == src_name.lower()) & 
            (target_districts['state_name'].str.lower() == src_state.lower())
        ]
        if len(exact_matches) == 1:
            match = exact_matches.iloc[0]
            mappings.append({
                'source_district': src_name,
                'source_state': src_state,
                'canonical_district': match['district_name'],
                'canonical_state': match['state_name'],
                'match_method': 'exact',
                'match_score': 100,
                'district_id': match['district_id'],
            })
            continue
        state_mask = target_districts['state_name'].str.lower() == src_state.lower()
        state_districts = target_districts[state_mask]['district_name'].tolist()
        if len(state_districts) > 0:
            best_match, score = process.extractOne(src_name, state_districts, scorer=fuzz.ratio)
            if score >= threshold:
                match_row = target_districts[
                    (target_districts['district_name'] == best_match) & 
                    (target_districts['state_name'].str.lower() == src_state.lower())
                ].iloc[0]
                mappings.append({
                    'source_district': src_name,
                    'source_state': src_state,
                    'canonical_district': best_match,
                    'canonical_state': match_row['state_name'],
                    'match_method': 'fuzzy_state',
                    'match_score': score,
                    'district_id': match_row['district_id'],
                })
                continue
        best_match, score = process.extractOne(src_name, target_names, scorer=fuzz.ratio)
        if score >= threshold:
            match_row = target_districts[target_districts['district_name'] == best_match].iloc[0]
            mappings.append({
                'source_district': src_name,
                'source_state': src_state,
                'canonical_district': best_match,
                'canonical_state': match_row['state_name'],
                'match_method': 'fuzzy_all',
                'match_score': score,
                'district_id': match_row['district_id'],
            })
        else:
            mappings.append({
                'source_district': src_name,
                'source_state': src_state,
                'canonical_district': None,
                'canonical_state': None,
                'match_method': 'no_match',
                'match_score': score if 'score' in locals() else 0,
                'district_id': None,
            })
    return pd.DataFrame(mappings)

def load_raw_data():
    rainfall = pd.read_csv(RAW_DIR / 'rainfall_district_annual.csv')
    production = pd.read_csv(RAW_DIR / 'crop_production_district.csv')
    yield_df = pd.read_csv(RAW_DIR / 'crop_yield_district.csv')
    return rainfall, production, yield_df

print('Testing step 1...')
geo_df = load_geojson_districts()
rainfall, production, yield_df = load_raw_data()
rain_districts = rainfall[['DISTRICT', 'STATE']].drop_duplicates()
prod_districts = production[['DISTRICT', 'STATE']].drop_duplicates()
yield_districts = yield_df[['DISTRICT', 'STATE']].drop_duplicates()
all_source = pd.concat([rain_districts, prod_districts, yield_districts]).drop_duplicates().reset_index(drop=True)
print('GeoJSON districts:', len(geo_df))
print('Unique source districts:', len(all_source))
mapping = fuzzy_match_districts(all_source, geo_df)
mapping.to_csv('district_name_mapping.csv', index=False)
print('Saved mapping')
matched = mapping[mapping['match_method'] != 'no_match']
print('Matched:', len(matched), '/', len(mapping))
print('Match methods:', matched['match_method'].value_counts().to_dict())