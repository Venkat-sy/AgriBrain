#!/usr/bin/env python
"""Initialize the database with tables and sample data."""
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from agrisim_backend.models import Base
from agrisim_backend.core.config import get_settings


def init_database():
    """Create all tables and insert sample data."""
    settings = get_settings()
    engine = create_engine(settings.DATABASE_URL)
    
    # Create all tables
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully!")
    
    # Create a session for inserting sample data
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Check if data already exists
        from agrisim_backend.models import District, CropProfile, RainfallMonthly, CropCost, CropPrice
        
        existing_districts = db.query(District).count()
        if existing_districts > 0:
            print(f"Database already has {existing_districts} districts. Skipping sample data insertion.")
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
                "temperature_min_c": 20.0,
                "temperature_max_c": 35.0,
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
                "temperature_min_c": 12.0,
                "temperature_max_c": 25.0,
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
                "temperature_min_c": 18.0,
                "temperature_max_c": 32.0,
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
                "temperature_min_c": 20.0,
                "temperature_max_c": 35.0,
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
                "temperature_min_c": 20.0,
                "temperature_max_c": 30.0,
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
                "temperature_min_c": 22.0,
                "temperature_max_c": 32.0,
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
                "temperature_min_c": 20.0,
                "temperature_max_c": 35.0,
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
                "temperature_min_c": 10.0,
                "temperature_max_c": 25.0,
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
        
        # Sample crop costs (per hectare)
        # Get crop IDs
        crops = db.query(CropProfile).all()
        for crop in crops:
            if crop.name == "Rice":
                costs = [
                    ("Seeds", "kg", 80, 50),
                    ("Fertilizer (N)", "kg", 60, 120),
                    ("Fertilizer (P)", "kg", 45, 60),
                    ("Fertilizer (K)", "kg", 30, 40),
                    ("Labor", "hr", 300, 200),
                    ("Irrigation", "ha", 5000, 1),
                    ("Pesticides", "ha", 3000, 1),
                    ("Machinery", "hr", 800, 15),
                ]
            elif crop.name == "Wheat":
                costs = [
                    ("Seeds", "kg", 60, 100),
                    ("Fertilizer (N)", "kg", 60, 150),
                    ("Fertilizer (P)", "kg", 45, 60),
                    ("Fertilizer (K)", "kg", 30, 40),
                    ("Labor", "hr", 300, 150),
                    ("Irrigation", "ha", 4000, 1),
                    ("Pesticides", "ha", 2000, 1),
                    ("Machinery", "hr", 800, 12),
                ]
            elif crop.name == "Maize":
                costs = [
                    ("Seeds", "kg", 150, 20),
                    ("Fertilizer (N)", "kg", 60, 180),
                    ("Fertilizer (P)", "kg", 45, 70),
                    ("Fertilizer (K)", "kg", 30, 50),
                    ("Labor", "hr", 300, 120),
                    ("Irrigation", "ha", 3000, 1),
                    ("Pesticides", "ha", 2500, 1),
                    ("Machinery", "hr", 800, 10),
                ]
            elif crop.name == "Cotton":
                costs = [
                    ("Seeds", "kg", 800, 2.5),
                    ("Fertilizer (N)", "kg", 60, 120),
                    ("Fertilizer (P)", "kg", 45, 60),
                    ("Fertilizer (K)", "kg", 30, 60),
                    ("Labor", "hr", 300, 300),
                    ("Irrigation", "ha", 6000, 1),
                    ("Pesticides", "ha", 8000, 1),
                    ("Machinery", "hr", 800, 20),
                ]
            elif crop.name == "Soybean":
                costs = [
                    ("Seeds", "kg", 80, 75),
                    ("Fertilizer (N)", "kg", 60, 20),
                    ("Fertilizer (P)", "kg", 45, 60),
                    ("Fertilizer (K)", "kg", 30, 40),
                    ("Labor", "hr", 300, 100),
                    ("Irrigation", "ha", 2000, 1),
                    ("Pesticides", "ha", 2000, 1),
                    ("Machinery", "hr", 800, 8),
                ]
            elif crop.name == "Groundnut":
                costs = [
                    ("Seeds", "kg", 100, 100),
                    ("Fertilizer (N)", "kg", 60, 20),
                    ("Fertilizer (P)", "kg", 45, 40),
                    ("Fertilizer (K)", "kg", 30, 40),
                    ("Labor", "hr", 300, 150),
                    ("Irrigation", "ha", 2500, 1),
                    ("Pesticides", "ha", 2500, 1),
                    ("Machinery", "hr", 800, 10),
                ]
            elif crop.name == "Sugarcane":
                costs = [
                    ("Seeds (Setts)", "qtl", 3000, 30),
                    ("Fertilizer (N)", "kg", 60, 250),
                    ("Fertilizer (P)", "kg", 45, 100),
                    ("Fertilizer (K)", "kg", 30, 200),
                    ("Labor", "hr", 300, 500),
                    ("Irrigation", "ha", 10000, 1),
                    ("Pesticides", "ha", 5000, 1),
                    ("Machinery", "hr", 800, 30),
                ]
            elif crop.name == "Chickpea":
                costs = [
                    ("Seeds", "kg", 80, 80),
                    ("Fertilizer (N)", "kg", 60, 20),
                    ("Fertilizer (P)", "kg", 45, 50),
                    ("Fertilizer (K)", "kg", 30, 30),
                    ("Labor", "hr", 300, 100),
                    ("Irrigation", "ha", 2000, 1),
                    ("Pesticides", "ha", 1500, 1),
                    ("Machinery", "hr", 800, 8),
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
                    market_name="National Average",
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