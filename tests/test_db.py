import sys
sys.path.insert(0, '.')
from backend.models import CropProfile, CropCost, CropPrice
from backend.core.config import get_db

db = next(get_db())
try:
    crops = db.query(CropProfile).all()
    print(f'Total crops: {len(crops)}')
    for crop in crops:
        print(f'  {crop.name}: yield={crop.expected_yield_tons_per_ha}, duration={crop.duration_days}, spacing={crop.spacing_cm}x{crop.row_spacing_cm}')
        prices = db.query(CropPrice).filter(CropPrice.crop_id == crop.id).all()
        if prices:
            for p in prices[:2]:
                print(f'    Rs{p.price_per_ton}/ton ({p.market})')
        else:
            print('    No prices')
        costs = db.query(CropCost).filter(CropCost.crop_id == crop.id).all()
        if costs:
            total_cost = sum(c.unit_cost * c.quantity_per_ha for c in costs)
            print(f'    Total cost/ha: Rs{total_cost:,.0f}')
            for c in costs[:3]:
                print(f'      {c.activity}: Rs{c.unit_cost} x {c.quantity_per_ha} {c.unit}')
        else:
            print('    No costs')
finally:
    db.close()