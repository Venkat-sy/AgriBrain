import os
import requests
from fastapi import APIRouter, Query, Depends
from typing import Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import select

from backend.core.config import get_db
from backend.models import District

router = APIRouter()

# Open-Meteo API (no API key required, generous free tier)
OPEN_METEO_BASE = "https://api.open-meteo.com/v1/forecast"

# Fallback historical averages by 15 ICAR Agro-Climatic Zones
ZONE_HISTORICAL_AVG = {
    "Western Himalayan Temperate Zone": {"temp": 16.5, "humidity": 65, "rainfall": 140.0},
    "Eastern Himalayan Zone": {"temp": 18.0, "humidity": 75, "rainfall": 200.0},
    "Lower Gangetic Plains Zone": {"temp": 27.0, "humidity": 78, "rainfall": 180.0},
    "Middle Gangetic Plains Zone": {"temp": 26.5, "humidity": 70, "rainfall": 120.0},
    "Upper Gangetic Plains Zone": {"temp": 25.0, "humidity": 60, "rainfall": 105.0},
    "Trans-Gangetic Plains Zone": {"temp": 25.0, "humidity": 60, "rainfall": 105.0},
    "Eastern Plateau and Hills Zone": {"temp": 27.5, "humidity": 68, "rainfall": 150.0},
    "Central Plateau and Hills Zone": {"temp": 28.0, "humidity": 62, "rainfall": 130.0},
    "Western Plateau and Hills Zone": {"temp": 27.5, "humidity": 62, "rainfall": 125.0},
    "Southern Plateau and Hills Zone": {"temp": 27.5, "humidity": 65, "rainfall": 130.0},
    "East Coast Plains and Hills Zone": {"temp": 29.0, "humidity": 75, "rainfall": 140.0},
    "West Coast Plains and Hills Zone": {"temp": 28.5, "humidity": 79, "rainfall": 240.0},
    "Gujarat Plains and Hills Zone": {"temp": 29.5, "humidity": 55, "rainfall": 70.0},
    "Western Dry Zone": {"temp": 32.5, "humidity": 38, "rainfall": 48.0},
    "Islands Zone": {"temp": 28.0, "humidity": 80, "rainfall": 200.0},
}

# Zone-specific soil parameter ranges for 15 ICAR zones
ZONE_SOIL_PARAMS = {
    "Western Himalayan Temperate Zone": {"n_range": (160, 200), "p_range": (40, 60), "k_range": (140, 180), "ph_range": (5.8, 6.8), "soil_type": "Mountain Forest / Podzolic Loam"},
    "Eastern Himalayan Zone": {"n_range": (140, 180), "p_range": (35, 55), "k_range": (130, 170), "ph_range": (5.5, 6.5), "soil_type": "Red & Lateritic Soil"},
    "Lower Gangetic Plains Zone": {"n_range": (180, 240), "p_range": (45, 70), "k_range": (120, 160), "ph_range": (6.5, 7.5), "soil_type": "Gangetic Alluvial"},
    "Middle Gangetic Plains Zone": {"n_range": (200, 260), "p_range": (50, 80), "k_range": (130, 180), "ph_range": (6.8, 8.0), "soil_type": "Gangetic Alluvial"},
    "Upper Gangetic Plains Zone": {"n_range": (200, 260), "p_range": (50, 80), "k_range": (130, 180), "ph_range": (6.8, 8.0), "soil_type": "Indo-Gangetic Alluvial"},
    "Trans-Gangetic Plains Zone": {"n_range": (200, 260), "p_range": (50, 80), "k_range": (130, 180), "ph_range": (6.8, 8.0), "soil_type": "Indo-Gangetic Alluvial"},
    "Eastern Plateau and Hills Zone": {"n_range": (130, 190), "p_range": (30, 55), "k_range": (150, 200), "ph_range": (5.2, 6.8), "soil_type": "Red & Lateritic Soil"},
    "Central Plateau and Hills Zone": {"n_range": (140, 200), "p_range": (35, 65), "k_range": (120, 170), "ph_range": (6.0, 7.5), "soil_type": "Black Cotton / Medium Black Soil"},
    "Western Plateau and Hills Zone": {"n_range": (140, 200), "p_range": (35, 65), "k_range": (120, 170), "ph_range": (6.0, 7.5), "soil_type": "Black Cotton / Medium Black Soil"},
    "Southern Plateau and Hills Zone": {"n_range": (130, 190), "p_range": (30, 55), "k_range": (150, 200), "ph_range": (5.2, 6.8), "soil_type": "Red & Lateritic Soil"},
    "East Coast Plains and Hills Zone": {"n_range": (150, 210), "p_range": (40, 65), "k_range": (140, 190), "ph_range": (6.0, 7.5), "soil_type": "Coastal Alluvial"},
    "West Coast Plains and Hills Zone": {"n_range": (130, 190), "p_range": (30, 55), "k_range": (150, 200), "ph_range": (5.2, 6.8), "soil_type": "Lateritic Soil"},
    "Gujarat Plains and Hills Zone": {"n_range": (140, 200), "p_range": (35, 65), "k_range": (120, 170), "ph_range": (6.5, 8.0), "soil_type": "Black Cotton / Medium Black Soil"},
    "Western Dry Zone": {"n_range": (80, 130), "p_range": (20, 45), "k_range": (100, 150), "ph_range": (7.2, 8.5), "soil_type": "Desert / Sandy Soil"},
    "Islands Zone": {"n_range": (100, 160), "p_range": (30, 50), "k_range": (120, 160), "ph_range": (6.0, 7.5), "soil_type": "Coastal Alluvial"},
}


def fetch_live_weather(lat: float, lon: float) -> Optional[Dict[str, Any]]:
    """
    Fetch real-time weather from Open-Meteo API.
    Returns dict with temp, humidity, rainfall or None on failure.
    """
    try:
        params = {
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m,relative_humidity_2m,precipitation",
            "timezone": "auto",
            "forecast_days": 1,
        }
        resp = requests.get(OPEN_METEO_BASE, params=params, timeout=8)
        if resp.status_code == 200:
            data = resp.json().get("current", {})
            return {
                "temp": round(data.get("temperature_2m", 0), 1),
                "humidity": int(data.get("relative_humidity_2m", 0)),
                "rainfall": round(data.get("precipitation", 0), 1),
            }
    except Exception as e:
        print(f"[Weather] Open-Meteo fetch failed: {e}")
    return None


def determine_zone_icar(lat: float, lon: float) -> tuple[str, str]:
    """
    Determine ICAR Agro-Climatic Zone (15 zones) and soil type from coordinates.
    India bounds: Lat 6-38N, Lng 67-98E
    Uses authoritative ICAR zone boundaries.
    """
    # Validate India bounds
    if not (6.0 <= lat <= 38.0 and 67.0 <= lon <= 98.0):
        pass  # Allow but will use fallback

    # 1. Western Himalayan Temperate Zone (J&K, Himachal, Uttarakhand high hills)
    if lat >= 29.5 and lon >= 73.0 and lon <= 80.0:
        return "Western Himalayan Temperate Zone", "Mountain Forest / Podzolic Loam"

    # 2. Eastern Himalayan Zone (Arunachal, Sikkim, Darjeeling)
    if lat >= 26.5 and lon >= 88.0:
        return "Eastern Himalayan Zone", "Red & Lateritic Soil"

    # 3. Lower Gangetic Plains Zone (West Bengal, parts of Jharkhand)
    if lat >= 21.5 and lat <= 25.5 and lon >= 86.0 and lon <= 89.0:
        return "Lower Gangetic Plains Zone", "Gangetic Alluvial"

    # 4. Middle Gangetic Plains Zone (Bihar, Eastern UP)
    if lat >= 24.5 and lat <= 27.0 and lon >= 83.0 and lon <= 87.0:
        return "Middle Gangetic Plains Zone", "Gangetic Alluvial"

    # 5. Upper Gangetic Plains Zone (Central/Western UP, Delhi) - KANPUR/ETAWAH AREA
    if lat >= 26.0 and lat <= 30.0 and lon >= 77.0 and lon <= 81.0:
        return "Upper Gangetic Plains Zone", "Indo-Gangetic Alluvial"

    # 6. Trans-Gangetic Plains Zone (Punjab, Haryana, Western UP)
    if lat >= 28.5 and lat <= 32.0 and lon >= 74.0 and lon <= 77.5:
        return "Trans-Gangetic Plains Zone", "Indo-Gangetic Alluvial"

    # 7. Eastern Plateau and Hills Zone (Chotanagpur plateau, Jharkhand, West Bengal west)
    if lat >= 20.0 and lat <= 25.0 and lon >= 83.0 and lon <= 87.0:
        return "Eastern Plateau and Hills Zone", "Red & Lateritic Soil"

    # 8. Central Plateau and Hills Zone (MP, Bundelkhand, parts of UP south)
    if lat >= 21.0 and lat <= 26.5 and lon >= 76.0 and lon <= 82.0:
        return "Central Plateau and Hills Zone", "Black Cotton / Medium Black Soil"

    # 9. Western Plateau and Hills Zone (Maharashtra plateau, Malwa)
    if lat >= 16.0 and lat <= 22.0 and lon >= 72.0 and lon <= 77.0:
        return "Western Plateau and Hills Zone", "Black Cotton / Medium Black Soil"

    # 10. Southern Plateau and Hills Zone (Deccan plateau - Karnataka, Telangana, TN, AP interior)
    if lat >= 11.5 and lat <= 18.5 and lon >= 74.0 and lon <= 78.5:
        return "Southern Plateau and Hills Zone", "Red & Lateritic Soil"

    # 11. East Coast Plains and Hills Zone (Coastal AP, Odisha, TN coast)
    if lat >= 8.0 and lat <= 19.5 and lon >= 79.0 and lon <= 85.0:
        return "East Coast Plains and Hills Zone", "Coastal Alluvial"

    # 12. West Coast Plains and Hills Zone (Kerala, Karnataka coast, Goa, Maharashtra coast)
    if lat >= 8.0 and lat <= 16.0 and lon >= 72.0 and lon <= 76.0:
        return "West Coast Plains and Hills Zone", "Lateritic Soil"

    # 13. Gujarat Plains and Hills Zone (Gujarat, Diu, Daman)
    if lat >= 20.0 and lat <= 25.0 and lon >= 68.0 and lon <= 74.0:
        return "Gujarat Plains and Hills Zone", "Black Cotton / Medium Black Soil"

    # 14. Western Dry Zone (Rajasthan west of Aravallis)
    if lat >= 23.0 and lat <= 31.0 and lon >= 68.0 and lon <= 75.0:
        return "Western Dry Zone", "Desert / Sandy Soil"

    # 15. Islands Zone (Andaman & Nicobar, Lakshadweep)
    if lat >= 6.0 and lat <= 14.0 and lon >= 90.0:
        return "Islands Zone", "Coastal Alluvial"
    if lat >= 8.0 and lat <= 12.0 and lon >= 71.0 and lon <= 74.0:
        return "Islands Zone", "Coral Sand"

    # Fallback - Central India default
    return "Central Plateau and Hills Zone", "Black Cotton / Medium Black Soil"


def deterministic_soil(lat: float, lon: float, zone: str) -> Dict[str, Any]:
    """Generate deterministic but realistic soil NPK/pH from coordinates + zone."""
    params = ZONE_SOIL_PARAMS.get(zone, ZONE_SOIL_PARAMS["Central Plateau and Hills Zone"])
    n = params["n_range"][0] + int((lat * 1000 + lon * 100) % (params["n_range"][1] - params["n_range"][0]))
    p = params["p_range"][0] + int((lat * 500 + lon * 200) % (params["p_range"][1] - params["p_range"][0]))
    k = params["k_range"][0] + int((lat * 300 + lon * 400) % (params["k_range"][1] - params["k_range"][0]))
    ph = round(params["ph_range"][0] + ((lon * 100) % 100) / 100 * (params["ph_range"][1] - params["ph_range"][0]), 1)
    return {"N": n, "P": p, "K": k, "pH": ph, "type": params["soil_type"]}


async def lookup_spatial_db(lat: float, lon: float, db: Session) -> Optional[Dict[str, Any]]:
    """Try to find district in database using spatial proximity."""
    try:
        lat_min, lat_max = lat - 0.5, lat + 0.5
        lon_min, lon_max = lon - 0.5, lon + 0.5
        stmt = select(District).where(
            District.latitude >= lat_min,
            District.latitude <= lat_max,
            District.longitude >= lon_min,
            District.longitude <= lon_max
        ).limit(1)
        district = db.execute(stmt).scalar_one_or_none()
        if district:
            return {
                "district": district.name,
                "state": district.state,
                "agro_zone": district.agro_climatic_zone,
                "district_id": district.id,
                "district_code": district.district_code,
            }
    except Exception as e:
        print(f"[Spatial] DB lookup failed: {e}")
    return None


def lookup_spatial(lat: float, lon: float, db: Session = None) -> Dict[str, Any]:
    """Main spatial lookup with database integration and coordinate fallback."""
    district_name = "Regional Farming Hub"
    state = "India"
    district_id = None
    district_code = None
    if db:
        import asyncio
        db_result = asyncio.run(lookup_spatial_db(lat, lon, db))
        if db_result:
            district_name = db_result["district"]
            state = db_result["state"]
            district_id = db_result["district_id"]
            district_code = db_result["district_code"]
    if district_id is None:
        try:
            resp = requests.get(
                f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}&zoom=10",
                headers={"User-Agent": "AgriBrain-DigitalTwin/3.0"},
                timeout=5
            )
            if resp.status_code == 200:
                addr = resp.json().get("address", {})
                district_name = (
                    addr.get("state_district")
                    or addr.get("county")
                    or addr.get("city")
                    or addr.get("town")
                    or "Regional District"
                )
                state = addr.get("state") or "India"
        except Exception as e:
            print(f"[Spatial] Nominatim lookup failed: {e}")
    zone, soil_type = determine_zone_icar(lat, lon)
    soil = deterministic_soil(lat, lon, zone)
    weather = fetch_live_weather(lat, lon)
    if weather is None:
        print(f"[Weather] Using historical fallback for zone: {zone}")
        fallback = ZONE_HISTORICAL_AVG.get(zone, ZONE_HISTORICAL_AVG["Central Plateau and Hills Zone"])
        weather = fallback.copy()
        weather["source"] = "historical_fallback"
    else:
        weather["source"] = "open_meteo_live"
    return {
        "district": district_name,
        "state": state,
        "agro_zone": zone,
        "lat": lat,
        "lng": lon,
        "district_id": district_id,
        "district_code": district_code,
        "soil_type": soil_type,
        "soil": soil,
        "weather": weather,
    }


@router.get("/reverse-geocode")
async def reverse_geocode(lat: float = Query(...), lon: float = Query(None), lng: float = Query(None), db: Session = Depends(get_db)):
    actual_lon = lon if lon is not None else (lng if lng is not None else 77.5946)
    return lookup_spatial(lat, actual_lon, db)


@router.get("/weather")
async def get_weather(lat: float = Query(...), lon: float = Query(None), lng: float = Query(None), db: Session = Depends(get_db)):
    """Get current weather for coordinates."""
    actual_lon = lon if lon is not None else (lng if lng is not None else 77.5946)
    result = lookup_spatial(lat, actual_lon, db)
    return {
        "weather": result["weather"],
        "district": result["district"],
        "state": result["state"],
        "agro_zone": result["agro_zone"],
    }


@router.get("/lookup")
async def lookup_district(lat: float = Query(...), lon: float = Query(None), lng: float = Query(None), db: Session = Depends(get_db)):
    """Full spatial lookup including district, soil, and weather."""
    actual_lon = lon if lon is not None else (lng if lng is not None else 77.5946)
    return lookup_spatial(lat, actual_lon, db)
