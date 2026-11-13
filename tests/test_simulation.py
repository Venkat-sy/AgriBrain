import sys
sys.path.insert(0, '.')
from backend.services.simulation_engine import SimulationEngine
from backend.core.config import get_db
from backend.models import CropProfile, District
from backend.schemas import SimulationRequest
from datetime import date

db = next(get_db())
engine = SimulationEngine(db)
crop = db.query(CropProfile).filter(CropProfile.name.ilike('Rice')).first()
district = db.query(District).first()

request = SimulationRequest(
    district_id=district.id,
    selected_crop='Rice',
    land_area_ha=2.0,
    budget_inr=100000,
    confirmed_soil_type='Alluvial Soil',
    rainfall_override_mm=800,
    planting_season='Kharif',
    planned_start_date=date(2024,6,15)
)

result = engine.run_simulation(request, district, crop)
print(f'Crop: {result.selected_crop}')
print(f'District: {result.district_name}')
print(f'Land Area: {result.land_area_ha} ha')
print(f'Yield: {result.estimated_yield_tons:.2f} tons')
print(f'Yield per ha: {result.estimated_yield_tons_per_ha:.2f} tons/ha')
print(f'Cost: ₹{result.total_cost_inr:,.2f}')
print(f'Revenue: ₹{result.market_value_inr:,.2f}')
print(f'Profit: ₹{result.net_profit_inr:,.2f}')
print(f'ROI: {result.roi_percentage:.1f}%')
print(f'Risk: {result.risk_level.value}')
print(f'Cost breakdown:')
for item in result.cost_breakdown:
    print(f'  {item.activity}: ₹{item.total_cost:,.2f} ({item.quantity} {item.unit} @ ₹{item.unit_cost:,.2f}/{item.unit})')