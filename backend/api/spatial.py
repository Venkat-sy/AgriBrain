import requests
from fastapi import APIRouter, Query

router = APIRouter()

def lookup_spatial(lat: float, lon: float, db=None):
    district = "Regional Farming Hub"
    state = "India"
    try:
        resp = requests.get(
            f"[https://nominatim.openstreetmap.org/reverse?format=json&lat=](https://nominatim.openstreetmap.org/reverse?format=json&lat=){lat}&lon={lon}&zoom=10",
            headers={"User-Agent": "AgriBrain-DigitalTwin/3.0"},
            timeout=5
        )
        if resp.status_code == 200:
            addr = resp.json().get("address", {})
            district = (
                addr.get("state_district")
                or addr.get("county")
                or addr.get("city")
                or addr.get("town")
                or "Regional District"
            )
            state = addr.get("state") or "India"
    except Exception:
        pass

    # Deterministic Agro-Climatic Zone Mapping across India
    is_west_coast = lon < 76.2 and lat < 19.5
    is_east_coast = lon > 79.8 and lat < 21.0
    is_northern_plains = lat > 25.5 and lon > 74.5
    is_arid_west = lon < 74.5 and lat > 22.0
    is_himalayan = lat > 29.8

    if is_himalayan:
        zone = "Western Himalayan Temperate Zone"
        soil_type = "Mountain Forest / Podzolic Loam"
        n, p, k, ph = int(175 + (lat * 2) % 30), int(48 + (lon % 18)), int(155 + (lat % 25)), round(6.1 + (lon % 0.7), 1)
        base_rain, base_hum, temp = round(140.0 + (lon * 3) % 70, 1), int(65 + (lat % 15)), round(16.5 + (lon % 5), 1)
    elif is_west_coast or is_east_coast:
        zone = "Coastal Alluvial & Lateritic Zone"
        soil_type = "Coastal Lateritic / Alluvial Loam"
        n, p, k, ph = int(150 + (lat * 3) % 40), int(38 + (lon % 20)), int(170 + (lat % 35)), round(5.7 + (lon % 1.1), 1)
        base_rain, base_hum, temp = round(240.0 + (lat * 6) % 110, 1), int(79 + (lon % 12)), round(28.5 + (lat % 4), 1)
    elif is_northern_plains:
        zone = "Trans-Gangetic & Indo-Gangetic Plains"
        soil_type = "Deep Indo-Gangetic Alluvial"
        n, p, k, ph = int(220 + (lon * 2) % 50), int(58 + (lat % 22)), int(150 + (lon % 30)), round(7.2 + (lat % 0.7), 1)
        base_rain, base_hum, temp = round(105.0 + (lon * 3) % 65, 1), int(60 + (lat % 15)), round(25.0 + (lon % 6), 1)
    elif is_arid_west:
        zone = "Western Arid & Semi-Arid Zone"
        soil_type = "Arid Sandy / Calcareous Loam"
        n, p, k, ph = int(95 + (lat * 2) % 35), int(28 + (lon % 15)), int(115 + (lat % 25)), round(7.8 + (lon % 0.6), 1)
        base_rain, base_hum, temp = round(48.0 + (lat * 2) % 40, 1), int(38 + (lon % 14)), round(32.5 + (lat % 4), 1)
    else:
        zone = "Central & Southern Deccan Plateau"
        soil_type = "Deccan Black Cotton / Red Loam"
        n, p, k, ph = int(165 + (lat * 3) % 45), int(46 + (lon % 22)), int(140 + (lat % 30)), round(6.6 + (lon % 0.9), 1)
        base_rain, base_hum, temp = round(125.0 + (lat * 4) % 85, 1), int(62 + (lon % 16)), round(27.5 + (lat % 4.5), 1)

    return {
        "district": district,
        "state": state,
        "agro_zone": zone,
        "lat": lat,
        "lng": lon,
        "soil_type": soil_type,
        "soil": {"N": n, "P": p, "K": k, "pH": ph, "type": soil_type},
        "weather": {"temp": temp, "humidity": base_hum, "rainfall": base_rain}
    }

@router.get("/reverse-geocode")
async def reverse_geocode(lat: float = Query(...), lon: float = Query(None), lng: float = Query(None)):
    actual_lon = lon if lon is not None else (lng if lng is not None else 77.5946)
    return lookup_spatial(lat, actual_lon)