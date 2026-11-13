#!/usr/bin/env python
"""
Step 1: Load ICRISAT data and transform to long format.
"""
import pandas as pd
from pathlib import Path

DATASETS_DIR = Path(__file__).parent
PROCESSED_DIR = DATASETS_DIR / "processed"
PROCESSED_DIR.mkdir(exist_ok=True)


def transform_icrisat_to_long(icrisat_file):
    """Transform ICRISAT wide format to long format."""
    print("Loading ICRISAT data...")
    df = pd.read_csv(icrisat_file)
    print(f"  Records: {len(df)}")
    print(f"  Columns: {len(df.columns)}")
    print(f"  Years: {df['Year'].min()}-{df['Year'].max()}")
    print(f"  States: {df['State Name'].nunique()}")
    print(f"  Districts: {df['Dist Name'].nunique()}")
    
    # Melt the data - each crop has AREA, PRODUCTION, YIELD columns
    id_vars = ['Dist Code', 'Year', 'State Code', 'State Name', 'Dist Name']
    
    # Find all crop columns
    area_cols = [c for c in df.columns if 'AREA' in c and '(1000 ha)' in c]
    prod_cols = [c for c in df.columns if 'PRODUCTION' in c and '(1000 tons)' in c]
    yield_cols = [c for c in df.columns if 'YIELD' in c and 'Kg per ha' in c]
    
    print(f"  Area columns: {len(area_cols)}")
    print(f"  Production columns: {len(prod_cols)}")
    print(f"  Yield columns: {len(yield_cols)}")
    
    # Build crop mapping from column names
    crop_map = {}
    for col in area_cols:
        crop_name = col.replace(' AREA (1000 ha)', '')
        crop_map[crop_name] = {'area': col}
    
    for col in prod_cols:
        crop_name = col.replace(' PRODUCTION (1000 tons)', '')
        if crop_name in crop_map:
            crop_map[crop_name]['production'] = col
    
    for col in yield_cols:
        crop_name = col.replace(' YIELD (Kg per ha)', '')
        if crop_name in crop_map:
            crop_map[crop_name]['yield'] = col
    
    print(f"  Crops with all 3 metrics: {len([c for c in crop_map if all(k in crop_map[c] for k in ['area', 'production', 'yield'])])}")
    
    # Melt to long format
    long_records = []
    for crop_key, cols in crop_map.items():
        if not all(k in cols for k in ['area', 'production', 'yield']):
            continue
            
        temp = df[id_vars + [cols['area'], cols['production'], cols['yield']]].copy()
        temp = temp.rename(columns={
            cols['area']: 'area_1000ha',
            cols['production']: 'production_1000tons',
            cols['yield']: 'yield_kg_per_ha'
        })
        temp['crop'] = crop_key
        long_records.append(temp)
    
    long_df = pd.concat(long_records, ignore_index=True)
    print(f"  Long format records: {len(long_df)}")
    
    # Convert units: 1000 ha -> ha, 1000 tons -> tonnes, kg/ha -> tonnes/ha
    long_df['area_ha'] = (long_df['area_1000ha'] * 1000).round(1)
    long_df['production_tonnes'] = (long_df['production_1000tons'] * 1000).round(1)
    long_df['yield_tons_per_ha'] = (long_df['yield_kg_per_ha'] / 1000).round(3)
    
    # Filter out zero/negative values
    long_df = long_df[(long_df['area_ha'] > 0) & (long_df['production_tonnes'] > 0)]
    print(f"  After filtering zero values: {len(long_df)}")
    
    # Rename columns to standard format
    long_df = long_df.rename(columns={
        'Dist Name': 'DISTRICT',
        'State Name': 'STATE',
        'Year': 'YEAR'
    })
    
    # Select final columns
    final_cols = ['DISTRICT', 'STATE', 'crop', 'YEAR', 'area_ha', 'production_tonnes', 'yield_tons_per_ha']
    long_df = long_df[final_cols]
    
    # Save intermediate
    long_df.to_csv(PROCESSED_DIR / "icrisat_long_format.csv", index=False)
    print(f"  Saved intermediate: icrisat_long_format.csv")
    
    return long_df, crop_map


if __name__ == "__main__":
    icrisat_file = DATASETS_DIR / "ICRISAT-District Level Data.csv"
    long_df, crop_map = transform_icrisat_to_long(icrisat_file)
    print("Step 1 complete.")