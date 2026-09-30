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

router = APIRouter(prefix="/api/v1/simulation", tags=["simulation"])


@router.post("/run", response_model=SimulationResponse)
async def run_simulation(
    request: SimulationRequest,
    db: Session = Depends(get_db)
):
    """Run a crop simulation with the given parameters."""
    # Validate district
    district = db.query(District).filter(District.id == request.district_id).first()
    if not district:
        raise HTTPException(status_code=404, detail="District not found")
    
    # Validate crop
    crop = db.query(CropProfile).filter(CropProfile.name.ilike(request.selected_crop)).first()
    if not crop:
        raise HTTPException(status_code=404, detail=f"Crop '{request.selected_crop}' not found")
    
    # Run simulation engine
    engine = SimulationEngine(db)
    result = engine.run_simulation(request, district, crop)
    
    return result


@router.post("/save", response_model=SimulationResultResponse)
async def save_simulation(
    request: SimulationRequest,
    user_id: str = Query(..., description="User ID"),
    db: Session = Depends(get_db)
):
    """Run and save a simulation result."""
    # Validate district
    district = db.query(District).filter(District.id == request.district_id).first()
    if not district:
        raise HTTPException(status_code=404, detail="District not found")
    
    # Validate crop
    crop = db.query(CropProfile).filter(CropProfile.name.ilike(request.selected_crop)).first()
    if not crop:
        raise HTTPException(status_code=404, detail=f"Crop '{request.selected_crop}' not found")
    
    # Run simulation
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
