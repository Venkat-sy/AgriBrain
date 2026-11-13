import requests
import re

# Search for crop-related datasets
url = 'https://api.data.gov.in/catalog/datasets'
params = {
    'filters[sector]': 'Agriculture',
    'limit': 50
}
try:
    r = requests.get(url, params=params, timeout=60)
    print(f'Status: {r.status_code}')
    print(f'Response length: {len(r.text)}')
    data = r.json()
    print(f'Total datasets: {data.get("total", "N/A")}')
    for ds in data.get('records', [])[:20]:
        title = ds.get('title', '')
        if any(kw in title.lower() for kw in ['crop', 'production', 'yield', 'district', 'rainfall', 'soil', 'area']):
            print(f"  - {title} (ID: {ds.get('identifier', 'N/A')})")
except Exception as e:
    print(f'Error: {e}')