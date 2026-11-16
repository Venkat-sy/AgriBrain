"""
Digital Twin Simulation Orchestrator - AgriBrain
Strict spec: guide2.txt / AGRIBRAIN_STRICT_SPEC.txt
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from pathlib import Path
import os
import json
import numpy as np
import joblib
import requests

from backend.core.config import get_db
from backend.models import (
    District, CropProfile, CropCost, CropPrice, SimulationResult
)
from backend.schemas import (
    SimulationRequest,
    SimulationResponse,
    SimulationResultResponse,
    SimulationListResponse,
    CostBreakdownItem,
    RiskLevel
)
from backend.services.simulation_engine import SimulationEngine
from pydantic import BaseModel
from fastapi.concurrency import run_in_threadpool

router = APIRouter(prefix="/api/v1/simulation", tags=["simulation"])

# ---------------------------------------------------------------------------
# Pydantic schemas per strict spec (guide2.txt section 1)
# ---------------------------------------------------------------------------

class TimelineStage(BaseModel):
    stage_name: str
    estimated_days: int
    agronomy_advice: str


class DigitalTwinRequest(BaseModel):
    """Request body for the new /run endpoint per strict spec."""
    lat: float
    lng: float
    setup_type: str = "short-term"   # "short-term" | "long-term"


class DigitalTwinResponse(BaseModel):
    """Response per strict spec section 1."""
    district: str
    soil_n: float
    soil_p: float
    soil_k: float
    soil_ph: float
    live_temp: float
    live_humidity: float
    live_rainfall: float
    recommended_crop: str
    confidence_score: float
    cultivation_timeline: List[TimelineStage]


class LocationSimulationRequest(BaseModel):
    """Legacy: run simulation from map coordinates."""
    lat: float
    lng: float
    land_area_ha: float = 1.0
    budget_inr: float = 50000.0
    top_k: int = 3


class LocationSimulationResponse(BaseModel):
    """Legacy response from location-based simulation."""
    district_name: str
    state: str
    latitude: float
    longitude: float
    soil_type: str
    baseline_parameters: dict
    weather: dict
    recommendations: List[dict]
    timelines: dict


class TimelineResponse(BaseModel):
    crop_name: str
    stages: List[TimelineStage]


# ---------------------------------------------------------------------------
# Crop classification sets per spec
# ---------------------------------------------------------------------------
LONG_TERM_CROPS = {
    "apple", "banana", "papaya", "coconut", "grapes", "orange",
    "mango", "pomegranate", "coffee"
}
SHORT_TERM_CROPS = {
    "rice", "maize", "mungbean", "blackgram", "mothbeans", "lentil",
    "chickpea", "kidneybeans", "pigeonpeas", "jute", "cotton",
    "watermelon", "muskmelon", "wheat"
}

# ---------------------------------------------------------------------------
# Static fallback timelines (5 key crops)
# ---------------------------------------------------------------------------
CROP_TIMELINES = {
    "rice": [
        {"stage_name": "Sowing & Germination", "estimated_days": 15, "agronomy_advice": "Maintain 2-3 cm standing water. Use certified seeds. Apply starter fertilizer (N:P:K = 20:40:20 kg/ha)."},
        {"stage_name": "Vegetative Stage", "estimated_days": 35, "agronomy_advice": "Apply 50% N at tillering. Maintain 5 cm water depth. Monitor for stem borer and leaf folder."},
        {"stage_name": "Reproductive/Flowering", "estimated_days": 20, "agronomy_advice": "Critical water stage - maintain 5 cm water. Apply remaining 25% N at panicle initiation. Monitor for blast and bacterial leaf blight."},
        {"stage_name": "Ripening", "estimated_days": 25, "agronomy_advice": "Drain field 10-15 days before harvest. Stop irrigation. Monitor for grain discoloration and pests."},
        {"stage_name": "Harvesting", "estimated_days": 10, "agronomy_advice": "Harvest at 20-22% moisture. Use combine or manual harvest. Dry to 14% moisture for storage."}
    ],
    "wheat": [
        {"stage_name": "Sowing & Germination", "estimated_days": 12, "agronomy_advice": "Sow at 4-5 cm depth. Apply DAP (125 kg/ha) + Urea (50 kg/ha) at sowing. Irrigate lightly after sowing."},
        {"stage_name": "Vegetative Stage", "estimated_days": 30, "agronomy_advice": "First irrigation at 21 days (CRI stage). Apply remaining 50% N. Monitor for termites and aphids."},
        {"stage_name": "Reproductive/Flowering", "estimated_days": 20, "agronomy_advice": "Critical irrigation at booting and flowering. Avoid water stress. Apply ZnSO4 if deficient."},
        {"stage_name": "Ripening", "estimated_days": 20, "agronomy_advice": "Stop irrigation at dough stage. Monitor for rust and aphids. Prepare for harvest."},
        {"stage_name": "Harvesting", "estimated_days": 7, "agronomy_advice": "Harvest at 12-14% moisture. Combine harvest preferred. Dry to 12% for storage."}
    ],
    "cotton": [
        {"stage_name": "Sowing & Germination", "estimated_days": 10, "agronomy_advice": "Sow at 3-4 cm depth. Apply FYM (10 t/ha) + NPK (120:60:60). Treat seeds with imidacloprid."},
        {"stage_name": "Vegetative Stage", "estimated_days": 40, "agronomy_advice": "Intercrop with pulses. Apply 2nd split of N at squaring. Monitor for jassids and thrips."},
        {"stage_name": "Reproductive/Flowering", "estimated_days": 35, "agronomy_advice": "Critical stage - avoid water stress. Apply naphthalene acetic acid for boll retention. Monitor for pink bollworm."},
        {"stage_name": "Ripening", "estimated_days": 25, "agronomy_advice": "Reduce irrigation. Apply potassium for boll development. Monitor for boll rot."},
        {"stage_name": "Harvesting", "estimated_days": 15, "agronomy_advice": "Pick in 3-4 flushes. Morning picking preferred. Grade and store properly."}
    ],
    "maize": [
        {"stage_name": "Sowing & Germination", "estimated_days": 10, "agronomy_advice": "Sow at 5 cm depth with 60x20 cm spacing. Apply starter fertilizer. Monitor for cutworms."},
        {"stage_name": "Vegetative Stage", "estimated_days": 30, "agronomy_advice": "Earth up at knee-high stage. Apply 50% N at knee-high. Monitor for fall armyworm."},
        {"stage_name": "Reproductive/Flowering", "estimated_days": 20, "agronomy_advice": "Critical water stage - tasseling to silking. Avoid water stress. Detassel if seed production."},
        {"stage_name": "Ripening", "estimated_days": 20, "agronomy_advice": "Monitor grain fill. Reduce irrigation. Protect from birds and pests."},
        {"stage_name": "Harvesting", "estimated_days": 7, "agronomy_advice": "Harvest at 20-25% moisture. Shell and dry to 14%. Store in aerated bins."}
    ],
    "sugarcane": [
        {"stage_name": "Sowing & Germination", "estimated_days": 20, "agronomy_advice": "Plant 3-budded setts at 90 cm spacing. Apply FYM 25 t/ha + NPK. Irrigate immediately."},
        {"stage_name": "Vegetative Stage", "estimated_days": 90, "agronomy_advice": "Earthing up at 45 and 90 days. Split N application (4 splits). Monitor for early shoot borer."},
        {"stage_name": "Reproductive/Flowering", "estimated_days": 60, "agronomy_advice": "Grand growth phase - heavy N and K. Monitor for top borer and pyrilla. Propping at 180 days."},
        {"stage_name": "Ripening", "estimated_days": 60, "agronomy_advice": "Stop irrigation 3 weeks before harvest. Cane maturity at 18-20% brix. Burning if needed."},
        {"stage_name": "Harvesting", "estimated_days": 10, "agronomy_advice": "Harvest at ground level. Crush within 24 hours. Ratoon management for next crop."}
    ]
}

# ---------------------------------------------------------------------------
# Lazy-loaded XGBoost bundle (module-level, loaded once)
# ---------------------------------------------------------------------------
_BUNDLE = None

def _load_bundle():
    global _BUNDLE
    if _BUNDLE is None:
        project_root = Path(__file__).resolve().parents[2]
        model_path = project_root / "backend" / "ml" / "saved_models" / "xgboost_crop_model.joblib"
        if model_path.exists():
            try:
                _BUNDLE = joblib.load(str(model_path))
                print(f"[XGBoost] Model loaded from {model_path}")
            except Exception as e:
                print(f"[XGBoost] Failed to load model: {e}")
                _BUNDLE = None
    return _BUNDLE


# ---------------------------------------------------------------------------
# Reverse geocode via Nominatim (synchronous, runs in threadpool)
# ---------------------------------------------------------------------------
def _reverse_geocode_sync(lat: float, lng: float) -> str:
    """Synchronous Nominatim reverse geocode. Returns district name string."""
    try:
        r = requests.get(
            "https://nominatim.openstreetmap.org/reverse",
            params={"format": "json", "lat": lat, "lon": lng, "zoom": 10, "addressdetails": 1},
            headers={"User-Agent": "AgriBrain/1.0"},
            timeout=5
        )
        if r.status_code == 200:
            data = r.json()
            addr = data.get("address", {})
            district = (
                addr.get("state_district") or
                addr.get("county") or
                addr.get("city_district") or
                addr.get("city") or
                addr.get("town") or
                addr.get("village") or
                "Unknown"
            )
            return district
    except Exception as e:
        print(f"[Nominatim] Error: {e}")
    return "Unknown"


# ---------------------------------------------------------------------------
# Generate LLM timeline via Groq (runs inside function — ZERO global client)
# ---------------------------------------------------------------------------
def _generate_timeline_sync(crop: str, district: str) -> List[dict]:
    """Generate a cultivation timeline using Groq LLM. Fallback to static dict."""
    try:
        from groq import Groq
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        prompt = (
            f"Generate a cultivation timeline for {crop} farming in {district}, India. "
            f"Return strictly a JSON array of objects with keys: stage_name, estimated_days, agronomy_advice. "
            f"Include 5 stages: Sowing & Germination, Vegetative Stage, Reproductive/Flowering, Ripening, Harvesting. "
            f"Output ONLY the JSON array, no markdown, no extra text."
        )
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
            max_tokens=800,
        )
        raw = response.choices[0].message.content.strip()
        # Strip markdown fences if present
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        stages = json.loads(raw)
        if isinstance(stages, list) and len(stages) > 0:
            return stages
    except Exception as e:
        print(f"[Groq Timeline] Error for {crop}: {e}")

    # Fallback to static
    key = crop.lower()
    if key in CROP_TIMELINES:
        return CROP_TIMELINES[key]
    # Generic 5-stage fallback
    return [
        {"stage_name": "Sowing & Germination", "estimated_days": 14, "agronomy_advice": f"Prepare field. Sow {crop} seeds at recommended depth. Irrigate lightly."},
        {"stage_name": "Vegetative Stage", "estimated_days": 30, "agronomy_advice": f"Apply nitrogen fertilizer. Monitor for pests. Irrigate at critical stages."},
        {"stage_name": "Reproductive/Flowering", "estimated_days": 20, "agronomy_advice": f"Avoid water stress during flowering. Apply micronutrients if deficient."},
        {"stage_name": "Ripening", "estimated_days": 20, "agronomy_advice": f"Reduce irrigation. Monitor maturity indicators. Prepare for harvest."},
        {"stage_name": "Harvesting", "estimated_days": 7, "agronomy_advice": f"Harvest at right moisture. Dry and store properly to minimize post-harvest losses."},
    ]


# ---------------------------------------------------------------------------
# NEW /run endpoint — Digital Twin Orchestrator (strict spec)
# ---------------------------------------------------------------------------
@router.post("/run", response_model=DigitalTwinResponse)
async def run_digital_twin(request: DigitalTwinRequest):
    """
    Digital Twin simulation endpoint per AGRIBRAIN_STRICT_SPEC.txt.
    Flow: reverse geocode -> weather -> soil defaults -> XGBoost -> filter by setup_type -> LLM timeline.
    """
    # Step 1: Reverse geocode
    district = await run_in_threadpool(_reverse_geocode_sync, request.lat, request.lng)

    # Step 2: Live weather via weather_service
    try:
        from backend.services.weather_service import get_live_weather
        weather = await run_in_threadpool(
            get_live_weather,
            district,
            {"temperature": 28.0, "humidity": 65.0, "rainfall": 100.0}
        )
        temp = float(weather.get("temperature", 28.0))
        humidity = float(weather.get("humidity", 65.0))
        rainfall = float(weather.get("rainfall", 100.0))
    except Exception as e:
        print(f"[Weather] Error: {e}")
        temp, humidity, rainfall = 28.0, 65.0, 100.0

    # Step 3: Soil baseline (India-wide defaults per spec: N=150, P=20, K=120, pH=6.5)
    soil_n, soil_p, soil_k, soil_ph = 150.0, 20.0, 120.0, 6.5

    # Step 4: XGBoost inference
    bundle = _load_bundle()
    recommended_crop = "rice"
    confidence_score = 0.5

    if bundle is not None:
        try:
            model = bundle["model"]
            label_encoder = bundle["label_encoder"]
            # Feature order: N, P, K, temperature, humidity, ph, rainfall
            X = np.array([[soil_n, soil_p, soil_k, temp, humidity, soil_ph, rainfall]])
            probs = model.predict_proba(X)[0]
            sorted_indices = np.argsort(probs)[::-1]

            # Step 5: Filter by setup_type
            selected_idx = None
            selected_confidence = 0.0

            for idx in sorted_indices[:10]:
                crop_name = label_encoder.inverse_transform([idx])[0].lower()
                if request.setup_type == "long-term":
                    if crop_name in LONG_TERM_CROPS:
                        selected_idx = idx
                        selected_confidence = float(probs[idx])
                        break
                else:  # short-term (default)
                    if crop_name not in LONG_TERM_CROPS:
                        selected_idx = idx
                        selected_confidence = float(probs[idx])
                        break

            # Fallback: highest probability overall
            if selected_idx is None:
                selected_idx = sorted_indices[0]
                selected_confidence = float(probs[selected_idx])

            recommended_crop = label_encoder.inverse_transform([selected_idx])[0]
            confidence_score = round(selected_confidence, 4)

        except Exception as e:
            print(f"[XGBoost Inference] Error: {e}")
            recommended_crop = "rice" if request.setup_type == "short-term" else "mango"
            confidence_score = 0.5
    else:
        # No model — deterministic fallback
        recommended_crop = "rice" if request.setup_type == "short-term" else "mango"
        confidence_score = 0.5

    # Step 6: Generate LLM timeline
    raw_stages = await run_in_threadpool(_generate_timeline_sync, recommended_crop, district)

    # Coerce to TimelineStage objects
    stages = []
    for s in raw_stages:
        try:
            stages.append(TimelineStage(
                stage_name=str(s.get("stage_name", "Stage")),
                estimated_days=int(s.get("estimated_days", 14)),
                agronomy_advice=str(s.get("agronomy_advice", "Follow recommended agronomic practices."))
            ))
        except Exception:
            pass

    # Step 7: Return payload
    return DigitalTwinResponse(
        district=district,
        soil_n=round(soil_n, 1),
        soil_p=round(soil_p, 1),
        soil_k=round(soil_k, 1),
        soil_ph=round(soil_ph, 2),
        live_temp=round(temp, 1),
        live_humidity=round(humidity, 1),
        live_rainfall=round(rainfall, 1),
        recommended_crop=recommended_crop,
        confidence_score=confidence_score,
        cultivation_timeline=stages
    )


# ---------------------------------------------------------------------------
# GET /timeline - static cultivation timeline lookup
# ---------------------------------------------------------------------------
@router.get("/timeline", response_model=TimelineResponse)
async def get_cultivation_timeline(crop_name: str = Query(..., description="Name of the crop")):
    """Get static cultivation timeline for a specific crop."""
    crop_key = crop_name.lower()
    if crop_key not in CROP_TIMELINES:
        raise HTTPException(status_code=404, detail=f"No timeline data for crop: {crop_name}")
    stages = [TimelineStage(**s) for s in CROP_TIMELINES[crop_key]]
    return TimelineResponse(crop_name=crop_name.capitalize(), stages=stages)


# ---------------------------------------------------------------------------
# Legacy: POST /run-from-location (kept for backward compat)
# ---------------------------------------------------------------------------
def _get_fallback_recommendations():
    return [
        {"crop_name": "rice", "confidence": 0.8, "match_reasons": ["Default fallback"]},
        {"crop_name": "wheat", "confidence": 0.7, "match_reasons": ["Default fallback"]},
        {"crop_name": "maize", "confidence": 0.6, "match_reasons": ["Default fallback"]},
    ]


async def _generate_timelines(crop_recommendations):
    timelines = {}
    for rec in crop_recommendations:
        crop_name = rec["crop_name"]
        try:
            stages = await run_in_threadpool(_generate_timeline_sync, crop_name, "India")
            timelines[crop_name] = stages
        except Exception as e:
            print(f"Timeline generation failed for {crop_name}: {e}")
            if crop_name.lower() in CROP_TIMELINES:
                timelines[crop_name] = CROP_TIMELINES[crop_name.lower()]
    return timelines


@router.post("/run-from-location", response_model=LocationSimulationResponse)
async def run_simulation_from_location(
    request: LocationSimulationRequest,
    db: Session = Depends(get_db)
):
    """Legacy: Run full simulation pipeline from map coordinates (lat/lng)."""
    from backend.api.spatial import reverse_geocode_nominatim

    # Reverse geocode
    nominatim_result = await reverse_geocode_nominatim(request.lat, request.lng)
    district_name = nominatim_result["district_name"] if nominatim_result else "Unknown"
    state = nominatim_result["state"] if nominatim_result else "Unknown"

    soil_type = "Loamy"
    baseline = {"n": 90, "p": 42, "k": 43, "ph": 6.5,
                "temperature_c": 27, "humidity_percent": 60, "rainfall_mm": 1000}

    # Weather
    try:
        from backend.services.weather_service import get_live_weather
        weather_data_raw = await run_in_threadpool(
            get_live_weather, district_name,
            {"temperature": 27, "humidity": 60, "rainfall": 1000}
        )
        weather_data = {
            "temperature": weather_data_raw.get("temperature", 27),
            "humidity": weather_data_raw.get("humidity", 60),
            "rainfall": weather_data_raw.get("rainfall", 1000),
            "source": weather_data_raw.get("source", "default")
        }
        baseline["temperature_c"] = weather_data["temperature"]
        baseline["humidity_percent"] = weather_data["humidity"]
        baseline["rainfall_mm"] = weather_data["rainfall"]
    except Exception as e:
        print(f"[Weather] Error: {e}")
        weather_data = {"temperature": 27, "humidity": 60, "rainfall": 1000, "source": "default"}

    # XGBoost inference
    bundle = _load_bundle()
    crop_recommendations = []

    if bundle is not None:
        try:
            model = bundle["model"]
            label_encoder = bundle["label_encoder"]
            X = np.array([[
                baseline["n"], baseline["p"], baseline["k"],
                baseline["temperature_c"], baseline["humidity_percent"],
                baseline["ph"], baseline["rainfall_mm"]
            ]])
            probs = model.predict_proba(X)[0]
            top_indices = np.argsort(probs)[::-1][:request.top_k]
            for idx in top_indices:
                crop_name = label_encoder.inverse_transform([idx])[0]
                confidence = float(probs[idx])
                crop_recommendations.append({
                    "crop_name": crop_name,
                    "confidence": confidence,
                    "match_reasons": [f"Model confidence: {confidence:.1%}"]
                })
        except Exception as e:
            print(f"[XGBoost] Legacy inference error: {e}")
            crop_recommendations = _get_fallback_recommendations()
    else:
        crop_recommendations = _get_fallback_recommendations()

    timelines = await _generate_timelines(crop_recommendations)

    return LocationSimulationResponse(
        district_name=district_name,
        state=state,
        latitude=request.lat,
        longitude=request.lng,
        soil_type=soil_type,
        baseline_parameters=baseline,
        weather=weather_data,
        recommendations=crop_recommendations,
        timelines=timelines
    )


# ---------------------------------------------------------------------------
# Legacy DB-backed simulation routes (unchanged)
# ---------------------------------------------------------------------------

@router.post("/simulate", response_model=SimulationResponse)
async def run_simulation(
    request: SimulationRequest,
    db: Session = Depends(get_db)
):
    """Run a crop simulation with the given parameters (legacy DB route)."""
    crop = db.query(CropProfile).filter(CropProfile.name.ilike(request.selected_crop)).first()
    if not crop:
        raise HTTPException(status_code=404, detail=f"Crop '{request.selected_crop}' not found")

    district = db.query(District).filter(District.id == request.district_id).first()

    engine = SimulationEngine(db)
    result = engine.run_simulation(request, district, crop)

    if not district:
        result.district_name = f"District_{request.district_id}"

    return result


@router.post("/save", response_model=SimulationResultResponse)
async def save_simulation(
    request: SimulationRequest,
    user_id: str = Query(..., description="User ID"),
    db: Session = Depends(get_db)
):
    """Run and save a simulation result."""
    crop = db.query(CropProfile).filter(CropProfile.name.ilike(request.selected_crop)).first()
    if not crop:
        raise HTTPException(status_code=404, detail=f"Crop '{request.selected_crop}' not found")

    district = db.query(District).filter(District.id == request.district_id).first()

    engine = SimulationEngine(db)
    sim_result = engine.run_simulation(request, district, crop)
    roadmap = engine.generate_roadmap(request, crop)

    def activity_to_dict(activity):
        d = activity.model_dump()
        d['start_date'] = activity.start_date.isoformat()
        d['end_date'] = activity.end_date.isoformat()
        d['activity_type'] = activity.activity_type.value
        return d

    saved_result = SimulationResult(
        user_id=user_id,
        district_id=request.district_id,
        selected_crop=request.selected_crop,
        land_area_ha=request.land_area_ha,
        budget_inr=request.budget_inr,
        confirmed_soil_type=request.confirmed_soil_type,
        rainfall_override_mm=request.rainfall_override_mm,
        plant_capacity=sim_result.plant_capacity,
        total_cost_inr=sim_result.total_cost_inr,
        cost_breakdown=[item.model_dump() for item in sim_result.cost_breakdown],
        estimated_yield_tons=sim_result.estimated_yield_tons,
        estimated_yield_tons_per_ha=sim_result.estimated_yield_tons_per_ha,
        market_value_inr=sim_result.market_value_inr,
        net_profit_inr=sim_result.net_profit_inr,
        roi_percentage=sim_result.roi_percentage,
        risk_level=sim_result.risk_level.value,
        risk_factors=sim_result.risk_factors,
        farming_roadmap=[activity_to_dict(activity) for activity in roadmap],
        status="completed"
    )

    db.add(saved_result)
    db.commit()
    db.refresh(saved_result)

    return SimulationResultResponse.model_validate(saved_result)


@router.get("/history/{user_id}", response_model=SimulationListResponse)
async def get_simulation_history(
    user_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Get user's simulation history with pagination."""
    query = db.query(SimulationResult).filter(SimulationResult.user_id == user_id)
    total = query.count()
    results = query.order_by(SimulationResult.created_at.desc()).offset(
        (page - 1) * page_size
    ).limit(page_size).all()

    return SimulationListResponse(
        results=[SimulationResultResponse.model_validate(r) for r in results],
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/result/{result_id}", response_model=SimulationResultResponse)
async def get_simulation_result(result_id: int, db: Session = Depends(get_db)):
    """Get a specific simulation result by ID."""
    result = db.query(SimulationResult).filter(SimulationResult.id == result_id).first()
    if not result:
        raise HTTPException(status_code=404, detail="Simulation result not found")
    return SimulationResultResponse.model_validate(result)


@router.delete("/result/{result_id}")
async def delete_simulation_result(result_id: int, db: Session = Depends(get_db)):
    """Delete a simulation result."""
    result = db.query(SimulationResult).filter(SimulationResult.id == result_id).first()
    if not result:
        raise HTTPException(status_code=404, detail="Simulation result not found")
    db.delete(result)
    db.commit()
    return {"message": "Simulation result deleted successfully"}
