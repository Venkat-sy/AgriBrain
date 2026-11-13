import sys
sys.path.insert(0, '.')
from backend.services.crop_recommendation_service import recommend_crops

# Test with various soil conditions
test_cases = [
    # High NPK, good conditions - should recommend rice/wheat
    {'N': 90, 'P': 42, 'K': 43, 'temperature': 25, 'humidity': 80, 'ph': 6.5, 'rainfall': 200},
    # Low NPK - should recommend different crops
    {'N': 10, 'P': 10, 'K': 10, 'temperature': 25, 'humidity': 80, 'ph': 6.5, 'rainfall': 200},
    # High P, medium NPK - legumes?
    {'N': 50, 'P': 80, 'K': 40, 'temperature': 20, 'humidity': 90, 'ph': 5.5, 'rainfall': 300},
    # Medium NPK, higher temperature
    {'N': 20, 'P': 40, 'K': 40, 'temperature': 30, 'humidity': 60, 'ph': 7.0, 'rainfall': 100},
    # Very low NPK
    {'N': 5, 'P': 5, 'K': 5, 'temperature': 35, 'humidity': 50, 'ph': 8.0, 'rainfall': 50},
    # High NPK, all good
    {'N': 120, 'P': 60, 'K': 40, 'temperature': 28, 'humidity': 70, 'ph': 6.8, 'rainfall': 150},
]

for i, case in enumerate(test_cases):
    print(f"\nTest Case {i+1}: {case}")
    try:
        recommendations = recommend_crops(case)
        for rec in recommendations:
            print(f"  {rec['crop_name']}: {rec['confidence']:.2f} - {rec['match_reasons']}")
    except Exception as e:
        print(f"  ERROR: {e}")