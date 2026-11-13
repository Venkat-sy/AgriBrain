import httpx
import time
import sys

# Wait a bit for server to fully start
time.sleep(2)

try:
    # Test health endpoint
    r = httpx.get('http://localhost:8000/health', timeout=5.0)
    print(f'Health: {r.status_code} - {r.json()}')
    
    # Test simulation endpoint
    payload = {
        'district_id': 1,
        'selected_crop': 'Rice',
        'land_area_ha': 2.0,
        'budget_inr': 100000,
        'confirmed_soil_type': 'Clay',
        'rainfall_override_mm': 800,
        'planting_month': 6
    }
    r = httpx.post('http://localhost:8000/api/v1/simulation/run', json=payload, timeout=10.0)
    print(f'Simulation: {r.status_code}')
    if r.status_code == 200:
        data = r.json()
        print(f'  Yield: {data.get("estimated_yield_tons_per_ha"):.2f} tons/ha')
        print(f'  ML Yield: {data.get("ml_yield_prediction_tons_per_ha")} tons/ha')
        print(f'  ML Yield Total: {data.get("ml_yield_prediction_tons")} tons')
        print(f'  Recommended crops: {data.get("recommended_crops")}')
    else:
        print(f'  Error: {r.text}')
except Exception as e:
    print(f'Error: {e}')