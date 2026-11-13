import pandas as pd
import numpy as np
import geopandas as gpd
from pathlib import Path

DATASETS_DIR = Path('.')
PROCESSED_DIR = DATASETS_DIR / 'processed'

districts = gpd.read_file(DATASETS_DIR / 'india_districts.geojson')
print('Districts loaded:', len(districts))

crop_prod = pd.read_csv(PROCESSED_DIR / 'crop_production_district_icrisat.csv')
crop_yield = pd.read_csv(PROCESSED_DIR / 'crop_yield_district_icrisat.csv')
print('Crop data loaded')

icrisat_years = sorted(crop_prod['year'].unique())
icrisat_crops = sorted(crop_prod['crop'].unique())
print(f'Years: {len(icrisat_years)}, Crops: {len(icrisat_crops)}')
print(f'Total grid: {len(districts) * len(icrisat_crops) * len(icrisat_years)}')