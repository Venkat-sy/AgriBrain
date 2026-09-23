from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from agrisim_backend.core.config import get_db
from agrisim_backend.models import CropProfile, CropCost, CropPrice, District
from agrisim_backend.schemas import CropProfileResponse

router = APIRouter(prefix="/api/v1/crop", tags=["crop"])


@router.get("/profiles", response_model=List[CropProfileResponse])
async def get_crop_profiles(
    category: Optional[str] = Query(None),
    season: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get all crop profiles with optional filtering."""
    query = db.query(CropProfile)
    if category:
        query = query.filter(CropProfile.category.ilike(f"%{category}%"))
    if season:
        query = query.filter(CropProfile.season.ilike(f"%{season}%"))
    
    crops = query.all()
    return crops


@router.get("/profiles/{crop_id}", response_model=CropProfileResponse)
async def get_crop_profile(crop_id: int, db: Session = Depends(get_db)):
    """Get a specific crop profile by ID."""
    crop = db.query(CropProfile).filter(CropProfile.id == crop_id).first()
    if not crop:
        raise HTTPException(status_code=404, detail="Crop profile not found")
    return crop


@router.get("/profiles/by-name/{crop_name}", response_model=CropProfileResponse)
async def get_crop_profile_by_name(crop_name: str, db: Session = Depends(get_db)):
    """Get a specific crop profile by name."""
    crop = db.query(CropProfile).filter(CropProfile.name.ilike(crop_name)).first()
    if not crop:
        raise HTTPException(status_code=404, detail="Crop profile not found")
    return crop