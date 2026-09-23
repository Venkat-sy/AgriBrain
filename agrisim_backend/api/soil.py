from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional

from agrisim_backend.core.config import get_db
from agrisim_backend.models import District, SoilType, DistrictSoilType, SoilImageResult
from agrisim_backend.schemas import (
    DistrictSoilResponse,
    SoilTypeResponse,
    DistrictSoilTypeResponse,
    SoilImageRequest,
    SoilImageResponse,
    SoilImageFeedbackRequest
)

router = APIRouter(prefix="/api/v1/soil", tags=["soil"])


@router.get("/types", response_model=List[SoilTypeResponse])
async def get_soil_types(db: Session = Depends(get_db)):
    """Get all reference soil types."""
    soil_types = db.query(SoilType).all()
    return soil_types


@router.get("/types/{soil_type_id}", response_model=SoilTypeResponse)
async def get_soil_type(soil_type_id: int, db: Session = Depends(get_db)):
    """Get a specific soil type by ID."""
    soil_type = db.query(SoilType).filter(SoilType.id == soil_type_id).first()
    if not soil_type:
        raise HTTPException(status_code=404, detail="Soil type not found")
    return soil_type


@router.get("/district/{district_id}", response_model=DistrictSoilResponse)
async def get_district_soil(district_id: int, db: Session = Depends(get_db)):
    """Get soil type composition for a district."""
    district = db.query(District).filter(District.id == district_id).first()
    if not district:
        raise HTTPException(status_code=404, detail="District not found")
    
    soil_mappings = db.query(DistrictSoilType).filter(
        DistrictSoilType.district_id == district_id
    ).all()
    
    soil_types = []
    for mapping in soil_mappings:
        soil_type = db.query(SoilType).filter(SoilType.id == mapping.soil_type_id).first()
        if soil_type:
            soil_types.append(DistrictSoilTypeResponse(
                id=mapping.id,
                district_id=mapping.district_id,
                soil_type_id=mapping.soil_type_id,
                percentage=mapping.percentage,
                is_predominant=bool(mapping.is_predominant),
                soil_type=SoilTypeResponse.model_validate(soil_type)
            ))
    
    return DistrictSoilResponse(
        district_id=district_id,
        district_name=district.name,
        soil_types=soil_types
    )


@router.post("/analyze", response_model=SoilImageResponse)
async def analyze_soil_image(
    file: UploadFile = File(...),
    user_id: str = Form(...),
    lat: Optional[float] = Form(None),
    lon: Optional[float] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Analyze soil image using ML model.
    This is a placeholder - actual ML inference would go here.
    """
    # TODO: Implement actual ML model inference
    # For now, return mock result
    import uuid
    from datetime import datetime
    
    # Save file (in production, use cloud storage)
    file_path = f"uploads/soil/{user_id}_{uuid.uuid4().hex}.jpg"
    
    # Mock prediction - in reality, run ML model here
    predicted_soil = "Alluvial Soil"
    confidence = 0.87
    model_version = "soil_classifier_v1.0"
    
    result = SoilImageResult(
        user_id=user_id,
        image_path=file_path,
        predicted_soil=predicted_soil,
        confidence=confidence,
        model_version=model_version
    )
    db.add(result)
    db.commit()
    db.refresh(result)
    
    return SoilImageResponse.model_validate(result)


@router.post("/confirm", response_model=SoilImageResponse)
async def confirm_soil_type(
    feedback: SoilImageFeedbackRequest,
    db: Session = Depends(get_db)
):
    """Confirm or correct the ML-predicted soil type."""
    result = db.query(SoilImageResult).filter(SoilImageResult.id == feedback.result_id).first()
    if not result:
        raise HTTPException(status_code=404, detail="Soil analysis result not found")
    
    result.user_confirmed_soil = feedback.confirmed_soil
    db.commit()
    db.refresh(result)
    
    return SoilImageResponse.model_validate(result)


@router.get("/history/{user_id}", response_model=List[SoilImageResponse])
async def get_soil_analysis_history(
    user_id: str,
    db: Session = Depends(get_db)
):
    """Get user's soil analysis history."""
    results = db.query(SoilImageResult).filter(
        SoilImageResult.user_id == user_id
    ).order_by(SoilImageResult.created_at.desc()).all()
    
    return [SoilImageResponse.model_validate(r) for r in results]