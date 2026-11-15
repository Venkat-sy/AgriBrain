import pandas as pd
import geopandas as gpd

df = pd.read_pickle('temp_annual.pkl')
# Check the district names that appear
rainfall_pairs = set()
for _, row in df.iterrows():
    rainfall_pairs.add((row['district_name'].strip(), row['state_name'].strip()))
print(f'Rainfall pairs: {len(rainfall_pairs)}')

districts = gpd.read_file('india_districts.geojson')
geojson_pairs = set()
for _, row in districts.iterrows():
    geojson_pairs.add((row['district_name'].strip(), row['state_name'].strip()))
print(f'GeoJSON pairs: {len(geojson_pairs)}')

missing_in_rainfall = geojson_pairs - rainfall_pairs
print(f'Missing in rainfall: {len(missing_in_rainfall)}')
for m in sorted(missing_in_rainfall)[:20]:
    print(f'  {m}')