import requests
import re
import os

# Try accessing the specific dataset mentioned in acquire_crop_data.py
dataset_id = '9ef84268-d588-465a-a308-a864a43d0070'
url = f'https://api.data.gov.in/resource/{dataset_id}'
params = {
    'format': 'json',
    'limit': 10
}
try:
    r = requests.get(url, params=params, timeout=30)
    print(f'Status: {r.status_code}')
    print(f'Response: {r.text[:500]}')
except Exception as e:
    print(f'Error: {e}')

# Also try with API key if available
api_key = os.getenv('DATA_GOV_API_KEY')
if api_key:
    params['api-key'] = api_key
    try:
        r = requests.get(url, params=params, timeout=30)
        print(f'With API key - Status: {r.status_code}')
        print(f'With API key - Response: {r.text[:500]}')
    except Exception as e:
        print(f'With API key - Error: {e}')
else:
    print('No DATA_GOV_API_KEY in environment')