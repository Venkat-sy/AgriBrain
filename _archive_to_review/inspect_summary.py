import json
f = open('district_rainfall_summary.json')
data = json.load(f)
f.close()
print('Total districts:', len(data))
items = list(data.items())
for k, v in items[:5]:
    print(k, v['years_available'], v['data_sources'])

# Check if 2021-2025 data exists
for k, v in items:
    if any(y in v['years_available'] for y in [2021, 2022, 2023, 2024, 2025]):
        print(f'HAS 2021-2025: {k} - years: {v["years_available"]}, sources: {v["data_sources"]}')
        break

# Count districts with netcdf data
netcdf_count = sum(1 for v in data.values() if 'netcdf_grid_derived' in v['data_sources'])
print(f'Districts with netcdf_grid_derived: {netcdf_count}')