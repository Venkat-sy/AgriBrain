import requests
import json

# Test the IMD APIs
apis_to_test = [
    ('Subdivisional Rainfall Forecast', 'https://api.imd.gov.in/api/v1/subdivision_rainfall_forecast'),
    ('State District Rainfall Forecast', 'https://api.imd.gov.in/api/v1/state_district_rainfall_forecast'),
    ('AWS Data Mapping', 'https://api.imd.gov.in/api/v1/aws_data_mapping'),
]

for name, url in apis_to_test:
    try:
        r = requests.get(url, timeout=30)
        print(name + ': ' + str(r.status_code))
        if r.status_code == 200:
            data = r.json()
            if isinstance(data, list):
                print('  Records: ' + str(len(data)))
            else:
                print('  Records: N/A')
            if isinstance(data, list) and len(data) > 0:
                print('  Sample: ' + json.dumps(data[0], indent=2)[:1000])
        else:
            print('  Error: ' + r.text[:500])
    except Exception as e:
        print(name + ': Error - ' + str(e))
    print()