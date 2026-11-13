from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from enum import Enum


class SimulationStatus(str, Enum):
    DRAFT = "draft"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class SimulationRequest(BaseModel):
    district_id: int
    selected_crop: str
    land_area_ha: float = Field(..., gt=0)
    budget_inr: float = Field(..., gt=0)
    confirmed_soil_type: str
    rainfall_override_mm: Optional[float] = Field(default=None, ge=0)
    planting_month: Optional[int] = Field(default=None, ge=1, le=12)
    planting_season: Optional[str] = Field(default=None, description="Kharif, Rabi, Zaid, or Annual")
    planned_start_date: Optional[date] = Field(default=None, description="Planned start date for cultivation")


class CostBreakdownItem(BaseModel):
    activity: str
    unit: str
    unit_cost: float
    quantity: float
    total_cost: float


class SimulationResponse(BaseModel):
    # Inputs (echoed back)
    district_id: int
    district_name: str
    selected_crop: str
    land_area_ha: float
    budget_inr: float
    confirmed_soil_type: str
    rainfall_mm: float
    
    # Outputs
    plant_capacity: int
    cost_breakdown: List[CostBreakdownItem]
    total_cost_inr: float
    estimated_yield_tons: float
    estimated_yield_tons_per_ha: float
    market_value_inr: float
    net_profit_inr: float
    roi_percentage: float
    risk_level: RiskLevel
    risk_factors: List[str]
    
    # ML-based predictions
    ml_yield_prediction_tons_per_ha: Optional[float] = Field(default=None, description="Yield prediction from ML model (tons/ha)")
    ml_yield_prediction_tons: Optional[float] = Field(default=None, description="Total yield prediction from ML model (tons)")
    recommended_crops: Optional[List[Dict[str, Any]]] = Field(default=None, description="ML crop recommendations")
    
    # Metadata
    model_version: str
    generated_at: datetime

    model_config = ConfigDict(protected_namespaces=())


class SimulationResultResponse(BaseModel):
    id: int
    user_id: str
    district_id: int
    district_name: str
    selected_crop: str
    land_area_ha: float
    budget_inr: float
    confirmed_soil_type: str
    rainfall_override_mm: Optional[float]
    plant_capacity: int
    total_cost_inr: float
    cost_breakdown: List[Dict[str, Any]]
    estimated_yield_tons: float
    estimated_yield_tons_per_ha: float
    market_value_inr: float
    net_profit_inr: float
    roi_percentage: float
    risk_level: str
    risk_factors: List[str]
    farming_roadmap: List[Dict[str, Any]]
    status: SimulationStatus
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True, protected_namespaces=())


class SimulationListResponse(BaseModel):
    results: List[SimulationResultResponse]
    total: int
    page: int
    page_size: int