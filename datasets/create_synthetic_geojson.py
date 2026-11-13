#!/usr/bin/env python
"""
Create a synthetic India districts GeoJSON with the exact district names
used in the backend (from init_db.py) to serve as the canonical reference.
This ensures 100% compatibility with the existing database.
"""
import json
from pathlib import Path

OUTPUT_PATH = Path(__file__).parent / "india_districts.geojson"

# Canonical district names from backend/init_db.py (10 districts)
# These are the exact names that must be used everywhere
DISTRICTS = [
    {"district_name": "Ludhiana", "state_name": "Punjab", "state_code": "PB", "district_code": "LUD", "latitude": 30.9010, "longitude": 75.8573},
    {"district_name": "Karnal", "state_name": "Haryana", "state_code": "HR", "district_code": "KAR", "latitude": 29.6857, "longitude": 76.9905},
    {"district_name": "Coimbatore", "state_name": "Tamil Nadu", "state_code": "TN", "district_code": "CBE", "latitude": 11.0168, "longitude": 76.9558},
    {"district_name": "Nashik", "state_name": "Maharashtra", "state_code": "MH", "district_code": "NSK", "latitude": 19.9975, "longitude": 73.7898},
    {"district_name": "East Godavari", "state_name": "Andhra Pradesh", "state_code": "AP", "district_code": "EGD", "latitude": 16.9875, "longitude": 82.2460},
    {"district_name": "Guntur", "state_name": "Andhra Pradesh", "state_code": "AP", "district_code": "GNT", "latitude": 16.3067, "longitude": 80.4365},
    {"district_name": "Ahmednagar", "state_name": "Maharashtra", "state_code": "MH", "district_code": "AHM", "latitude": 19.0948, "longitude": 74.7479},
    {"district_name": "Sangli", "state_name": "Maharashtra", "state_code": "MH", "district_code": "SGL", "latitude": 16.8524, "longitude": 74.5815},
    {"district_name": "Belgaum", "state_name": "Karnataka", "state_code": "KA", "district_code": "BGM", "latitude": 15.8497, "longitude": 74.4977},
    {"district_name": "Mysore", "state_name": "Karnataka", "state_code": "KA", "district_code": "MYS", "latitude": 12.2958, "longitude": 76.6394},
]

def create_synthetic_polygon(lat, lon, size=0.5):
    """Create a simple square polygon around the district center point."""
    half = size / 2
    return [[
        [lon - half, lat - half],
        [lon + half, lat - half],
        [lon + half, lat + half],
        [lon - half, lat + half],
        [lon - half, lat - half]
    ]]

def create_geojson():
    features = []
    
    for district in DISTRICTS:
        polygon = create_synthetic_polygon(district["latitude"], district["longitude"])
        
        feature = {
            "type": "Feature",
            "properties": {
                "district_name": district["district_name"],
                "state_name": district["state_name"],
                "state_code": district["state_code"],
                "district_code": district["district_code"],
                "latitude": district["latitude"],
                "longitude": district["longitude"]
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": polygon
            }
        }
        features.append(feature)
    
    geojson = {
        "type": "FeatureCollection",
        "features": features
    }
    
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(geojson, f, ensure_ascii=False, indent=2)
    
    print(f"Created synthetic GeoJSON with {len(features)} districts at {OUTPUT_PATH}")
    
    # Extract canonical district names
    district_names = [d["district_name"] for d in DISTRICTS]
    print(f"Canonical district names: {district_names}")
    
    return district_names

if __name__ == "__main__":
    create_geojson()