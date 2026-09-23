from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime, date


class RainfallMonthResponse(BaseModel):
    id: int
    district_id: int
    year: int
    month: int
    rainfall_mm: float
    source: str
    created_at: datetime

    class Config:
        from_attributes = True


class RainfallHistoryResponse(BaseModel):
    district_id: int
    district_name: str
    records: List[RainfallMonthResponse]
    summary: dict  # total, avg, min, max per year


class RainfallForecastResponse(BaseModel):
    id: int
    district_id: int
    district_name: str
    forecast_date: date
    predicted_mm: float
    lower_bound_mm: Optional[float]
    upper_bound_mm: Optional[float]
    model_version: str
    created_at: datetime

    model_config = ConfigDict(protected_namespaces=())


class RainfallForecastListResponse(BaseModel):
    district_id: int
    district_name: str
    forecasts: List[RainfallForecastResponse]
    model_version: str
    generated_at: datetime