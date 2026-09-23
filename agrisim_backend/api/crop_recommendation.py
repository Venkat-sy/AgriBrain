from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from agrisim_backend.core.config import get_db
from agrisim_backend.models import CropProfile, CropCost, CropPrice, District
from agrisim_backend.schemas import (
    CropRecommendationRequest,
    CropRecommendationResponse,
    CropRecommendationItem,
    CropCostResponse,
    CropPriceResponse
)

router = APIRouter(prefix="/api/v1/crop", tags=["crop"])


@router.post("/recommend", response_model=CropRecommendationResponse)
async def recommend_crops(
    request: CropRecommendationRequest,
    db: Session = Depends(get_db)
):
    """
    Recommend crops based on soil, climate, and location parameters.
    This uses a rule-based scoring system (can be replaced with ML model).
    """
    # Verify district exists
    district = db.query(District).filter(District.id == request.district_id).first()
    if not district:
        raise HTTPException(status_code=404, detail="District not found")
    
    # Get all crop profiles
    all_crops = db.query(CropProfile).all()
    
    recommendations = []
    
    for crop in all_crops:
        score = 0.0
        match_reasons = []
        
        # Soil type matching (40% weight)
        if crop.suitable_soil_types and request.soil_type in crop.suitable_soil_types:
            score += 0.4
            match_reasons.append(f"Suitable for {request.soil_type}")
        
        # Rainfall matching (25% weight)
        if crop.rainfall_min_mm and crop.rainfall_max_mm:
            if crop.rainfall_min_mm <= request.rainfall_mm <= crop.rainfall_max_mm:
                score += 0.25
                match_reasons.append(f"Rainfall ({request.rainfall_mm}mm) within optimal range ({crop.rainfall_min_mm}-{crop.rainfall_max_mm}mm)")
            elif request.rainfall_mm < crop.rainfall_min_mm:
                score += 0.1
                match_reasons.append(f"Rainfall below optimal (needs {crop.rainfall_min_mm}mm+)")
            else:
                score += 0.1
                match_reasons.append(f"Rainfall above optimal (max {crop.rainfall_max_mm}mm)")
        
        # Temperature matching (15% weight)
        if crop.temp_min_c and crop.temp_max_c and request.temperature_c:
            if crop.temp_min_c <= request.temperature_c <= crop.temp_max_c:
                score += 0.15
                match_reasons.append(f"Temperature ({request.temperature_c}°C) within optimal range")
            else:
                score += 0.05
                match_reasons.append(f"Temperature outside optimal range ({crop.temp_min_c}-{crop.temp_max_c}°C)")
        
        # pH matching (10% weight)
        if crop.ph_min and crop.ph_max and request.ph:
            if crop.ph_min <= request.ph <= crop.ph_max:
                score += 0.1
                match_reasons.append(f"pH ({request.ph}) within optimal range ({crop.ph_min}-{crop.ph_max})")
            else:
                score += 0.02
                match_reasons.append(f"pH outside optimal range")
        
        # Nutrient matching (10% weight)
        nutrient_score = 0
        nutrient_count = 0
        if crop.n_requirement and request.n:
            nutrient_count += 1
            if request.n >= crop.n_requirement * 0.8:
                nutrient_score += 1
        if crop.p_requirement and request.p:
            nutrient_count += 1
            if request.p >= crop.p_requirement * 0.8:
                nutrient_score += 1
        if crop.k_requirement and request.k:
            nutrient_count += 1
            if request.k >= crop.k_requirement * 0.8:
                nutrient_score += 1
        
        if nutrient_count > 0:
            score += 0.1 * (nutrient_score / nutrient_count)
            if nutrient_score == nutrient_count:
                match_reasons.append("Soil nutrients meet requirements")
        
        # Only include crops with some positive score
        if score > 0.1:
            recommendations.append(CropRecommendationItem(
                crop_name=crop.name,
                confidence=round(score, 2),
                match_reasons=match_reasons,
                expected_yield_tons_per_ha=crop.expected_yield_tons_per_ha,
                season=crop.season
            ))
    
    # Sort by confidence descending and take top_k
    recommendations.sort(key=lambda x: x.confidence, reverse=True)
    recommendations = recommendations[:request.top_k]
    
    return CropRecommendationResponse(
        district_id=request.district_id,
        soil_type=request.soil_type,
        rainfall_mm=request.rainfall_mm,
        recommendations=recommendations,
        model_version="rule_based_v1.0",
        generated_at=datetime.utcnow()
    )


@router.get("/costs/{crop_id}", response_model=List[CropCostResponse])
async def get_crop_costs(
    crop_id: int,
    region: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get input costs for a crop."""
    crop = db.query(CropProfile).filter(CropProfile.id == crop_id).first()
    if not crop:
        raise HTTPException(status_code=404, detail="Crop not found")
    
    query = db.query(CropCost).filter(CropCost.crop_id == crop_id)
    if region:
        query = query.filter(CropCost.region.ilike(f"%{region}%"))
    
    costs = query.all()
    return costs


@router.get("/prices/{crop_id}", response_model=List[CropPriceResponse])
async def get_crop_prices(
    crop_id: int,
    market: Optional[str] = Query(None),
    days_back: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """Get market prices for a crop."""
    crop = db.query(CropProfile).filter(CropProfile.id == crop_id).first()
    if not crop:
        raise HTTPException(status_code=404, detail="Crop not found")
    
    start_date = datetime.utcnow() - timedelta(days=days_back)
    
    query = db.query(CropPrice).filter(
        CropPrice.crop_id == crop_id,
        CropPrice.price_date >= start_date
    )
    if market:
        query = query.filter(CropPrice.market.ilike(f"%{market}%"))
    
    prices = query.order_by(CropPrice.price_date.desc()).all()
    return prices