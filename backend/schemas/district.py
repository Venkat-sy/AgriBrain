from pydantic import BaseModel, Field
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from .soil import SoilTypeResponse


class DistrictBase(BaseModel):
    name: str = Field(..., max_length=100)
    state: str = Field(..., max_length=100)
    state_code: Optional[str] = Field(None, max_length=10)
    district_code: Optional[str] = Field(None, max_length=20)


class DistrictCreate(DistrictBase):
    pass


class DistrictResponse(DistrictBase):
    id: int
    geometry: Optional[dict] = None  # GeoJSON
    centroid: Optional[dict] = None  # GeoJSON Point
    created_at: datetime

    class Config:
        from_attributes = True


class DistrictSoilTypeResponse(BaseModel):
    id: int
    district_id: int
    soil_type_id: int
    percentage: float
    is_predominant: bool
    soil_type: "SoilTypeResponse"

    class Config:
        from_attributes = True


class DistrictWithSoilResponse(DistrictResponse):
    soil_types: List["DistrictSoilTypeResponse"] = []

    class Config:
        from_attributes = True


# Resolve forward references
from .soil import SoilTypeResponse

DistrictSoilTypeResponse.model_rebuild()
DistrictWithSoilResponse.model_rebuild()