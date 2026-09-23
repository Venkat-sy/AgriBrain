from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta

from agrisim_backend.core.config import get_db
from agrisim_backend.models import District, CropProfile, SimulationResult
from agrisim_backend.schemas import (
    FarmingRoadmapResponse,
    RoadmapActivity,
    ActivityType
)
from agrisim_backend.services.simulation_engine import SimulationEngine

router = APIRouter(prefix="/api/v1/roadmap", tags=["roadmap"])


@router.get("/generate", response_model=FarmingRoadmapResponse)
async def generate_roadmap(
    district_id: int = Query(...),
    crop_name: str = Query(...),
    land_area_ha: float = Query(..., gt=0),
    planting_month: int = Query(6, ge=1, le=12),
    db: Session = Depends(get_db)
):
    """Generate a farming roadmap for a crop in a district."""
    # Validate district
    district = db.query(District).filter(District.id == district_id).first()
    if not district:
        raise HTTPException(status_code=404, detail="District not found")
    
    # Validate crop
    crop = db.query(CropProfile).filter(CropProfile.name.ilike(crop_name)).first()
    if not crop:
        raise HTTPException(status_code=404, detail=f"Crop '{crop_name}' not found")
    
    # Create a simulation request object for the engine
    from agrisim_backend.schemas import SimulationRequest
    sim_request = SimulationRequest(
        district_id=district_id,
        selected_crop=crop_name,
        land_area_ha=land_area_ha,
        budget_inr=100000,  # Default budget
        confirmed_soil_type="Alluvial Soil",
        planting_month=planting_month
    )
    
    # Generate roadmap
    engine = SimulationEngine(db)
    activities = engine.generate_roadmap(sim_request, crop)
    
    # Calculate dates
    planting_date = datetime(datetime.now().year, planting_month, 15).date()
    if planting_date < datetime.now().date():
        planting_date = datetime(datetime.now().year + 1, planting_month, 15).date()
    
    duration_days = crop.duration_days or 120
    harvest_date = planting_date + timedelta(days=duration_days)
    
    total_cost = sum(a.estimated_cost or 0 for a in activities)
    
    return FarmingRoadmapResponse(
        crop_name=crop.name,
        district_id=district_id,
        planting_date=planting_date,
        harvest_date=harvest_date,
        total_duration_days=duration_days,
        activities=activities,
        total_estimated_cost=total_cost,
        generated_at=datetime.utcnow()
    )


@router.get("/activities", response_model=List[ActivityType])
async def get_activity_types():
    """Get all available activity types."""
    return list(ActivityType)


@router.get("/from-simulation/{simulation_id}", response_model=FarmingRoadmapResponse)
async def get_roadmap_from_simulation(
    simulation_id: int,
    db: Session = Depends(get_db)
):
    """Get the roadmap from a saved simulation."""
    simulation = db.query(SimulationResult).filter(SimulationResult.id == simulation_id).first()
    if not simulation:
        raise HTTPException(status_code=404, detail="Simulation not found")
    
    if not simulation.farming_roadmap:
        raise HTTPException(status_code=404, detail="No roadmap available for this simulation")
    
    # Convert stored roadmap to response format
    activities = []
    for i, activity_data in enumerate(simulation.farming_roadmap):
        activities.append(RoadmapActivity(
            id=activity_data.get("id", i + 1),
            activity_type=ActivityType(activity_data.get("activity_type", "land_preparation")),
            title=activity_data.get("title", ""),
            description=activity_data.get("description"),
            start_date=datetime.fromisoformat(activity_data["start_date"]).date() if "start_date" in activity_data else None,
            end_date=datetime.fromisoformat(activity_data["end_date"]).date() if "end_date" in activity_data else None,
            estimated_cost=activity_data.get("estimated_cost"),
            is_critical=activity_data.get("is_critical", False),
            depends_on=activity_data.get("depends_on")
        ))
    
    # Calculate dates from simulation
    crop = db.query(CropProfile).filter(CropProfile.name.ilike(simulation.selected_crop)).first()
    duration_days = crop.duration_days if crop else 120
    
    # Estimate planting date from first activity
    planting_date = activities[0].start_date if activities else datetime.now().date()
    harvest_date = planting_date + timedelta(days=duration_days) if planting_date else datetime.now().date()
    
    total_cost = sum(a.estimated_cost or 0 for a in activities)
    
    return FarmingRoadmapResponse(
        crop_name=simulation.selected_crop,
        district_id=simulation.district_id,
        planting_date=planting_date,
        harvest_date=harvest_date,
        total_duration_days=duration_days,
        activities=activities,
        total_estimated_cost=total_cost,
        generated_at=simulation.created_at
    )