from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime


class SoilTypeResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    typical_crops: Optional[List[str]]
    properties: Optional[Dict[str, Any]]
    color_hex: Optional[str]

    class Config:
        from_attributes = True


class DistrictSoilTypeResponse(BaseModel):
    id: int
    district_id: int
    soil_type_id: int
    percentage: float
    is_predominant: bool
    soil_type: SoilTypeResponse

    class Config:
        from_attributes = True


class DistrictSoilResponse(BaseModel):
    district_id: int
    district_name: str
    soil_types: List[DistrictSoilTypeResponse]


class SoilImageRequest(BaseModel):
    image_base64: str
    lat: Optional[float] = None
    lon: Optional[float] = None


class SoilImageResponse(BaseModel):
    id: int
    user_id: str
    predicted_soil: str
    confidence: float
    user_confirmed_soil: Optional[str]
    model_version: str
    created_at: datetime

    model_config = ConfigDict(protected_namespaces=())


class SoilImageFeedbackRequest(BaseModel):
    result_id: int
    confirmed_soil: str