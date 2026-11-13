import pandas as pd
import os

# Check the raw data files we already have
raw_files = [
    'raw/rainfall_district_annual.csv',
    'raw/crop_production_district.csv',
    'raw/crop_yield_district.csv'
]

for f in raw_files:
    if os.path.exists(f):
        df = pd.read_csv(f)
        print(f + ': ' + str(df.shape[0]) + ' rows, ' + str(df.shape[1]) + ' cols')
        print('  Columns: ' + str(list(df.columns)))
        if 'Year' in df.columns:
            print('  Year range: ' + str(df['Year'].min()) + '-' + str(df['Year'].max()))
        if 'District' in df.columns:
            print('  Unique districts: ' + str(df['District'].nunique()))
        print()
    else:
        print(f + ': NOT FOUND')