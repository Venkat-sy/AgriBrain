#!/usr/bin/env python
"""Initialize the database with tables and sample data."""
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.models import Base
from backend.core.config import engine, SessionLocal


def init_database():
    """Create all tables and insert sample data."""
    # Create all tables
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully!")
    
    # Create a session for inserting sample data
    db = SessionLocal()
    
    try:
        # Check if data already exists
        from backend.models import District, CropProfile, RainfallMonthly, CropCost, CropPrice, SoilType, DistrictSoilType
        
        existing_districts = db.query(District).count()
        existing_soils = db.query(SoilType).count()
        if existing_districts > 0 and existing_soils > 0:
            print(f"Database already has {existing_districts} districts and {existing_soils} soil types. Skipping sample data insertion.")
            return
        
        print("Inserting sample data...")
        
        # Sample districts (Indian major agricultural districts)
        districts_data = [
            {"id": 1, "name": "Ludhiana", "state": "Punjab", "latitude": 30.9010, "longitude": 75.8573, "area_km2": 3578, "population": 3498739, "soil_type": "Alluvial", "agro_climatic_zone": "Trans-Gangetic Plains"},
            {"id": 2, "name": "Karnal", "state": "Haryana", "latitude": 29.6857, "longitude": 76.9905, "area_km2": 2520, "population": 1505324, "soil_type": "Alluvial", "agro_climatic_zone": "Trans-Gangetic Plains"},
            {"id": 3, "name": "Coimbatore", "state": "Tamil Nadu", "latitude": 11.0168, "longitude": 76.9558, "area_km2": 4732, "population": 3458045, "soil_type": "Red Soil", "agro_climatic_zone": "Southern Plateau"},
            {"id": 4, "name": "Nashik", "state": "Maharashtra", "latitude": 19.9975, "longitude": 73.7898, "area_km2": 15530, "population": 6107187, "soil_type": "Black Soil", "agro_climatic_zone": "Western Ghats"},
            {"id": 5, "name": "East Godavari", "state": "Andhra Pradesh", "latitude": 16.9875, "longitude": 82.2460, "area_km2": 10807, "population": 5154296, "soil_type": "Alluvial", "agro_climatic_zone": "East Coast Plains"},
            {"id": 6, "name": "Guntur", "state": "Andhra Pradesh", "latitude": 16.3067, "longitude": 80.4365, "area_km2": 11391, "population": 4887813, "soil_type": "Black Soil", "agro_climatic_zone": "East Coast Plains"},
            {"id": 7, "name": "Ahmednagar", "state": "Maharashtra", "latitude": 19.0948, "longitude": 74.7479, "area_km2": 17048, "population": 4543159, "soil_type": "Black Soil", "agro_climatic_zone": "Deccan Plateau"},
            {"id": 8, "name": "Sangli", "state": "Maharashtra", "latitude": 16.8524, "longitude": 74.5815, "area_km2": 8572, "population": 2822143, "soil_type": "Black Soil", "agro_climatic_zone": "Deccan Plateau"},
            {"id": 9, "name": "Belgaum", "state": "Karnataka", "latitude": 15.8497, "longitude": 74.4977, "area_km2": 13415, "population": 4779661, "soil_type": "Red Soil", "agro_climatic_zone": "Southern Plateau"},
            {"id": 10, "name": "Nalgonda", "state": "Telangana", "latitude": 17.0535, "longitude": 79.2667, "area_km2": 14240, "population": 3488809, "soil_type": "Red Soil", "agro_climatic_zone": "Deccan Plateau"},
        ]
        
        for d in districts_data:
            district = District(**d)
            db.add(district)
        
        # Sample soil types
        soil_types_data = [
            {"name": "Alluvial", "description": "Fertile young soils found in river basins", "typical_crops": ["Rice", "Wheat", "Sugarcane"], "color_hex": "#E8D5B7"},
            {"name": "Black Soil", "description": "High clay content, good moisture retention", "typical_crops": ["Cotton", "Soybean", "Sugarcane"], "color_hex": "#3D3D3D"},
            {"name": "Red Soil", "description": "Acidic, low CEC, requires liming", "typical_crops": ["Groundnut", "Millets", "Pulses"], "color_hex": "#B22222"},
            {"name": "Laterite", "description": "Highly weathered, acidic, low fertility", "typical_crops": ["Cashew", "Mango", "Tea"], "color_hex": "#8B4513"},
            {"name": "Desert", "description": "Sandy, alkaline, low organic matter", "typical_crops": ["Bajra", "Guar", "Moth Bean"], "color_hex": "#F4A460"},
            {"name": "Peaty", "description": "High organic matter, acidic", "typical_crops": ["Rice", "Vegetables"], "color_hex": "#2F4F2F"},
        ]
        
        for s in soil_types_data:
            soil = SoilType(**s)
            db.add(soil)
        db.flush()  # Get IDs for soil types
        
        # Sample district-soil type associations
        district_soil_data = [
            {"district_id": 1, "soil_type_id": 1, "percentage": 80.0, "is_predominant": True},   # Ludhiana - Alluvial
            {"district_id": 2, "soil_type_id": 1, "percentage": 75.0, "is_predominant": True},   # Karnal - Alluvial
            {"district_id": 3, "soil_type_id": 3, "percentage": 70.0, "is_predominant": True},   # Coimbatore - Red Soil
            {"district_id": 4, "soil_type_id": 2, "percentage": 65.0, "is_predominant": True},   # Nashik - Black Soil
            {"district_id": 5, "soil_type_id": 1, "percentage": 85.0, "is_predominant": True},   # East Godavari - Alluvial
            {"district_id": 6, "soil_type_id": 2, "percentage": 60.0, "is_predominant": True},   # Guntur - Black Soil
            {"district_id": 7, "soil_type_id": 2, "percentage": 55.0, "is_predominant": True},   # Ahmednagar - Black Soil
            {"district_id": 8, "soil_type_id": 2, "percentage": 50.0, "is_predominant": True},   # Sangli - Black Soil
            {"district_id": 9, "soil_type_id": 3, "percentage": 75.0, "is_predominant": True},   # Belgaum - Red Soil
            {"district_id": 10, "soil_type_id": 3, "percentage": 70.0, "is_predominant": True},  # Nalgonda - Red Soil
        ]
        
        for ds in district_soil_data:
            dst = DistrictSoilType(**ds)
            db.add(dst)
        
        # Sample crop profiles
        crops_data = [
            {
                "name": "Rice",
                "category": "Cereals",
                "season": "Kharif",
                "duration_days": 120,
                "spacing_cm": 20.0,
                "row_spacing_cm": 20.0,
                "n_requirement": 120.0,
                "p_requirement": 60.0,
                "k_requirement": 40.0,
                "rainfall_min_mm": 1000,
                "rainfall_max_mm": 2000,
                "temp_min_c": 20.0,
                "temp_max_c": 35.0,
                "ph_min": 5.5,
                "ph_max": 7.0,
                "suitable_soil_types": ["Alluvial Soil", "Clay Soil", "Clay Loam"],
                "expected_yield_tons_per_ha": 4.5,
                "water_requirement_mm": 1200,
                "description": "Major staple food crop, grown in kharif season"
            },
            {
                "name": "Wheat",
                "category": "Cereals",
                "season": "Rabi",
                "duration_days": 130,
                "spacing_cm": 22.5,
                "row_spacing_cm": 22.5,
                "n_requirement": 150.0,
                "p_requirement": 60.0,
                "k_requirement": 40.0,
                "rainfall_min_mm": 300,
                "rainfall_max_mm": 600,
                "temp_min_c": 12.0,
                "temp_max_c": 25.0,
                "ph_min": 6.0,
                "ph_max": 7.5,
                "suitable_soil_types": ["Alluvial Soil", "Loamy Soil", "Clay Loam"],
                "expected_yield_tons_per_ha": 4.0,
                "water_requirement_mm": 450,
                "description": "Major rabi cereal crop, grown in winter"
            }
        ]
        
        for c in crops_data:
            crop = CropProfile(**c)
            db.add(crop)
        
        # Add more crop profiles
        more_crops = [
            {
                "name": "Maize",
                "category": "Cereals",
                "season": "Kharif",
                "duration_days": 110,
                "spacing_cm": 60.0,
                "row_spacing_cm": 20.0,
                "n_requirement": 180.0,
                "p_requirement": 70.0,
                "k_requirement": 50.0,
                "rainfall_min_mm": 500,
                "rainfall_max_mm": 1000,
                "temp_min_c": 18.0,
                "temp_max_c": 32.0,
                "ph_min": 5.5,
                "ph_max": 7.5,
                "suitable_soil_types": ["Alluvial Soil", "Red Soil", "Loamy Soil"],
                "expected_yield_tons_per_ha": 5.5,
                "water_requirement_mm": 600,
                "description": "Versatile cereal crop for food and feed"
            },
            {
                "name": "Cotton",
                "category": "Fiber Crops",
                "season": "Kharif",
                "duration_days": 180,
                "spacing_cm": 90.0,
                "row_spacing_cm": 60.0,
                "n_requirement": 120.0,
                "p_requirement": 60.0,
                "k_requirement": 60.0,
                "rainfall_min_mm": 500,
                "rainfall_max_mm": 1200,
                "temp_min_c": 20.0,
                "temp_max_c": 35.0,
                "ph_min": 5.5,
                "ph_max": 8.0,
                "suitable_soil_types": ["Black Soil", "Red Soil", "Alluvial Soil"],
                "expected_yield_tons_per_ha": 2.5,
                "water_requirement_mm": 700,
                "description": "Major cash crop for fiber production"
            },
            {
                "name": "Soybean",
                "category": "Oilseeds",
                "season": "Kharif",
                "duration_days": 100,
                "spacing_cm": 45.0,
                "row_spacing_cm": 10.0,
                "n_requirement": 20.0,
                "p_requirement": 60.0,
                "k_requirement": 40.0,
                "rainfall_min_mm": 600,
                "rainfall_max_mm": 1000,
                "temp_min_c": 20.0,
                "temp_max_c": 30.0,
                "ph_min": 6.0,
                "ph_max": 7.5,
                "suitable_soil_types": ["Black Soil", "Red Soil", "Loamy Soil"],
                "expected_yield_tons_per_ha": 2.8,
                "water_requirement_mm": 650,
                "description": "Important oilseed and protein crop"
            },
            {
                "name": "Groundnut",
                "category": "Oilseeds",
                "season": "Kharif",
                "duration_days": 120,
                "spacing_cm": 30.0,
                "row_spacing_cm": 10.0,
                "n_requirement": 20.0,
                "p_requirement": 40.0,
                "k_requirement": 40.0,
                "rainfall_min_mm": 500,
                "rainfall_max_mm": 1000,
                "temp_min_c": 22.0,
                "temp_max_c": 32.0,
                "ph_min": 6.0,
                "ph_max": 7.0,
                "suitable_soil_types": ["Red Soil", "Sandy Loam", "Alluvial Soil"],
                "expected_yield_tons_per_ha": 2.0,
                "water_requirement_mm": 550,
                "description": "Major oilseed crop, also used for direct consumption"
            },
            {
                "name": "Sugarcane",
                "category": "Cash Crops",
                "season": "Annual",
                "duration_days": 300,
                "spacing_cm": 90.0,
                "row_spacing_cm": 90.0,
                "n_requirement": 250.0,
                "p_requirement": 100.0,
                "k_requirement": 200.0,
                "rainfall_min_mm": 1000,
                "rainfall_max_mm": 2000,
                "temp_min_c": 20.0,
                "temp_max_c": 35.0,
                "ph_min": 6.0,
                "ph_max": 8.0,
                "suitable_soil_types": ["Alluvial Soil", "Black Soil", "Red Soil"],
                "expected_yield_tons_per_ha": 70.0,
                "water_requirement_mm": 2000,
                "description": "Long duration cash crop for sugar production"
            },
            {
                "name": "Chickpea",
                "category": "Pulses",
                "season": "Rabi",
                "duration_days": 110,
                "spacing_cm": 30.0,
                "row_spacing_cm": 10.0,
                "n_requirement": 20.0,
                "p_requirement": 50.0,
                "k_requirement": 30.0,
                "rainfall_min_mm": 300,
                "rainfall_max_mm": 600,
                "temp_min_c": 10.0,
                "temp_max_c": 25.0,
                "ph_min": 6.0,
                "ph_max": 8.0,
                "suitable_soil_types": ["Alluvial Soil", "Black Soil", "Loamy Soil"],
                "expected_yield_tons_per_ha": 1.8,
                "water_requirement_mm": 350,
                "description": "Major rabi pulse crop"
            },
        ]
        
        for c in more_crops:
            crop = CropProfile(**c)
            db.add(crop)
        
        db.flush()  # Get IDs
        
        # Sample rainfall data
        rainfall_data = []
        for district_id in range(1, 11):
            # Monthly rainfall for a typical Indian district (mm)
            monthly_rainfall = {
                1: 15, 2: 10, 3: 15, 4: 20, 5: 50, 6: 150,
                7: 300, 8: 280, 9: 200, 10: 80, 11: 30, 12: 10
            }
            for month, rain in monthly_rainfall.items():
                rainfall_data.append({
                    "district_id": district_id,
                    "month": month,
                    "year": 2023,
                    "rainfall_mm": rain
                })
                # Add previous year data
                rainfall_data.append({
                    "district_id": district_id,
                    "month": month,
                    "year": 2022,
                    "rainfall_mm": rain * 0.9
                })
        
        for r in rainfall_data:
            db.add(RainfallMonthly(**r))
        
        # Sample crop costs (per hectare) - Realistic Indian farming costs
        # Get crop IDs
        crops = db.query(CropProfile).all()
        for crop in crops:
            if crop.name == "Rice":
                costs = [
                    ("Land Preparation (Puddling)", "ha", 4000, 1),
                    ("Seeds", "kg", 25, 40),
                    ("Transplanting", "ha", 3500, 1),
                    ("Basal Fertilizer (NPK)", "ha", 4500, 1),
                    ("Top Dressing - Nitrogen", "ha", 2500, 2),
                    ("Pesticides/Insecticides", "ha", 2500, 2),
                    ("Weeding", "ha", 2000, 2),
                    ("Irrigation", "ha", 3000, 8),
                    ("Harvesting", "ha", 4000, 1),
                    ("Threshing & Winnowing", "ha", 2500, 1),
                    ("Labor", "day", 400, 50),
                ]
            elif crop.name == "Wheat":
                costs = [
                    ("Land Preparation", "ha", 3000, 1),
                    ("Seeds", "kg", 40, 100),
                    ("Sowing", "ha", 2500, 1),
                    ("Basal Fertilizer (NPK)", "ha", 4000, 1),
                    ("Top Dressing - Nitrogen", "ha", 2500, 2),
                    ("Pesticides/Weedicides", "ha", 1500, 1),
                    ("Irrigation", "ha", 3000, 4),
                    ("Harvesting", "ha", 3500, 1),
                    ("Threshing", "ha", 2000, 1),
                    ("Labor", "day", 350, 40),
                ]
            elif crop.name == "Maize":
                costs = [
                    ("Land Preparation", "ha", 3000, 1),
                    ("Seeds", "kg", 180, 20),
                    ("Sowing", "ha", 2500, 1),
                    ("Basal Fertilizer (NPK)", "ha", 4000, 1),
                    ("Top Dressing - Nitrogen", "ha", 2500, 2),
                    ("Pesticides/Weedicides", "ha", 1500, 1),
                    ("Irrigation", "ha", 2500, 3),
                    ("Harvesting", "ha", 3000, 1),
                    ("Shelling/Drying", "ha", 2000, 1),
                    ("Labor", "day", 350, 35),
                ]
            elif crop.name == "Cotton":
                costs = [
                    ("Land Preparation", "ha", 3500, 1),
                    ("Seeds (Bt Cotton)", "kg", 800, 2.5),
                    ("Sowing", "ha", 2000, 1),
                    ("Basal Fertilizer (NPK)", "ha", 5000, 1),
                    ("Top Dressing - Nitrogen", "ha", 3000, 3),
                    ("Pesticides/Insecticides", "ha", 8000, 4),
                    ("Weeding", "ha", 3000, 3),
                    ("Irrigation", "ha", 6000, 5),
                    ("Harvesting (Multiple pickings)", "ha", 10000, 1),
                    ("Post-harvest Handling", "ha", 3000, 1),
                    ("Labor", "day", 400, 80),
                ]
            elif crop.name == "Soybean":
                costs = [
                    ("Land Preparation", "ha", 3000, 1),
                    ("Seeds", "kg", 70, 75),
                    ("Sowing", "ha", 2500, 1),
                    ("Basal Fertilizer (NPK)", "ha", 3500, 1),
                    ("Top Dressing", "ha", 2000, 1),
                    ("Pesticides/Weedicides", "ha", 1500, 1),
                    ("Irrigation", "ha", 2000, 2),
                    ("Harvesting", "ha", 2500, 1),
                    ("Threshing", "ha", 1500, 1),
                    ("Labor", "day", 350, 30),
                ]
            elif crop.name == "Groundnut":
                costs = [
                    ("Land Preparation", "ha", 3500, 1),
                    ("Seeds", "kg", 90, 100),
                    ("Sowing", "ha", 3000, 1),
                    ("Basal Fertilizer (NPK)", "ha", 4000, 1),
                    ("Gypsum Application", "ha", 2000, 1),
                    ("Pesticides/Weedicides", "ha", 2000, 1),
                    ("Irrigation", "ha", 2500, 3),
                    ("Harvesting", "ha", 4000, 1),
                    ("Threshing/Drying", "ha", 2500, 1),
                    ("Labor", "day", 400, 45),
                ]
            elif crop.name == "Sugarcane":
                costs = [
                    ("Land Preparation", "ha", 5000, 1),
                    ("Seeds (Setts)", "qtl", 3000, 30),
                    ("Planting", "ha", 4000, 1),
                    ("Basal Fertilizer (NPK)", "ha", 8000, 1),
                    ("Top Dressing - Nitrogen", "ha", 4000, 3),
                    ("Earthing Up", "ha", 3000, 2),
                    ("Pesticides/Weedicides", "ha", 5000, 3),
                    ("Irrigation", "ha", 10000, 12),
                    ("Harvesting & Loading", "ha", 8000, 1),
                    ("Labor", "day", 450, 150),
                ]
            elif crop.name == "Chickpea":
                costs = [
                    ("Land Preparation", "ha", 2500, 1),
                    ("Seeds", "kg", 80, 80),
                    ("Sowing", "ha", 2000, 1),
                    ("Basal Fertilizer (NPK)", "ha", 2500, 1),
                    ("Pesticides/Weedicides", "ha", 1500, 1),
                    ("Irrigation", "ha", 1500, 1),
                    ("Harvesting", "ha", 2500, 1),
                    ("Threshing", "ha", 1500, 1),
                    ("Labor", "day", 350, 25),
                ]
            else:
                continue
            
            for activity, unit, unit_cost, qty in costs:
                db.add(CropCost(
                    crop_id=crop.id,
                    activity=activity,
                    unit=unit,
                    unit_cost=unit_cost,
                    quantity_per_ha=qty,
                    region="national"
                ))
        
        # Sample market prices
        price_data = {
            "Rice": 22000,
            "Wheat": 24000,
            "Maize": 20000,
            "Cotton": 58000,
            "Soybean": 48000,
            "Groundnut": 58000,
            "Sugarcane": 3200,
            "Chickpea": 52000,
        }
        
        from datetime import date, timedelta
        for crop in crops:
            if crop.name in price_data:
                db.add(CropPrice(
                    crop_id=crop.id,
                    price_per_ton=price_data[crop.name],
                    price_date=date.today() - timedelta(days=30),
                    market="National Average",
                    source="AgMarkNet"
                ))
        
        db.commit()
        print("Sample data inserted successfully!")
        
    except Exception as e:
        db.rollback()
        print(f"Error inserting sample data: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    init_database()
