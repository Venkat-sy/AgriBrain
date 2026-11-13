import json

with open('india_districts.geojson', 'r') as f:
    gj = json.load(f)

# Check for Ahmednagar/Ahmadnagar
for feat in gj['features']:
    name = feat['properties']['district_name'].lower()
    if 'ahmed' in name or 'ahmad' in name:
        print('Found:', feat['properties']['district_name'], '|', feat['properties']['state_name'])