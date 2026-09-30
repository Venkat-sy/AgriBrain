from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime


class CropProfileResponse(BaseModel):
    id: int
    name: str
    common_name: Optional[str]
    category: Optional[str]
    season: Optional[str]
    suitable_soil_types: Optional[List[str]]
    ph_min: Optional[float]
    ph_max: Optional[float]
    rainfall_min_mm: Optional[float]
    rainfall_max_mm: Optional[float]
    temp_min_c: Optional[float]
    temp_max_c: Optional[float]
    n_requirement: Optional[float]
    p_requirement: Optional[float]
    k_requirement: Optional[float]
    spacing_cm: Optional[float]
    row_spacing_cm: Optional[float]
    duration_days: Optional[int]
    expected_yield_tons_per_ha: Optional[float]
    water_requirement_mm: Optional[float]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CropRecommendationRequest(BaseModel):
    district_id: int
    soil_type: str
    rainfall_mm: float
    temperature_c: Optional[float] = None
    humidity_percent: Optional[float] = None
    ph: Optional[float] = None
    n: Optional[float] = None
    p: Optional[float] = None
    k: Optional[float] = None
    top_k: int = Field(default=5, ge=1, le=10)


class CropRecommendationItem(BaseModel):
    crop_name: str
    confidence: float
    match_reasons: List[str]
    expected_yield_tons_per_ha: Optional[float]
    season: Optional[str]


class CropRecommendationResponse(BaseModel):
    district_id: int
    soil_type: str
    rainfall_mm: float
    recommendations: List[CropRecommendationItem]
    model_version: str
    generated_at: datetime

    model_config = ConfigDict(protected_namespaces=())


class CropCostResponse(BaseModel):
    id: int
    crop_id: int
    activity: str
    unit: str
    unit_cost: float
    quantity_per_ha: float
    region: str
    validity_start: Optional[datetime]
    validity_end: Optional[datetime]
    source: Optional[str]

    class Config:
        from_attributes = True


class CropPriceResponse(BaseModel):
    id: int
    crop_id: int
    market: Optional[str]
    price_per_ton: float
    price_date: datetime
    source: Optional[str]

    class Config:
        from_attributes = True