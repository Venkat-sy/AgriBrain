from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Literal
from datetime import datetime
from enum import Enum


class LookupMethod(str, Enum):
    EXACT = "exact"
    STATE_AVERAGE = "state_average"
    SOIL_AVERAGE = "soil_average"


class BaselineParametersRequest(BaseModel):
    district: str = Field(..., description="District name")
    state: str = Field(..., description="State name")
    soil_type: str = Field(..., description="Soil type (e.g., 'Black Soil (Regur)', 'Red Soil (Laterite)')")


class BaselineParametersResponse(BaseModel):
    """Response containing baseline agricultural parameters with lookup metadata."""
    # Core soil parameters
    n: float = Field(..., description="Nitrogen (kg/ha)")
    p: float = Field(..., description="Phosphorus (kg/ha)")
    k: float = Field(..., description="Potassium (kg/ha)")
    ph: float = Field(..., description="Soil pH")
    
    # Weather parameters
    temperature_c: float = Field(..., description="Average temperature (°C)")
    humidity_percent: float = Field(..., description="Average humidity (%)")
    rainfall_mm: float = Field(..., description="Annual rainfall (mm)")
    
    # Metadata
    district: str
    state: str
    soil_type: str
    lookup_method: LookupMethod = Field(..., description="Method used to obtain parameters")
    
    model_config = ConfigDict(protected_namespaces=())


class BaselineParametersStoreRequest(BaseModel):
    """Request to store/update baseline parameters for a district/soil combination."""
    district: str
    state: str
    soil_type: str
    n: float
    p: float
    k: float
    ph: float
    temperature_c: float
    humidity_percent: float
    rainfall_mm: float