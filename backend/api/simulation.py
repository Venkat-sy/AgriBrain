import os
import json
import requests
from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from groq import Groq
from backend.api.spatial import lookup_spatial, fetch_live_weather
from backend.ml.inference.crop_recommendation import compute_shap_values, _get_xgboost_bundle, XGBOOST_FEATURE_COLUMNS
from backend.core.config import get_db

router = APIRouter()

# Expanded 22 Short-Term / Seasonal Crops (Kharif, Rabi, Zaid)
SHORT_TERM_CROPS = [
    {"name": "Rice (Paddy)", "season": "Kharif", "duration_days": 120, "opt_temp": 28, "opt_rain": 210, "opt_ph": 6.0, "opt_n": 180, "base_yield_t_acre": 2.4, "msp_inr_t": 23000, "water_mm": 1200},
    {"name": "Wheat", "season": "Rabi", "duration_days": 115, "opt_temp": 21, "opt_rain": 85, "opt_ph": 7.1, "opt_n": 200, "base_yield_t_acre": 2.1, "msp_inr_t": 22750, "water_mm": 450},
    {"name": "Maize (Hybrid Corn)", "season": "Kharif/Rabi", "duration_days": 105, "opt_temp": 25, "opt_rain": 115, "opt_ph": 6.5, "opt_n": 165, "base_yield_t_acre": 2.6, "msp_inr_t": 20900, "water_mm": 550},
    {"name": "Blackgram (Urad Dal)", "season": "Kharif/Zaid", "duration_days": 80, "opt_temp": 29, "opt_rain": 95, "opt_ph": 6.7, "opt_n": 120, "base_yield_t_acre": 0.65, "msp_inr_t": 69500, "water_mm": 350},
    {"name": "Mungbean (Moong Dal)", "season": "Zaid/Kharif", "duration_days": 70, "opt_temp": 30, "opt_rain": 75, "opt_ph": 6.6, "opt_n": 110, "base_yield_t_acre": 0.6, "msp_inr_t": 85580, "water_mm": 320},
    {"name": "Chickpea (Bengal Gram)", "season": "Rabi", "duration_days": 100, "opt_temp": 22, "opt_rain": 65, "opt_ph": 7.3, "opt_n": 115, "base_yield_t_acre": 0.85, "msp_inr_t": 54400, "water_mm": 300},
    {"name": "Pigeonpea (Tur/Arhar)", "season": "Kharif", "duration_days": 150, "opt_temp": 27, "opt_rain": 110, "opt_ph": 6.8, "opt_n": 135, "base_yield_t_acre": 0.9, "msp_inr_t": 70000, "water_mm": 450},
    {"name": "Groundnut (Peanut)", "season": "Kharif/Rabi", "duration_days": 110, "opt_temp": 28, "opt_rain": 100, "opt_ph": 6.4, "opt_n": 130, "base_yield_t_acre": 1.2, "msp_inr_t": 63770, "water_mm": 500},
    {"name": "Soybean", "season": "Kharif", "duration_days": 95, "opt_temp": 26, "opt_rain": 125, "opt_ph": 6.6, "opt_n": 150, "base_yield_t_acre": 1.1, "msp_inr_t": 46000, "water_mm": 520},
    {"name": "Mustard (Rapeseed)", "season": "Rabi", "duration_days": 105, "opt_temp": 20, "opt_rain": 60, "opt_ph": 7.4, "opt_n": 140, "base_yield_t_acre": 0.95, "msp_inr_t": 56500, "water_mm": 280},
    {"name": "Sunflower", "season": "Rabi/Zaid", "duration_days": 90, "opt_temp": 27, "opt_rain": 80, "opt_ph": 6.9, "opt_n": 145, "base_yield_t_acre": 0.9, "msp_inr_t": 67600, "water_mm": 420},
    {"name": "Cotton (Bt Hybrid)", "season": "Kharif", "duration_days": 160, "opt_temp": 31, "opt_rain": 90, "opt_ph": 7.5, "opt_n": 160, "base_yield_t_acre": 1.15, "msp_inr_t": 66200, "water_mm": 700},
    {"name": "Jute", "season": "Kharif", "duration_days": 120, "opt_temp": 30, "opt_rain": 230, "opt_ph": 6.1, "opt_n": 170, "base_yield_t_acre": 1.8, "msp_inr_t": 50500, "water_mm": 900},
    {"name": "Potato", "season": "Rabi", "duration_days": 95, "opt_temp": 19, "opt_rain": 90, "opt_ph": 5.8, "opt_n": 190, "base_yield_t_acre": 9.5, "msp_inr_t": 14000, "water_mm": 500},
    {"name": "Onion", "season": "Rabi/Kharif", "duration_days": 110, "opt_temp": 24, "opt_rain": 85, "opt_ph": 6.5, "opt_n": 155, "base_yield_t_acre": 7.5, "msp_inr_t": 18000, "water_mm": 450},
    {"name": "Tomato (Hybrid)", "season": "All-Season", "duration_days": 90, "opt_temp": 25, "opt_rain": 95, "opt_ph": 6.4, "opt_n": 175, "base_yield_t_acre": 11.0, "msp_inr_t": 16000, "water_mm": 480},
    {"name": "Chilli (Guntur/Byadgi)", "season": "Kharif/Rabi", "duration_days": 135, "opt_temp": 28, "opt_rain": 105, "opt_ph": 6.6, "opt_n": 160, "base_yield_t_acre": 1.4, "msp_inr_t": 135000, "water_mm": 600},
    {"name": "Okra (Bhindi)", "season": "Zaid/Kharif", "duration_days": 65, "opt_temp": 30, "opt_rain": 110, "opt_ph": 6.5, "opt_n": 140, "base_yield_t_acre": 4.8, "msp_inr_t": 22000, "water_mm": 400},
    {"name": "Watermelon", "season": "Zaid", "duration_days": 80, "opt_temp": 32, "opt_rain": 55, "opt_ph": 6.3, "opt_n": 135, "base_yield_t_acre": 12.0, "msp_inr_t": 11500, "water_mm": 380},
    {"name": "Muskmelon", "season": "Zaid", "duration_days": 75, "opt_temp": 33, "opt_rain": 50, "opt_ph": 6.5, "opt_n": 125, "base_yield_t_acre": 8.5, "msp_inr_t": 16500, "water_mm": 350},
    {"name": "Ragi (Finger Millet)", "season": "Kharif", "duration_days": 105, "opt_temp": 27, "opt_rain": 95, "opt_ph": 6.2, "opt_n": 120, "base_yield_t_acre": 1.3, "msp_inr_t": 38460, "water_mm": 350},
    {"name": "Bajra (Pearl Millet)", "season": "Kharif", "duration_days": 85, "opt_temp": 32, "opt_rain": 50, "opt_ph": 7.6, "opt_n": 100, "base_yield_t_acre": 1.2, "msp_inr_t": 25000, "water_mm": 280}
]

# Expanded 18 Long-Term / Orchard, Plantation & Commercial Crops
LONG_TERM_CROPS = [
    {"name": "Coconut (Tall/Dwarf Hybrid)", "season": "Perennial Plantation", "duration_days": 365, "opt_temp": 29, "opt_rain": 230, "opt_ph": 5.8, "opt_n": 155, "base_yield_t_acre": 4.5, "msp_inr_t": 32000, "water_mm": 1300},
    {"name": "Arecanut (Supari)", "season": "Perennial Plantation", "duration_days": 365, "opt_temp": 28, "opt_rain": 250, "opt_ph": 5.7, "opt_n": 150, "base_yield_t_acre": 1.1, "msp_inr_t": 420000, "water_mm": 1400},
    {"name": "Mango (Alphonso/Kesar)", "season": "Perennial Orchard", "duration_days": 365, "opt_temp": 29, "opt_rain": 115, "opt_ph": 6.5, "opt_n": 165, "base_yield_t_acre": 4.2, "msp_inr_t": 55000, "water_mm": 750},
    {"name": "Banana (Grand Naine Tissue)", "season": "Annual/Perennial", "duration_days": 320, "opt_temp": 28, "opt_rain": 175, "opt_ph": 6.4, "opt_n": 205, "base_yield_t_acre": 18.0, "msp_inr_t": 14500, "water_mm": 1500},
    {"name": "Pomegranate (Bhagwa)", "season": "Perennial Orchard", "duration_days": 280, "opt_temp": 31, "opt_rain": 65, "opt_ph": 7.4, "opt_n": 125, "base_yield_t_acre": 5.5, "msp_inr_t": 85000, "water_mm": 550},
    {"name": "Coffee (Arabica/Robusta)", "season": "Shade Plantation", "duration_days": 365, "opt_temp": 23, "opt_rain": 200, "opt_ph": 5.9, "opt_n": 165, "base_yield_t_acre": 0.65, "msp_inr_t": 280000, "water_mm": 1100},
    {"name": "Black Pepper (Panniyur)", "season": "Perennial Vine", "duration_days": 365, "opt_temp": 27, "opt_rain": 235, "opt_ph": 5.8, "opt_n": 155, "base_yield_t_acre": 0.55, "msp_inr_t": 580000, "water_mm": 1250},
    {"name": "Cashew (Vengurla Hybrid)", "season": "Perennial Orchard", "duration_days": 365, "opt_temp": 29, "opt_rain": 190, "opt_ph": 5.6, "opt_n": 135, "base_yield_t_acre": 0.85, "msp_inr_t": 130000, "water_mm": 650},
    {"name": "Papaya (Red Lady 786)", "season": "Long-Duration Fruit", "duration_days": 270, "opt_temp": 29, "opt_rain": 125, "opt_ph": 6.3, "opt_n": 180, "base_yield_t_acre": 22.0, "msp_inr_t": 12500, "water_mm": 950},
    {"name": "Guava (Taiwan Pink/Allahabad)", "season": "Perennial Orchard", "duration_days": 300, "opt_temp": 27, "opt_rain": 95, "opt_ph": 6.9, "opt_n": 145, "base_yield_t_acre": 8.0, "msp_inr_t": 28000, "water_mm": 620},
    {"name": "Grapes (Thompson Seedless)", "season": "Perennial Vineyard", "duration_days": 330, "opt_temp": 26, "opt_rain": 80, "opt_ph": 6.8, "opt_n": 170, "base_yield_t_acre": 9.5, "msp_inr_t": 48000, "water_mm": 680},
    {"name": "Sweet Orange (Mosambi/Kinnow)", "season": "Perennial Citrus", "duration_days": 340, "opt_temp": 25, "opt_rain": 100, "opt_ph": 6.7, "opt_n": 160, "base_yield_t_acre": 7.5, "msp_inr_t": 34000, "water_mm": 720},
    {"name": "Apple (Gala/Delicious)", "season": "Temperate Orchard", "duration_days": 365, "opt_temp": 16, "opt_rain": 125, "opt_ph": 6.1, "opt_n": 165, "base_yield_t_acre": 6.0, "msp_inr_t": 75000, "water_mm": 650},
    {"name": "Sugarcane (Co-86032)", "season": "Annual/Ratoon", "duration_days": 330, "opt_temp": 28, "opt_rain": 150, "opt_ph": 6.8, "opt_n": 220, "base_yield_t_acre": 42.0, "msp_inr_t": 3400, "water_mm": 1800},
    {"name": "Turmeric (Prathibha/Salem)", "season": "Long-Duration Spice", "duration_days": 260, "opt_temp": 27, "opt_rain": 145, "opt_ph": 6.2, "opt_n": 175, "base_yield_t_acre": 2.3, "msp_inr_t": 140000, "water_mm": 850},
    {"name": "Ginger (Rio-de-Janeiro)", "season": "Long-Duration Spice", "duration_days": 240, "opt_temp": 26, "opt_rain": 165, "opt_ph": 6.0, "opt_n": 170, "base_yield_t_acre": 5.5, "msp_inr_t": 65000, "water_mm": 900},
    {"name": "Rubber (RRII 105)", "season": "Perennial Plantation", "duration_days": 365, "opt_temp": 28, "opt_rain": 260, "opt_ph": 5.4, "opt_n": 145, "base_yield_t_acre": 0.75, "msp_inr_t": 175000, "water_mm": 1500},
    {"name": "Cardamom (Malabar/Mysore)", "season": "Highland Plantation", "duration_days": 365, "opt_temp": 21, "opt_rain": 220, "opt_ph": 5.7, "opt_n": 160, "base_yield_t_acre": 0.22, "msp_inr_t": 1650000, "water_mm": 1350}
]

@router.post("/run")
@router.post("/run-from-location")
async def run_simulation(request: Request, db: Session = Depends(get_db)):
    body = await request.json()
    
    # Support both payload formats:
    # Format 1 (new frontend): district_id, selected_crop, land_area_ha, budget_inr, confirmed_soil_type, rainfall_override_mm, planting_season, planned_start_date
    # Format 2 (legacy): lat, lng, area_acres, setup_type, overrides
    
    district_id = body.get("district_id")
    selected_crop = body.get("selected_crop") or body.get("crop")
    land_area_ha = body.get("land_area_ha") or body.get("land_area")
    area_acres = body.get("area_acres")
    budget_inr = body.get("budget_inr", 100000)
    confirmed_soil_type = body.get("confirmed_soil_type")
    rainfall_override_mm = body.get("rainfall_override_mm", 0)
    planting_season = body.get("planting_season") or body.get("setup_type") or "short-term"
    planned_start_date = body.get("planned_start_date")
    overrides = body.get("overrides") or {}
    lat = body.get("lat")
    lng = body.get("lng") or body.get("lon")
    
    # Determine coordinates and spatial data
    spatial_data = None
    
    if district_id:
        # Look up district by ID to get coordinates
        from backend.models import District
        district = db.query(District).filter(District.id == district_id).first()
        if district and district.latitude and district.longitude:
            lat = float(district.latitude)
            lng = float(district.longitude)
            spatial_data = lookup_spatial(lat, lng, db)
        else:
            # Fallback to coordinate-based lookup
            if lat is None or lng is None:
                lat, lng = 12.9716, 77.5946  # Default Bengaluru
            spatial_data = lookup_spatial(lat, lng, db)
    elif lat is not None and lng is not None:
        spatial_data = lookup_spatial(lat, lng, db)
    else:
        # Default to Bengaluru
        spatial_data = lookup_spatial(12.9716, 77.5946, db)
        lat, lng = 12.9716, 77.5946
    
    district = spatial_data["district"]
    state = spatial_data["state"]
    agro_zone = spatial_data["agro_zone"]
    soil = dict(spatial_data["soil"])
    weather = dict(spatial_data["weather"])
    
    # Convert area to acres if needed
    if land_area_ha is not None:
        area_acres = float(land_area_ha) * 2.471
    elif area_acres is None:
        area_acres = 2.5
    
    # Apply Digital Twin "What-If" Scenario Overrides
    if rainfall_override_mm:
        weather["rainfall"] = float(rainfall_override_mm)
        overrides["rainfall"] = float(rainfall_override_mm)
    if overrides.get("rainfall") is not None:
        weather["rainfall"] = float(overrides["rainfall"])
    if overrides.get("temp") is not None:
        weather["temp"] = float(overrides["temp"])
    if overrides.get("ph") is not None:
        soil["pH"] = float(overrides["ph"])
    if overrides.get("N") is not None:
        soil["N"] = int(overrides["N"])
    if confirmed_soil_type:
        soil["type"] = confirmed_soil_type

    pref = planting_season.lower()
    pool = LONG_TERM_CROPS if ("long" in pref or "orchard" in pref or "tree" in pref or "perennial" in pref) else SHORT_TERM_CROPS

    scored_crops = []
    for c in pool:
        temp_diff = abs(weather["temp"] - c["opt_temp"]) * 2.1
        rain_diff = abs(weather["rainfall"] - c["opt_rain"]) * 0.22
        ph_diff = abs(soil["pH"] - c["opt_ph"]) * 11.5
        n_diff = abs(soil["N"] - c["opt_n"]) * 0.14

        total_penalty = temp_diff + rain_diff + ph_diff + n_diff
        score = max(52.0, min(98.8, round(100.0 - total_penalty * 0.42, 1)))

        # Compute Authentic SHAP Contributions using real ML model
        # Prepare input features for the ML model (7 features: N, P, K, temperature, humidity, ph, rainfall)
        ml_input_features = {
            "N": soil["N"],
            "P": soil.get("P", 40),  # P not in soil dict, use default
            "K": soil.get("K", 150),  # K not in soil dict, use default
            "temperature": weather["temp"],
            "humidity": weather["humidity"],
            "ph": soil["pH"],
            "rainfall": weather["rainfall"],
        }

        # Get real SHAP values from XGBoost model
        xgb_bundle = _get_xgboost_bundle()
        if xgb_bundle:
            shap_features = compute_shap_values(xgb_bundle, ml_input_features, XGBOOST_FEATURE_COLUMNS)
        else:
            shap_features = None

        # Format SHAP breakdown for frontend compatibility
        if shap_features:
            shap_breakdown = [
                {
                    "feature": sf["feature"],
                    "value": sf["value"],
                    "optimal": None,  # ML model doesn't have per-crop optimal values
                    "impact": round(sf["shap_value"], 4),
                }
                for sf in shap_features
            ]
        else:
            # Fallback to heuristic if SHAP unavailable
            shap_breakdown = [
                {"feature": "Temperature (°C)", "value": weather["temp"], "optimal": c["opt_temp"], "impact": round(max(-0.35, 0.35 - temp_diff * 0.02), 2)},
                {"feature": "Rainfall (mm)", "value": weather["rainfall"], "optimal": c["opt_rain"], "impact": round(max(-0.35, 0.35 - rain_diff * 0.015), 2)},
                {"feature": "Soil pH", "value": soil["pH"], "optimal": c["opt_ph"], "impact": round(max(-0.25, 0.25 - ph_diff * 0.02), 2)},
                {"feature": "Soil Nitrogen (N)", "value": soil["N"], "optimal": c["opt_n"], "impact": round(max(-0.25, 0.25 - n_diff * 0.02), 2)},
            ]
        shap_breakdown.sort(key=lambda x: x["impact"], reverse=True)

        scored_crops.append({
            "crop": c["name"],
            "season": c["season"],
            "duration_days": c["duration_days"],
            "confidence": round(score / 100.0, 2),
            "score_pct": score,
            "base_yield_t_acre": c["base_yield_t_acre"],
            "msp_inr_t": c["msp_inr_t"],
            "water_mm": c["water_mm"],
            "shap_breakdown": shap_breakdown
        })

        scored_crops.sort(key=lambda x: x["score_pct"], reverse=True)
    winner = scored_crops[0]
    top_crop = winner["crop"]

    # Digital Twin Module 1: Yield & Revenue Prediction
    suitability_factor = winner["score_pct"] / 100.0
    predicted_yield_per_acre = round(winner["base_yield_t_acre"] * suitability_factor, 2)
    total_yield_tonnes = round(predicted_yield_per_acre * area_acres, 2)
    estimated_revenue_inr = int(total_yield_tonnes * winner["msp_inr_t"])

    # Digital Twin Module 2: Irrigation Water Demand Engine
    effective_rain_mm = weather["rainfall"] * 0.75
    net_irrigation_mm = max(120.0, winner["water_mm"] - effective_rain_mm)
    # 1 mm over 1 acre = 4.047 m³ (4,047 Litres)
    total_water_m3 = round(net_irrigation_mm * 4.047 * area_acres, 1)
    daily_water_liters = int((total_water_m3 * 1000) / max(60, winner["duration_days"]))

    # Digital Twin Module 3: Multi-Hazard Risk Assessment Matrix
    drought_risk = "High" if weather["rainfall"] < 75 else ("Moderate" if weather["rainfall"] < 130 else "Low")
    pest_risk = "High" if (weather["humidity"] > 75 and weather["temp"] > 27) else ("Moderate" if weather["humidity"] > 60 else "Low")
    soil_stress = "High (Acidic/Alkaline Alert)" if (soil["pH"] < 5.5 or soil["pH"] > 7.8) else "Optimal"

    shap_explanation = {
        "top_feature": winner["shap_breakdown"][0]["feature"],
        "contribution": winner["shap_breakdown"][0]["impact"],
        "breakdown": winner["shap_breakdown"],
        "reasoning": (
            f"In {district} ({agro_zone}), {top_crop} achieved {winner['score_pct']}% suitability. "
            f"Primary positive driver: {winner['shap_breakdown'][0]['feature']} (SHAP impact: {winner['shap_breakdown'][0]['impact']})."
        )
    }

    timeline = [
        {"stage_name": "Land Preparation & Basal Nutrition", "days": 15, "agronomy_advice": f"Prepare {area_acres} acres of {soil['type']}. Apply basal NPK ({soil['N']}:{soil['P']}:{soil['K']} kg/ha) and organic FYM."},
        {"stage_name": "Sowing / Orchard Transplanting", "days": 20, "agronomy_advice": f"Plant certified {top_crop} ({winner['season']}). Maintain optimal spacing and initial drip/furrow moisture."},
        {"stage_name": "Vegetative Growth & Irrigation", "days": int(winner["duration_days"] * 0.35), "agronomy_advice": f"Supply ~{daily_water_liters:,} Litres/day across {area_acres} acres. Monitor weeds and top-dress Nitrogen."},
        {"stage_name": "Reproductive / Flowering & Pest Shield", "days": int(winner["duration_days"] * 0.25), "agronomy_advice": f"Pest risk is {pest_risk} at {weather['humidity']}% humidity. Apply preventive neem/micronutrient foliar spray."},
        {"stage_name": "Maturity & Harvest Realization", "days": 20, "agronomy_advice": f"Expected harvest: {total_yield_tonnes} Tonnes (~₹{estimated_revenue_inr:,} estimated value). Harvest in dry weather."}
    ]

    api_key = os.getenv("GROQ_API_KEY")
    if api_key:
        try:
            client = Groq(api_key=api_key)
            prompt = (
                f"Generate a 5-stage cultivation timeline for {area_acres} acres of {top_crop} in {district}, {state} "
                f"(Soil: {soil['type']}, pH {soil['pH']}, Temp {weather['temp']}°C, Rain {weather['rainfall']}mm). "
                "Return ONLY a valid JSON array of 5 objects with keys: 'stage_name' (string), 'days' (integer), 'agronomy_advice' (string)."
            )
            comp = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=600
            )
            raw = comp.choices[0].message.content.strip()
            s, e = raw.find("["), raw.rfind("]")
            if s != -1 and e != -1:
                parsed = json.loads(raw[s:e+1])
                if isinstance(parsed, list) and len(parsed) > 0:
                    timeline = parsed
        except Exception:
            pass

    return {
        "district": district,
        "state": state,
        "agro_zone": agro_zone,
        "area_acres": area_acres,
        "setup_type": pref,
        "weather": weather,
        "soil": soil,
        "recommended_crop": top_crop,
        "season": winner["season"],
        "duration_days": winner["duration_days"],
        "confidence": winner["confidence"],
        "score_pct": winner["score_pct"],
        "alternatives": scored_crops[1:6],
        "digital_twin": {
            "yield_per_acre_tonnes": predicted_yield_per_acre,
            "total_yield_tonnes": total_yield_tonnes,
            "estimated_revenue_inr": estimated_revenue_inr,
            "net_irrigation_mm": round(net_irrigation_mm, 1),
            "total_water_m3": total_water_m3,
            "daily_water_liters": daily_water_liters,
            "risks": {
                "drought": drought_risk,
                "pest_disease": pest_risk,
                "soil_reaction": soil_stress
            }
        },
        "shap_data": shap_explanation,
        "timeline": timeline
    }