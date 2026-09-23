from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from geoalchemy2.functions import ST_AsGeoJSON, ST_Contains, ST_PointFromText
from sqlalchemy import text

from agrisim_backend.core.config import get_db, settings
from agrisim_backend.models import District
from agrisim_backend.schemas import DistrictResponse, DistrictWithSoilResponse

router = APIRouter(prefix="/api/v1/map", tags=["map"])

# Check if using PostgreSQL with PostGIS
IS_POSTGIS = "postgresql" in settings.DATABASE_URL


@router.get("/districts", response_model=List[DistrictResponse])
async def get_all_districts(
    state: Optional[str] = Query(None, description="Filter by state name"),
    db: Session = Depends(get_db)
):
    """Get all districts, optionally filtered by state."""
    query = db.query(District)
    if state:
        query = query.filter(District.state.ilike(f"%{state}%"))
    districts = query.all()
    return districts


@router.get("/districts/{district_id}", response_model=DistrictResponse)
async def get_district(district_id: int, db: Session = Depends(get_db)):
    """Get a specific district by ID."""
    district = db.query(District).filter(District.id == district_id).first()
    if not district:
        raise HTTPException(status_code=404, detail="District not found")
    return district


@router.get("/districts/{district_id}/with-soil", response_model=DistrictWithSoilResponse)
async def get_district_with_soil(district_id: int, db: Session = Depends(get_db)):
    """Get district with its soil type mappings."""
    district = db.query(District).filter(District.id == district_id).first()
    if not district:
        raise HTTPException(status_code=404, detail="District not found")
    return district


@router.get("/identify-district")
async def identify_district(
    lat: float = Query(..., description="Latitude"),
    lon: float = Query(..., description="Longitude"),
    db: Session = Depends(get_db)
):
    """Identify district from lat/lon coordinates using PostGIS."""
    if not IS_POSTGIS:
        # For SQLite, return a fallback - just return the first district as an example
        district = db.query(District).first()
        if not district:
            raise HTTPException(status_code=404, detail="No districts in database")
        return {
            "district_id": district.id,
            "district_name": district.name,
            "state": district.state,
            "state_code": district.state_code,
            "centroid": {"lat": lat, "lon": lon},
            "note": "Spatial queries require PostgreSQL/PostGIS. Returning first district as fallback."
        }
    
    # Create point from lat/lon
    point_wkt = f"POINT({lon} {lat})"
    
    # Query district containing this point
    district = db.query(District).filter(
        ST_Contains(District.geometry, ST_PointFromText(point_wkt, 4326))
    ).first()
    
    if not district:
        raise HTTPException(status_code=404, detail="No district found for given coordinates")
    
    return {
        "district_id": district.id,
        "district_name": district.name,
        "state": district.state,
        "state_code": district.state_code,
        "centroid": {"lat": lat, "lon": lon}
    }


@router.get("/districts-geojson")
async def get_districts_geojson(
    state: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get all districts as GeoJSON for map rendering."""
    if not IS_POSTGIS:
        # For SQLite, return basic district info without geometry
        query = db.query(District.id, District.name, District.state)
        if state:
            query = query.filter(District.state.ilike(f"%{state}%"))
        results = query.all()
        
        features = []
        for row in results:
            features.append({
                "type": "Feature",
                "properties": {
                    "id": row.id,
                    "name": row.name,
                    "state": row.state
                },
                "geometry": None  # Geometry not available in SQLite
            })
        
        return {
            "type": "FeatureCollection",
            "features": features,
            "note": "Full GeoJSON with geometry requires PostgreSQL/PostGIS"
        }
    
    query = db.query(District.id, District.name, District.state, ST_AsGeoJSON(District.geometry).label("geometry"))
    if state:
        query = query.filter(District.state.ilike(f"%{state}%"))
    
    results = query.all()
    
    features = []
    for row in results:
        import json
        features.append({
            "type": "Feature",
            "properties": {
                "id": row.id,
                "name": row.name,
                "state": row.state
            },
            "geometry": json.loads(row.geometry)
        })
    
    return {
        "type": "FeatureCollection",
        "features": features
    }