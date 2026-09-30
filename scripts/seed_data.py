from backend.models import Base, District, SoilType, CropProfile, DistrictSoilType
from backend.core.config import settings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine(settings.DATABASE_URL, connect_args={'check_same_thread': False})
Session = sessionmaker(bind=engine)
session = Session()

# Add some sample districts
districts = [
    District(name='Bangalore Urban', state='Karnataka', state_code='KA', district_code='KA01'),
    District(name='Mysore', state='Karnataka', state_code='KA', district_code='KA02'),
    District(name='Pune', state='Maharashtra', state_code='MH', district_code='MH01'),
    District(name='Nashik', state='Maharashtra', state_code='MH', district_code='MH02'),
    District(name='Ahmedabad', state='Gujarat', state_code='GJ', district_code='GJ01'),
]

for d in districts:
    session.add(d)
session.commit()
print('Districts added')

# Add soil types
soil_types = [
    SoilType(name='Red Soil', description='Well-drained, sandy loam', typical_crops=['Ragi', 'Groundnut', 'Millets'], properties={'ph_range': [5.5, 7.0], 'drainage': 'good'}, color_hex='#CD5C5C'),
    SoilType(name='Black Soil', description='Clayey, moisture retentive', typical_crops=['Cotton', 'Soybean', 'Sorghum'], properties={'ph_range': [6.5, 8.0], 'drainage': 'moderate'}, color_hex='#2F2F2F'),
    SoilType(name='Alluvial Soil', description='Fertile, loamy', typical_crops=['Rice', 'Wheat', 'Sugarcane'], properties={'ph_range': [6.0, 7.5], 'drainage': 'good'}, color_hex='#DEB887'),
    SoilType(name='Laterite Soil', description='Acidic, low fertility', typical_crops=['Cashew', 'Mango', 'Coconut'], properties={'ph_range': [4.5, 6.0], 'drainage': 'good'}, color_hex='#A0522D'),
]

for s in soil_types:
    session.add(s)
session.commit()
print('Soil types added')

# Add crop profiles
crops = [
    CropProfile(name='rice', common_name='Rice', category='cereal', season='kharif', suitable_soil_types=['Alluvial Soil', 'Black Soil'], ph_min=5.5, ph_max=7.0, rainfall_min_mm=1000, rainfall_max_mm=2000, temp_min_c=20, temp_max_c=35, n_requirement=120, p_requirement=60, k_requirement=60, spacing_cm=20, row_spacing_cm=20, duration_days=120, expected_yield_tons_per_ha=4.5, water_requirement_mm=1200),
    CropProfile(name='wheat', common_name='Wheat', category='cereal', season='rabi', suitable_soil_types=['Alluvial Soil', 'Black Soil'], ph_min=6.0, ph_max=7.5, rainfall_min_mm=300, rainfall_max_mm=800, temp_min_c=10, temp_max_c=25, n_requirement=100, p_requirement=50, k_requirement=50, spacing_cm=22, row_spacing_cm=22, duration_days=130, expected_yield_tons_per_ha=3.5, water_requirement_mm=450),
    CropProfile(name='cotton', common_name='Cotton', category='fiber', season='kharif', suitable_soil_types=['Black Soil', 'Alluvial Soil'], ph_min=5.5, ph_max=8.0, rainfall_min_mm=500, rainfall_max_mm=1200, temp_min_c=21, temp_max_c=30, n_requirement=150, p_requirement=75, k_requirement=75, spacing_cm=90, row_spacing_cm=60, duration_days=180, expected_yield_tons_per_ha=2.0, water_requirement_mm=700),
    CropProfile(name='groundnut', common_name='Groundnut', category='oilseed', season='kharif', suitable_soil_types=['Red Soil', 'Alluvial Soil'], ph_min=5.5, ph_max=7.0, rainfall_min_mm=500, rainfall_max_mm=1000, temp_min_c=22, temp_max_c=32, n_requirement=20, p_requirement=40, k_requirement=40, spacing_cm=30, row_spacing_cm=45, duration_days=110, expected_yield_tons_per_ha=1.8, water_requirement_mm=500),
    CropProfile(name='ragi', common_name='Finger Millet (Ragi)', category='cereal', season='kharif', suitable_soil_types=['Red Soil', 'Laterite Soil'], ph_min=5.0, ph_max=7.0, rainfall_min_mm=400, rainfall_max_mm=900, temp_min_c=20, temp_max_c=35, n_requirement=40, p_requirement=20, k_requirement=20, spacing_cm=25, row_spacing_cm=25, duration_days=100, expected_yield_tons_per_ha=2.2, water_requirement_mm=450),
]

for c in crops:
    session.add(c)
session.commit()
print('Crop profiles added')

# Map districts to soil types
# Bangalore - Red Soil predominant
ds = DistrictSoilType(district_id=1, soil_type_id=1, percentage=70, is_predominant=1)
session.add(ds)
# Mysore - Red Soil predominant
ds = DistrictSoilType(district_id=2, soil_type_id=1, percentage=65, is_predominant=1)
session.add(ds)
# Pune - Black Soil predominant
ds = DistrictSoilType(district_id=3, soil_type_id=2, percentage=60, is_predominant=1)
session.add(ds)
# Nashik - Black Soil predominant
ds = DistrictSoilType(district_id=4, soil_type_id=2, percentage=55, is_predominant=1)
session.add(ds)
# Ahmedabad - Alluvial Soil predominant
ds = DistrictSoilType(district_id=5, soil_type_id=3, percentage=75, is_predominant=1)
session.add(ds)
session.commit()
print('District-Soil mappings added')

print('All seed data added successfully!')
