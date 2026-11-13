import sys
sys.path.insert(0, '.')
from backend.models import CropProfile
from backend.core.config import get_db

db = next(get_db())
try:
    crops = db.query(CropProfile).all()
    for crop in crops:
        print(f'{crop.name}: n_req={crop.n_requirement}, p_req={crop.p_requirement}, k_req={crop.k_requirement}')
        print(f'  temp: {crop.temp_min_c}-{crop.temp_max_c}, ph: {crop.ph_min}-{crop.ph_max}, rainfall: {crop.rainfall_min_mm}-{crop.rainfall_max_mm}')
finally:
    db.close()