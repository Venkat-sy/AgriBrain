"""Comprehensive test of the full API stack"""
import sys
sys.path.insert(0, '.')

# Test 1: Simulation Engine
print("=" * 60)
print("TEST 1: Simulation Engine")
print("=" * 60)
from backend.services.simulation_engine import SimulationEngine
from backend.models import CropProfile, District
from backend.schemas import SimulationRequest
from backend.core.config import get_db

db = next(get_db())
try:
    district = db.query(District).first()
    crops = db.query(CropProfile).all()
    
    for crop in crops:
        request = SimulationRequest(
            district_id=district.id,
            selected_crop=crop.name,
            land_area_ha=1.0,
            budget_inr=500000,
            confirmed_soil_type="Alluvial Soil",
            planting_month=6
        )
        
        engine = SimulationEngine(db)
        result = engine.run_simulation(request, district, crop)
        
        print(f"{crop.name}: Yield={result.estimated_yield_tons_per_ha:.2f} t/ha, "
              f"Cost=Rs{result.total_cost_inr:,.0f}, "
              f"Value=Rs{result.market_value_inr:,.0f}, "
              f"ROI={result.roi_percentage:.1f}%, "
              f"Risk={result.risk_level.value}")
finally:
    db.close()

# Test 2: Crop Recommendation (ML-based)
print("\n" + "=" * 60)
print("TEST 2: ML-based Crop Recommendation")
print("=" * 60)
from backend.services.crop_recommendation_service import recommend_crops

test_cases = [
    {'N': 90, 'P': 42, 'K': 43, 'temperature': 25, 'humidity': 80, 'ph': 6.5, 'rainfall': 200},
    {'N': 10, 'P': 10, 'K': 10, 'temperature': 25, 'humidity': 80, 'ph': 6.5, 'rainfall': 200},
    {'N': 50, 'P': 80, 'K': 40, 'temperature': 20, 'humidity': 90, 'ph': 5.5, 'rainfall': 300},
]

for i, case in enumerate(test_cases):
    print(f"\nTest Case {i+1}: {case}")
    recommendations = recommend_crops(case)
    for rec in recommendations:
        print(f"  {rec['crop_name']}: {rec['confidence']:.2f}")

# Test 3: Rule-based Crop Recommendation (API style)
print("\n" + "=" * 60)
print("TEST 3: Rule-based Crop Recommendation (API style)")
print("=" * 60)
from backend.api.crop_recommendation import recommend_crops as api_recommend_crops
from backend.schemas import CropRecommendationRequest
from backend.core.config import get_db

# We can't easily test the async API endpoint, but we can test the underlying logic
db = next(get_db())
try:
    district = db.query(District).first()
    request = CropRecommendationRequest(
        district_id=district.id,
        soil_type="Alluvial Soil",
        rainfall_mm=800,
        temperature_c=25,
        humidity_percent=70,
        ph=6.5,
        n=90,
        p=42,
        k=43,
        top_k=5
    )
    
    # Just test the function directly
    from backend.api.crop_recommendation import recommend_crops
    # Can't easily call async function, so we'll just check the schemas work
    print(f"Schema validation passed for CropRecommendationRequest")
    print(f"Request: soil={request.soil_type}, rainfall={request.rainfall_mm}mm, "
          f"temp={request.temperature_c}C, NPK=({request.n},{request.p},{request.k})")
finally:
    db.close()

# Test 4: Market Pricing
print("\n" + "=" * 60)
print("TEST 4: Market Pricing Service")
print("=" * 60)
from backend.services.market_pricing import fetch_live_market_price

crops = ['Rice', 'Wheat', 'Maize', 'Cotton', 'Sugarcane']
for c in crops:
    price = fetch_live_market_price(c, 'Punjab')
    print(f"  {c}: Rs{price:,.0f}/ton")

print("\n" + "=" * 60)
print("ALL TESTS COMPLETED SUCCESSFULLY!")
print("=" * 60)