import pandas as pd
import json

# Check current raw data
rain = pd.read_csv('raw/rainfall_district_annual.csv')
print('Current rainfall raw:')
print('  Shape:', rain.shape)
print('  Columns:', list(rain.columns))
print('  Years:', rain['YEAR'].min(), '-', rain['YEAR'].max())
print('  Districts:', rain['DISTRICT'].nunique())
print('  States:', rain['STATE'].nunique())
print('  Sample:')
print(rain.head(3).to_string())

prod = pd.read_csv('raw/crop_production_district.csv')
print('\nCurrent production raw:')
print('  Shape:', prod.shape)
print('  Columns:', list(prod.columns))
print('  Years:', prod['YEAR'].min(), '-', prod['YEAR'].max())
print('  Crops:', prod['CROP'].nunique())
print('  Districts:', prod['DISTRICT'].nunique())
print('  Sample:')
print(prod.head(3).to_string())

yield_df = pd.read_csv('raw/crop_yield_district.csv')
print('\nCurrent yield raw:')
print('  Shape:', yield_df.shape)
print('  Columns:', list(yield_df.columns))
print('  Years:', yield_df['YEAR'].min(), '-', yield_df['YEAR'].max())
print('  Crops:', yield_df['CROP'].nunique())
print('  Sample:')
print(yield_df.head(3).to_string())