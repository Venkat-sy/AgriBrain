from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.concurrency import run_in_threadpool
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from backend.core.config import get_db
from backend.models import CropProfile, CropCost, CropPrice, District
from backend.schemas import (
    CropRecommendationRequest,
    CropRecommendationResponse,
    CropRecommendationItem,
    CropCostResponse,
    CropPriceResponse
)
from backend.services.weather_service import get_live_weather
import importlib
import backend.services.crop_recommendation_service as svc
importlib.reload(svc)
# Import inside function to avoid caching issues
def get_recommend_crops():
    from backend.services.crop_recommendation_service import recommend_crops
    return recommend_crops

router = APIRouter(prefix="/api/v1/crop", tags=["crop"])


@router.post("/recommend", response_model=CropRecommendationResponse)
async def recommend_crops(
    request: CropRecommendationRequest,
    db: Session = Depends(get_db)
):
    """
    Recommend crops using the trained ML model (RandomForest).
    Takes soil and climate parameters, returns top-K crop predictions with confidence scores.
    """
    # Fill missing climate features with live weather for the district so the
    # XGBoost model always receives a complete payload. The weather service
    # falls back to historical averages if the API is unavailable.
    if request.temperature_c is None or request.humidity_percent is None:
        district = db.query(District).filter(District.id == request.district_id).first()
        if district:
            weather = await run_in_threadpool(get_live_weather, district.name)
            if request.temperature_c is None:
                request.temperature_c = weather["temperature"]
            if request.humidity_percent is None:
                request.humidity_percent = weather["humidity"]

    # Map API request fields to ML model feature names
    # API uses: n, p, k, temperature_c, humidity_percent, ph, rainfall_mm
    # ML expects: n, p, k, temperature, humidity, ph, rainfall
    input_features = {
        'N': request.n,
        'P': request.p,
        'K': request.k,
        'temperature': request.temperature_c,
        'humidity': request.humidity_percent,
        'ph': request.ph,
        'rainfall': request.rainfall_mm,
    }
    
    # Filter out None values - ML service will handle defaults
    input_features = {k: v for k, v in input_features.items() if v is not None}
    
    # Get ML-based recommendations
    ml_recommendations = get_recommend_crops()(input_features, top_k=request.top_k)
    
    # Convert ML response to API response format
    recommendations = []
    for rec in ml_recommendations:
        recommendations.append(CropRecommendationItem(
            crop_name=rec['crop_name'],
            confidence=round(rec['confidence'], 4),
            match_reasons=rec.get('match_reasons', []),
            expected_yield_tons_per_ha=None,  # ML model doesn't provide yield estimates
            season=None  # ML model doesn't provide season info
        ))
    
    return CropRecommendationResponse(
        district_id=request.district_id,
        soil_type=request.soil_type,
        rainfall_mm=request.rainfall_mm,
        recommendations=recommendations,
        version="xgboost_v2.0",
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
