from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from enum import Enum


class ActivityType(str, Enum):
    LAND_PREPARATION = "land_preparation"
    SOWING = "sowing"
    IRRIGATION = "irrigation"
    FERTILIZER_APPLICATION = "fertilizer_application"
    PEST_CONTROL = "pest_control"
    WEEDING = "weeding"
    HARVESTING = "harvesting"
    POST_HARVEST = "post_harvest"


class RoadmapActivity(BaseModel):
    id: int
    activity_type: ActivityType
    title: str
    description: Optional[str]
    start_date: date
    end_date: date
    estimated_cost: Optional[float]
    is_critical: bool
    depends_on: Optional[List[int]]  # IDs of preceding activities


class FarmingRoadmapResponse(BaseModel):
    crop_name: str
    district_id: int
    planting_date: date
    harvest_date: date
    total_duration_days: int
    activities: List[RoadmapActivity]
    total_estimated_cost: float
    generated_at: datetime


class RoadmapActivityCreate(BaseModel):
    activity_type: ActivityType
    title: str
    description: Optional[str]
    start_date: date
    end_date: date
    estimated_cost: Optional[float]
    is_critical: bool
    depends_on: Optional[List[int]]