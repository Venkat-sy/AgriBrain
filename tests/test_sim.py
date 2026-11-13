import sys
sys.path.insert(0, '.')
from backend.services.simulation_engine import SimulationEngine
from backend.models import CropProfile, District, RainfallMonthly
from backend.schemas import SimulationRequest
from backend.core.config import get_db

db = next(get_db())
try:
    # Get a district
    district = db.query(District).first()
    crops = db.query(CropProfile).all()
    
    for crop in crops:
        print(f"\n{'='*60}")
        print(f"Crop: {crop.name}, yield={crop.expected_yield_tons_per_ha}, duration={crop.duration_days}")
        print(f"  Suitable soils: {crop.suitable_soil_types}")
        print(f"  Rainfall range: {crop.rainfall_min_mm}-{crop.rainfall_max_mm} mm")
        
        # Create simulation request
        request = SimulationRequest(
            district_id=district.id,
            selected_crop=crop.name,
            land_area_ha=1.0,
            budget_inr=500000,
            confirmed_soil_type="Alluvial Soil",
            planting_month=6
        )
        
        # Run simulation
        engine = SimulationEngine(db)
        result = engine.run_simulation(request, district, crop)
        
        print(f"  Yield: {result.estimated_yield_tons_per_ha:.2f} t/ha")
        print(f"  Total cost: Rs{result.total_cost_inr:,.0f}")
        print(f"  Market value: Rs{result.market_value_inr:,.0f}")
        print(f"  Net profit: Rs{result.net_profit_inr:,.0f}")
        print(f"  ROI: {result.roi_percentage:.1f}%")
        print(f"  Risk level: {result.risk_level}")
        if result.risk_factors:
            print(f"  Risk factors: {result.risk_factors}")
    
finally:
    db.close()