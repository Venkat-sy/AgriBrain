from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

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
from typing import Optional
from fastapi.concurrency import run_in_threadpool

router = APIRouter(prefix="/api/v1/simulation", tags=["simulation"])

class LocationSimulationRequest(BaseModel):
    """Request to run simulation from map coordinates."""
    lat: float
    lng: float
    land_area_ha: float = 1.0
    budget_inr: float = 50000.0
    top_k: int = 3


class LocationSimulationResponse(BaseModel):
    """Response from location-based simulation."""
    district_name: str
    state: str
    latitude: float
    longitude: float
    soil_type: str
    baseline_parameters: dict
    weather: dict
    recommendations: List[dict]
    timelines: dict

class TimelineStage(BaseModel):
    stage_name: str
    estimated_days: int
    agronomy_advice: str


class TimelineResponse(BaseModel):
    crop_name: str
    stages: List[TimelineStage]


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


@router.get("/timeline", response_model=TimelineResponse)
async def get_cultivation_timeline(crop_name: str = Query(..., description="Name of the crop")):
    """Get cultivation timeline for a specific crop."""
    crop_key = crop_name.lower()
    if crop_key not in CROP_TIMELINES:
        raise HTTPException(status_code=404, detail=f"No timeline data for crop: {crop_name}")
    
    stages = CROP_TIMELINES[crop_key]
    return TimelineResponse(crop_name=crop_name.capitalize(), stages=stages)

class TimelineStage(BaseModel):
    stage_name: str
    estimated_days: int
    agronomy_advice: str


class TimelineResponse(BaseModel):
    crop_name: str
    stages: List[TimelineStage]


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


@router.get("/timeline", response_model=TimelineResponse)
async def get_cultivation_timeline(crop_name: str = Query(..., description="Name of the crop")):
    """Get cultivation timeline for a specific crop."""
    crop_key = crop_name.lower()
    if crop_key not in CROP_TIMELINES:
        raise HTTPException(status_code=404, detail=f"No timeline data for crop: {crop_name}")
    
    stages = CROP_TIMELINES[crop_key]
    return TimelineResponse(crop_name=crop_name.capitalize(), stages=stages)

router = APIRouter(prefix="/api/v1/simulation", tags=["simulation"])

class TimelineStage(BaseModel):
    stage_name: str
    estimated_days: int
    agronomy_advice: str


class TimelineResponse(BaseModel):
    crop_name: str
    stages: List[TimelineStage]


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


@router.get("/timeline", response_model=TimelineResponse)
async def get_cultivation_timeline(crop_name: str = Query(..., description="Name of the crop")):
    """Get cultivation timeline for a specific crop."""
    crop_key = crop_name.lower()
    if crop_key not in CROP_TIMELINES:
        raise HTTPException(status_code=404, detail=f"No timeline data for crop: {crop_name}")
    
    stages = CROP_TIMELINES[crop_key]
    return TimelineResponse(crop_name=crop_name.capitalize(), stages=stages)

@router.post("/run", response_model=SimulationResponse)
async def run_simulation(
    request: SimulationRequest,
    db: Session = Depends(get_db)
):
    """Run a crop simulation with the given parameters."""
    # Validate crop
    crop = db.query(CropProfile).filter(CropProfile.name.ilike(request.selected_crop)).first()
    if not crop:
        raise HTTPException(status_code=404, detail=f"Crop '{request.selected_crop}' not found")
    
    # Try to get district from DB (optional - for metadata only)
    district = db.query(District).filter(District.id == request.district_id).first()
    district_name = district.name if district else f"District_{request.district_id}"
    district_state = district.state if district else "Unknown"
    
    # Run simulation engine (pass district object or None)
    engine = SimulationEngine(db)
    result = engine.run_simulation(request, district, crop)
    
    # Override district name in response if district wasn't in DB
    if not district:
        result.district_name = district_name
    
    return result


@router.post("/save", response_model=SimulationResultResponse)
async def save_simulation(
    request: SimulationRequest,
    user_id: str = Query(..., description="User ID"),
    db: Session = Depends(get_db)
):
    """Run and save a simulation result."""
    # Validate crop
    crop = db.query(CropProfile).filter(CropProfile.name.ilike(request.selected_crop)).first()
    if not crop:
        raise HTTPException(status_code=404, detail=f"Crop '{request.selected_crop}' not found")
    
    # Try to get district from DB (optional - for metadata only)
    district = db.query(District).filter(District.id == request.district_id).first()
    district_name = district.name if district else f"District_{request.district_id}"
    district_state = district.state if district else "Unknown"
    
    # Run simulation
    engine = SimulationEngine(db)
    sim_result = engine.run_simulation(request, district, crop)

    engine = SimulationEngine(db)
    sim_result = engine.run_simulation(request, district, crop)
    
    # Generate farming roadmap
    roadmap = engine.generate_roadmap(request, crop)
    
    # Save to database
    # Convert dates to ISO format strings for JSON serialization
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
# Import for location-based simulation
import numpy as np
import joblib
from pathlib import Path
import httpx
from fastapi.concurrency import run_in_threadpool


def _get_fallback_recommendations():
    return [
        {"crop_name": "rice", "confidence": 0.8, "match_reasons": ["Default fallback"]},
        {"crop_name": "wheat", "confidence": 0.7, "match_reasons": ["Default fallback"]},
        {"crop_name": "maize", "confidence": 0.6, "match_reasons": ["Default fallback"]},
    ]


async def _generate_timelines(crop_recommendations):
    timelines = {}
    try:
        from backend.services.groq_service import generate_cultivation_timeline
        for rec in crop_recommendations:
            crop_name = rec["crop_name"]
            try:
                timeline = await generate_cultivation_timeline(crop_name)
                timelines[crop_name] = timeline
            except Exception as e:
                print(f"Timeline generation failed for {crop_name}: {e}")
                from backend.api.simulation import CROP_TIMELINES
                if crop_name.lower() in CROP_TIMELINES:
                    timelines[crop_name] = CROP_TIMELINES[crop_name.lower()]
    except Exception as e:
        print(f"Groq service unavailable: {e}")
        from backend.api.simulation import CROP_TIMELINES
        for rec in crop_recommendations:
            crop_name = rec["crop_name"].lower()
            if crop_name in CROP_TIMELINES:
                timelines[rec["crop_name"]] = CROP_TIMELINES[crop_name]
    return timelines


@router.post("/run-from-location", response_model=LocationSimulationResponse)
async def run_simulation_from_location(
    request: LocationSimulationRequest,
    db: Session = Depends(get_db)
):
    """Run full simulation pipeline from map coordinates (lat/lng)."""
    # Step 1: Reverse geocode to get district info
    spatial_url = "http://localhost:8000/api/v1/spatial/reverse-geocode"
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            spatial_response = await client.get(spatial_url, params={"lat": request.lat, "lon": request.lng})
            if spatial_response.status_code != 200:
                raise Exception("Spatial lookup failed")
            spatial_data = spatial_response.json()
    except Exception as e:
        from backend.api.spatial import lookup_spatial, reverse_geocode_nominatim
        spatial_data = await lookup_spatial(request.lat, request.lng, db)
        if not spatial_data or spatial_data.get("district_name", "").startswith("Unknown"):
            nominatim_result = await reverse_geocode_nominatim(request.lat, request.lng)
            if nominatim_result:
                spatial_data = {
                    "district_name": nominatim_result["district_name"],
                    "state": nominatim_result["state"],
                    "latitude": request.lat,
                    "longitude": request.lng,
                    "soil_type": "Loamy",
                    "baseline_parameters": {
                        "n": 90, "p": 42, "k": 43, "ph": 6.5,
                        "temperature_c": 27, "humidity_percent": 60, "rainfall_mm": 1000
                    }
                }
    
    district_name = spatial_data.get("district_name", "Unknown")
    state = spatial_data.get("state", "Unknown")
    soil_type = spatial_data.get("soil_type", "Loamy")
    baseline = spatial_data.get("baseline_parameters", {})
    
    # Step 2: Weather from baseline
    weather_data = {
        "temperature": baseline.get("temperature_c", 27),
        "humidity": baseline.get("humidity_percent", 60),
        "rainfall": baseline.get("rainfall_mm", 1000),
        "source": baseline.get("weather_source", "unknown")
    }
    
    # Step 3: Prepare features for XGBoost
    features = np.array([[
        baseline.get("n", 90),
        baseline.get("p", 42),
        baseline.get("k", 43),
        baseline.get("temperature_c", 27),
        baseline.get("humidity_percent", 60),
        baseline.get("ph", 6.5),
        baseline.get("rainfall_mm", 1000)
    ]])
    
    # Step 4: Load and run XGBoost model
    project_root = Path(__file__).resolve().parents[2]
    model_path = project_root / "backend" / "ml" / "saved_models" / "xgboost_crop_model.joblib"
    
    crop_recommendations = []
    if model_path.exists():
        try:
            model_bundle = joblib.load(model_path)
            model = model_bundle["model"]
            label_encoder = model_bundle["label_encoder"]
            probas = model.predict_proba(features)[0]
            top_indices = np.argsort(probas)[::-1][:request.top_k]
            for idx in top_indices:
                crop_name = label_encoder.inverse_transform([idx])[0]
                confidence = float(probas[idx])
                crop_recommendations.append({
                    "crop_name": crop_name,
                    "confidence": confidence,
                    "match_reasons": [f"Model confidence: {confidence:.1%}"]
                })
        except Exception as e:
            print(f"Model inference error: {e}")
            crop_recommendations = _get_fallback_recommendations()
    else:
        crop_recommendations = _get_fallback_recommendations()
    
    # Step 5: Generate timelines
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
