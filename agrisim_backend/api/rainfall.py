from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from agrisim_backend.core.config import get_db
from agrisim_backend.models import District, RainfallMonthly, RainfallForecast
from agrisim_backend.schemas import (
    RainfallHistoryResponse,
    RainfallForecastResponse,
    RainfallForecastListResponse,
    RainfallMonthResponse
)

router = APIRouter(prefix="/api/v1/rainfall", tags=["rainfall"])


@router.get("/history/{district_id}", response_model=RainfallHistoryResponse)
async def get_rainfall_history(
    district_id: int,
    start_year: Optional[int] = Query(None, ge=1900, le=2100),
    end_year: Optional[int] = Query(None, ge=1900, le=2100),
    db: Session = Depends(get_db)
):
    """Get historical monthly rainfall data for a district."""
    district = db.query(District).filter(District.id == district_id).first()
    if not district:
        raise HTTPException(status_code=404, detail="District not found")
    
    query = db.query(RainfallMonthly).filter(RainfallMonthly.district_id == district_id)
    
    if start_year:
        query = query.filter(RainfallMonthly.year >= start_year)
    if end_year:
        query = query.filter(RainfallMonthly.year <= end_year)
    
    records = query.order_by(RainfallMonthly.year, RainfallMonthly.month).all()
    
    # Build summary
    summary = {}
    for record in records:
        year = record.year
        if year not in summary:
            summary[year] = {"total_mm": 0, "months": 0, "min_mm": float('inf'), "max_mm": 0}
        summary[year]["total_mm"] += record.rainfall_mm
        summary[year]["months"] += 1
        summary[year]["min_mm"] = min(summary[year]["min_mm"], record.rainfall_mm)
        summary[year]["max_mm"] = max(summary[year]["max_mm"], record.rainfall_mm)
    
    for year in summary:
        summary[year]["avg_mm"] = round(summary[year]["total_mm"] / summary[year]["months"], 2)
        summary[year]["min_mm"] = round(summary[year]["min_mm"], 2) if summary[year]["min_mm"] != float('inf') else 0
        summary[year]["max_mm"] = round(summary[year]["max_mm"], 2)
    
    return RainfallHistoryResponse(
        district_id=district_id,
        district_name=district.name,
        records=[RainfallMonthResponse.model_validate(r) for r in records],
        summary=summary
    )


@router.get("/forecast/{district_id}", response_model=RainfallForecastListResponse)
async def get_rainfall_forecast(
    district_id: int,
    model_version: Optional[str] = Query(None),
    days_ahead: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """Get ML-generated rainfall forecast for a district."""
    district = db.query(District).filter(District.id == district_id).first()
    if not district:
        raise HTTPException(status_code=404, detail="District not found")
    
    # Get the latest model version if not specified
    if not model_version:
        latest_forecast = db.query(RainfallForecast).filter(
            RainfallForecast.district_id == district_id
        ).order_by(RainfallForecast.created_at.desc()).first()
        if latest_forecast:
            model_version = latest_forecast.model_version
    
    if not model_version:
        raise HTTPException(status_code=404, detail="No forecast available for this district")
    
    from datetime import datetime, timedelta
    start_date = datetime.utcnow().date()
    end_date = start_date + timedelta(days=days_ahead)
    
    query = db.query(RainfallForecast).filter(
        RainfallForecast.district_id == district_id,
        RainfallForecast.model_version == model_version,
        RainfallForecast.forecast_date >= start_date,
        RainfallForecast.forecast_date <= end_date
    ).order_by(RainfallForecast.forecast_date)
    
    forecasts = query.all()
    
    return RainfallForecastListResponse(
        district_id=district_id,
        district_name=district.name,
        forecasts=[RainfallForecastResponse.model_validate(f) for f in forecasts],
        model_version=model_version,
        generated_at=datetime.utcnow()
    )


@router.get("/seasonal/{district_id}")
async def get_seasonal_rainfall(
    district_id: int,
    year: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    """Get seasonal (kharif/rabi/zaid) rainfall summary for a district."""
    district = db.query(District).filter(District.id == district_id).first()
    if not district:
        raise HTTPException(status_code=404, detail="District not found")
    
    query = db.query(RainfallMonthly).filter(RainfallMonthly.district_id == district_id)
    if year:
        query = query.filter(RainfallMonthly.year == year)
    
    records = query.all()
    
    # Define seasons (Indian agricultural seasons)
    kharif_months = [6, 7, 8, 9, 10]  # Jun-Oct
    rabi_months = [11, 12, 1, 2, 3, 4]  # Nov-Apr
    zaid_months = [5]  # May (or sometimes Mar-May)
    
    seasonal_data = {}
    for record in records:
        if record.month in kharif_months:
            season = "kharif"
        elif record.month in rabi_months:
            season = "rabi"
        elif record.month in zaid_months:
            season = "zaid"
        else:
            continue
        
        year_key = record.year
        if year_key not in seasonal_data:
            seasonal_data[year_key] = {"kharif": 0, "rabi": 0, "zaid": 0}
        
        seasonal_data[year_key][season] += record.rainfall_mm
    
    return {
        "district_id": district_id,
        "district_name": district.name,
        "seasonal_rainfall": seasonal_data
    }