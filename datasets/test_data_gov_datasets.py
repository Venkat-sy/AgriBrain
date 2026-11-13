import requests
import json

# Try known dataset resource IDs for crop production
dataset_ids = [
    '9ef84268-d588-465a-a308-a864a43d0070',  # Crop production district-wise
    '66c26a81-cb80-48f3-8d6c-f6b9d6b25e3d',  # Rainfall data
    '1b0c8c8d-5e8e-4c4b-8a7b-9c8d7e6f5a4b',  # Generic agriculture
]

for ds_id in dataset_ids:
    url = 'https://api.data.gov.in/resource/' + ds_id
    params = {'format': 'json', 'limit': 5}
    try:
        r = requests.get(url, params=params, timeout=60)
        print(ds_id + ': ' + str(r.status_code))
        if r.status_code == 200:
            data = r.json()
            print('  Total: ' + str(data.get('total', 'N/A')))
            if data.get('records'):
                print('  Sample keys: ' + str(list(data['records'][0].keys())))
                print('  Sample: ' + json.dumps(data['records'][0], indent=2)[:1500])
        else:
            print('  Response: ' + r.text[:500])
    except Exception as e:
        print(ds_id + ': Error - ' + str(e))
    print()