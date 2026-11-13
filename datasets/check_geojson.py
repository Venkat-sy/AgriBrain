import geopandas as gpd

districts = gpd.read_file('india_districts.geojson')
print('GeoJSON columns:', districts.columns.tolist())
print('Sample districts:')
for i, row in districts.head(10).iterrows():
    dn = row.get('district_name', row.get('dtname', row.get('DISTRICT', 'N/A')))
    sn = row.get('state_name', row.get('stname', row.get('STATE', 'N/A')))
    print(f'  {dn}, {sn}')