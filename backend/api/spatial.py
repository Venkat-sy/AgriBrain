"""
Spatial lookup API for Pan-India district identification from coordinates.
Uses point-in-polygon queries with district boundary data.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import json
from pathlib import Path
import pandas as pd

from backend.core.config import get_db, settings
from backend.models import District
from backend.schemas import DistrictResponse

router = APIRouter(prefix="/api/v1/spatial", tags=["spatial"])

# Load district boundaries from GeoJSON for spatial lookup
def load_district_boundaries():
    """Load district boundaries from GeoJSON file."""
    project_root = Path(__file__).resolve().parents[2]
    geojson_path = project_root / "datasets" / "raw" / "districts.geojson"
    
    if geojson_path.exists():
        with open(geojson_path, 'r') as f:
            data = json.load(f)
        return data.get("features", [])
    return []

# Simple point-in-polygon check (ray casting algorithm)
def point_in_polygon(lat: float, lon: float, polygon_coords: List[List[float]]) -> bool:
    """Check if a point is inside a polygon using ray casting algorithm."""
    x, y = lon, lat
    inside = False
    
    for i in range(len(polygon_coords)):
        x1, y1 = polygon_coords[i][0], polygon_coords[i][1]
        x2, y2 = polygon_coords[(i + 1) % len(polygon_coords)][0], polygon_coords[(i + 1) % len(polygon_coords)][1]
        
        if ((y1 > y) != (y2 > y)) and (x < (x2 - x1) * (y - y1) / (y2 - y1) + x1):
            inside = not inside
    
    return inside

# Handle MultiPolygon geometries
def point_in_multipolygon(lat: float, lon: float, coordinates: List[List[List[float]]]) -> bool:
    """Check if point is in any polygon of a MultiPolygon."""
    for polygon in coordinates:
        if point_in_polygon(lat, lon, polygon[0]):
            return True
    return False

# Load master dataset for parameter lookups
def get_master_dataset():
    """Load the master dataset for parameter fallbacks."""
    project_root = Path(__file__).resolve().parents[2]
    master_path = project_root / "datasets" / "All_India_AgriSim_Master_Dataset.csv"
    if master_path.exists():
        import pandas as pd
        return pd.read_csv(master_path)
    return None

def get_rainfall_csv():
    """Load the district-wise rainfall normal CSV."""
    project_root = Path(__file__).resolve().parents[2]
    rainfall_path = project_root / "datasets" / "04_rainfall_india" / "district wise rainfall normal.csv"
    if rainfall_path.exists():
        import pandas as pd
        return pd.read_csv(rainfall_path)
    return None

def get_rainfall_for_district(rainfall_df, district: str, state: str):
    """Get annual rainfall for a specific district from CSV."""
    if rainfall_df is None:
        return None
    
    mask = (rainfall_df['STATE_UT_NAME'].str.strip().str.lower() == state.strip().lower()) & \
           (rainfall_df['DISTRICT'].str.strip().str.lower() == district.strip().lower())
    
    match = rainfall_df[mask]
    if not match.empty:
        val = match['ANNUAL'].values[0]
        if pd.notna(val):
            return float(val)
    
    mask = (rainfall_df['STATE_UT_NAME'].str.strip().str.lower() == state.strip().lower()) & \
           (rainfall_df['DISTRICT'].str.strip().str.lower().str.contains(district.strip().lower(), na=False))
    
    match = rainfall_df[mask]
    if not match.empty:
        val = match['ANNUAL'].values[0]
        if pd.notna(val):
            return float(val)
    
    return None

def get_state_average_rainfall(rainfall_df, state: str):
    """Get average rainfall for a state from CSV."""
    if rainfall_df is None:
        return None
    
    state_data = rainfall_df[
        rainfall_df['STATE_UT_NAME'].str.strip().str.lower() == state.strip().lower()
    ]
    
    if not state_data.empty:
        avg_rainfall = state_data['ANNUAL'].mean()
        if pd.notna(avg_rainfall):
            return float(avg_rainfall)
    return None


@router.get("/lookup")
async def spatial_lookup(
    lat: float = Query(..., description="Latitude", ge=6.0, le=38.0),
    lon: float = Query(..., description="Longitude", ge=68.0, le=98.0),
    db: Session = Depends(get_db)
):
    """
    Identify district from lat/lon coordinates using point-in-polygon on district boundaries.
    Returns district info plus baseline agricultural parameters.
    """
    boundaries = load_district_boundaries()
    found_district = None
    
    for feature in boundaries:
        geometry = feature.get("geometry")
        properties = feature.get("properties", {})
        
        if not geometry:
            continue
            
        geom_type = geometry.get("type")
        coords = geometry.get("coordinates")
        
        if geom_type == "Polygon" and coords:
            if point_in_polygon(lat, lon, coords[0]):
                found_district = properties
                break
        elif geom_type == "MultiPolygon" and coords:
            if point_in_multipolygon(lat, lon, coords):
                found_district = properties
                break
    
    district_info = None
    if found_district:
        district_name = found_district.get("name")
        state_name = found_district.get("state")
        
        district_db = db.query(District).filter(
            District.name.ilike(district_name),
            District.state.ilike(state_name)
        ).first()
        
        if district_db:
            district_info = {
                "district_id": district_db.id,
                "district_name": district_db.name,
                "state": district_db.state,
                "state_code": district_db.state_code,
                "latitude": district_db.latitude,
                "longitude": district_db.longitude,
                "soil_type": district_db.soil_type,
                "agro_climatic_zone": district_db.agro_climatic_zone,
                "area_km2": district_db.area_km2,
                "centroid": {"lat": lat, "lon": lon},
                "lookup_method": "spatial_exact"
            }
    
    if not district_info:
        districts = db.query(District).filter(
            District.latitude.isnot(None),
            District.longitude.isnot(None)
        ).all()
        
        if districts:
            min_dist = float('inf')
            nearest = None
            
            for d in districts:
                dist = (d.latitude - lat) ** 2 + (d.longitude - lon) ** 2
                if dist < min_dist:
                    min_dist = dist
                    nearest = d
            
            district_info = {
                "district_id": nearest.id,
                "district_name": nearest.name,
                "state": nearest.state,
                "state_code": nearest.state_code,
                "latitude": nearest.latitude,
                "longitude": nearest.longitude,
                "soil_type": nearest.soil_type,
                "agro_climatic_zone": nearest.agro_climatic_zone,
                "area_km2": nearest.area_km2,
                "centroid": {"lat": lat, "lon": lon},
                "lookup_method": "nearest_centroid",
                "distance_km": round((min_dist ** 0.5) * 111, 1)
            }
    
    if not district_info:
        raise HTTPException(status_code=404, detail="No district found for given coordinates")
    
    master_df = get_master_dataset()
    rainfall_df = get_rainfall_csv()
    
    district_name = district_info["district_name"]
    state_name = district_info["state"]
    soil_type = district_info["soil_type"] or "Alluvial Soil"
    
    n = p = k = ph = temperature_c = humidity_percent = rainfall_mm = None
    lookup_method = "default"
    
    if master_df is not None:
        mask = (master_df['State'].str.strip().str.lower() == state_name.strip().lower()) & \
               (master_df['District'].str.strip().str.lower().str.contains(district_name.strip().lower(), na=False))
        
        district_data = master_df[mask]
        
        if not district_data.empty:
            n = float(district_data['Soil_Nitrogen_kg_ha_Estimate'].median())
            ph = float(district_data['Soil_pH_Estimate'].median())
            soil_defaults = {
                "Black Soil (Regur)": {'p': 30, 'k': 200, 'temp': 27.0, 'humidity': 60},
                "Red Soil (Laterite)": {'p': 20, 'k': 150, 'temp': 27.5, 'humidity': 65},
                "Alluvial Soil": {'p': 28, 'k': 180, 'temp': 26.5, 'humidity': 68},
                "Sandy Soil": {'p': 15, 'k': 100, 'temp': 28.0, 'humidity': 55},
                "Clay Soil": {'p': 35, 'k': 220, 'temp': 26.0, 'humidity': 70},
                "Alluvial": {'p': 28, 'k': 180, 'temp': 26.5, 'humidity': 68},
                "Black Soil": {'p': 30, 'k': 200, 'temp': 27.0, 'humidity': 60},
                "Red Soil": {'p': 20, 'k': 150, 'temp': 27.5, 'humidity': 65},
            }
            defaults = soil_defaults.get(soil_type, soil_defaults["Alluvial Soil"])
            p = defaults['p']
            k = defaults['k']
            temperature_c = defaults['temp']
            humidity_percent = defaults['humidity']
            lookup_method = "master_dataset"
    
    rainfall = get_rainfall_for_district(rainfall_df, district_name, state_name)
    if rainfall is None:
        rainfall = get_state_average_rainfall(rainfall_df, state_name)
    if rainfall is None:
        rainfall = 1000.0
    
    rainfall_mm = rainfall
    
    if n is None:
        soil_n_defaults = {
            "Black Soil (Regur)": 300,
            "Red Soil (Laterite)": 200,
            "Alluvial Soil": 280,
            "Sandy Soil": 150,
            "Clay Soil": 320,
            "Alluvial": 280,
            "Black Soil": 300,
            "Red Soil": 200,
        }
        n = soil_n_defaults.get(soil_type, 250)
        lookup_method = "soil_defaults"
    
    # Defaults for remaining parameters if not set from master dataset
    if p is None:
        p = 20
    if k is None:
        k = 150
    if ph is None:
        ph = 7.0
    if temperature_c is None:
        temperature_c = 27.0
    if humidity_percent is None:
        humidity_percent = 60
    
    district_info.update({
        "baseline_parameters": {
            "n": round(n, 1),
            "p": round(p, 1),
            "k": round(k, 1),
            "ph": round(ph, 2),
            "temperature_c": round(temperature_c, 1),
            "humidity_percent": round(humidity_percent, 1),
            "rainfall_mm": round(rainfall_mm, 1),
            "lookup_method": lookup_method
        },
        "soil_type": soil_type,
        "note": f"Parameters derived via {lookup_method}"
    })
    
    return district_info


@router.get("/districts-geojson")
async def get_all_districts_geojson(
    state: Optional[str] = Query(None, description="Filter by state name"),
    db: Session = Depends(get_db)
):
    """Get all districts as GeoJSON for map rendering (from DB + GeoJSON file)."""
    boundaries = load_district_boundaries()
    
    features = []
    for feature in boundaries:
        props = feature.get("properties", {})
        if state and props.get("state", "").lower() != state.lower():
            continue
        
        district_db = db.query(District).filter(
            District.name.ilike(props.get("name", "")),
            District.state.ilike(props.get("state", ""))
        ).first()
        
        properties = {
            "name": props.get("name"),
            "state": props.get("state"),
            "state_code": props.get("state_code"),
            "district_code": props.get("district_code"),
        }
        
        if district_db:
            properties.update({
                "id": district_db.id,
                "soil_type": district_db.soil_type,
                "latitude": district_db.latitude,
                "longitude": district_db.longitude,
            })
        
        features.append({
            "type": "Feature",
            "properties": properties,
            "geometry": feature.get("geometry")
        })
    
    return {
        "type": "FeatureCollection",
        "features": features
    }


@router.get("/bounds")
async def get_india_bounds():
    """Get India's bounding box for map initialization."""
    return {
        "center": [20.5937, 78.9629],  # India center
        "zoom": 5,
        "bounds": [
            [6.0, 68.0],   # Southwest
            [38.0, 98.0]   # Northeast
        ],
        "max_bounds": [
            [0.0, 60.0],
            [40.0, 100.0]
        ]
    }