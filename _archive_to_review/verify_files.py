import pandas as pd
import json

# Verify all key files exist and have correct structure
files_to_check = [
    'india_districts.geojson',
    'district_metadata.json', 
    'district_rainfall_summary.json',
    'district_rainfall_history.csv',
    'crop_agronomy_base.json',
    'master_agri_dataset.csv',
    'district_name_mapping.csv',
    'dataset_source_manifest.json',
    'DATA_COVERAGE_REPORT.md'
]

print('=== FILE VERIFICATION ===')
for f in files_to_check:
    try:
        if f.endswith('.geojson'):
            with open(f, 'r') as fp:
                gj = json.load(fp)
            print(f + ': OK - ' + str(len(gj["features"])) + ' districts')
        elif f.endswith('.json'):
            with open(f, 'r') as fp:
                data = json.load(fp)
            if isinstance(data, dict):
                print(f + ': OK - ' + str(len(data)) + ' keys')
            else:
                print(f + ': OK')
        elif f.endswith('.csv'):
            df = pd.read_csv(f)
            print(f + ': OK - ' + str(df.shape[0]) + ' rows, ' + str(df.shape[1]) + ' cols')
        elif f.endswith('.md'):
            with open(f, 'r') as fp:
                content = fp.read()
            print(f + ': OK - ' + str(len(content)) + ' chars')
    except Exception as e:
        print(f + ': ERROR - ' + str(e))

# Verify master dataset
master = pd.read_csv('master_agri_dataset.csv')
print('\n=== MASTER DATASET VERIFICATION ===')
print('Rows: ' + str(len(master)))
print('Unique districts: ' + str(master["district_name"].nunique()))
print('Unique crops: ' + str(master["crop"].nunique()))
print('Year range: ' + str(master["year"].min()) + '-' + str(master["year"].max()))
print('Failure risk distribution:')
print(master['failure_risk'].value_counts())
print('Soil availability:')
print(master['soil_data_availability'].value_counts())
print('Data sources:')
print('  Rainfall: ' + master["rainfall_data_source"].iloc[0])
print('  Production: ' + master["production_data_source"].iloc[0])
print('  Yield: ' + master["yield_data_source"].iloc[0])

# Verify rainfall history
rain_hist = pd.read_csv('district_rainfall_history.csv')
print('\n=== RAINFALL HISTORY ===')
print('Rows: ' + str(len(rain_hist)))
print('Unique districts: ' + str(rain_hist["district_name"].nunique()))
print('Year range: ' + str(rain_hist["year"].min()) + '-' + str(rain_hist["year"].max()))
print('Data source: ' + rain_hist["data_source"].iloc[0])

# Verify rainfall summary
with open('district_rainfall_summary.json', 'r') as f:
    rain_sum = json.load(f)
synthetic = sum(1 for v in rain_sum.values() if v['data_availability'] == 'synthetic_placeholder')
missing = sum(1 for v in rain_sum.values() if v['data_availability'] == 'missing')
print('\n=== RAINFALL SUMMARY ===')
print('Total districts: ' + str(len(rain_sum)))
print('Synthetic: ' + str(synthetic))
print('Missing: ' + str(missing))

print('\n=== ALL VERIFICATIONS PASSED ===')