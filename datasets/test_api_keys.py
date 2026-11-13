import os
import requests
from dotenv import load_dotenv

load_dotenv()

# Get API keys from .env
SOIL_API_KEY_1 = os.getenv('SOIL_API_KEY_1')
SOIL_API_KEY_2 = os.getenv('SOIL_API_KEY_2')
CROP_DIST_WS_API_KEY = os.getenv('CROP_DIST_WS_API_KEY')
RAIN_API_KEY = os.getenv('RAIN_API_KEY')

print("=== API Keys from .env ===")
print(f"SOIL_API_KEY_1: {SOIL_API_KEY_1[:20]}..." if SOIL_API_KEY_1 else "NOT SET")
print(f"SOIL_API_KEY_2: {SOIL_API_KEY_2[:20]}..." if SOIL_API_KEY_2 else "NOT SET")
print(f"CROP_DIST_WS_API_KEY: {CROP_DIST_WS_API_KEY[:20]}..." if CROP_DIST_WS_API_KEY else "NOT SET")
print(f"RAIN_API_KEY: {RAIN_API_KEY[:20]}..." if RAIN_API_KEY else "NOT SET")
print()

# All keys are the same value
api_key = SOIL_API_KEY_1
print(f"Testing with API key: {api_key[:20]}...")
print()

# Test 1: data.gov.in catalog search - try HTTP first
print("=== Test 1: data.gov.in catalog search (HTTP) ===")
url = 'http://api.data.gov.in/catalog/datasets'
params = {'filters[sector]': 'Agriculture', 'limit': 10, 'api-key': api_key}
try:
    r = requests.get(url, params=params, timeout=60)
    print(f"Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        print(f"Total datasets: {data.get('total', 'N/A')}")
        for ds in data.get('records', [])[:10]:
            title = ds.get('title', '')
            if any(kw in title.lower() for kw in ['crop', 'production', 'yield', 'district', 'rainfall', 'soil', 'area']):
                print(f"  - {title} (ID: {ds.get('identifier', 'N/A')})")
    else:
        print(f"Error: {r.text[:200]}")
except Exception as e:
    print(f"Error: {e}")

print()

# Test 1b: Try HTTPS with longer timeout
print("=== Test 1b: data.gov.in catalog search (HTTPS, longer timeout) ===")
url = 'https://api.data.gov.in/catalog/datasets'
params = {'filters[sector]': 'Agriculture', 'limit': 10, 'api-key': api_key}
try:
    r = requests.get(url, params=params, timeout=120)
    print(f"Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        print(f"Total datasets: {data.get('total', 'N/A')}")
        for ds in data.get('records', [])[:10]:
            title = ds.get('title', '')
            if any(kw in title.lower() for kw in ['crop', 'production', 'yield', 'district', 'rainfall', 'soil', 'area']):
                print(f"  - {title} (ID: {ds.get('identifier', 'N/A')})")
    else:
        print(f"Error: {r.text[:200]}")
except Exception as e:
    print(f"Error: {e}")

print()

# Test 2: Specific crop dataset
print("=== Test 2: Specific crop dataset (9ef84268-d588-465a-a308-a864a43d0070) ===")
dataset_id = '9ef84268-d588-465a-a308-a864a43d0070'
url = f'https://api.data.gov.in/resource/{dataset_id}'
params = {'format': 'json', 'limit': 5, 'api-key': api_key}
try:
    r = requests.get(url, params=params, timeout=120)
    print(f"Status: {r.status_code}")
    print(f"Response: {r.text[:500]}")
except Exception as e:
    print(f"Error: {e}")

print()

# Test 3: Try data.gov.in direct website
print("=== Test 3: data.gov.in direct website ===")
url = 'https://data.gov.in/'
try:
    r = requests.get(url, timeout=60)
    print(f"Status: {r.status_code}")
    print(f"Accessible: {r.status_code == 200}")
except Exception as e:
    print(f"Error: {e}")

print()

# Test 4: Try with alternative API endpoint format
print("=== Test 4: Alternative API endpoint format ===")
url = 'https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070'
params = {'format': 'json', 'limit': 5, 'api-key': api_key}
try:
    r = requests.get(url, params=params, timeout=60)
    print(f"Status: {r.status_code}")
    print(f"Response: {r.text[:500]}")
except Exception as e:
    print(f"Error: {e}")