
"""
Cultivation Calendar Generator for AgriBrain.
"""

from datetime import date, timedelta
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class CalendarStage:
    stage_number: int
    name: str
    description: str
    start_date: date
    end_date: date
    day_range: str
    activities: List[str]

@dataclass
class CultivationCalendar:
    crop_name: str
    planned_start_date: date
    stages: List[CalendarStage]
    total_duration_days: int

DEFAULT_STAGES = [
    {"stage_number": 1, "name": "Land Prep & Sowing", "description": "Land preparation, tillage, and sowing/transplanting", "day_start": 0, "day_end": 15, "activities": ["Ploughing and harrowing", "Field leveling", "Basal fertilizer application", "Sowing/transplanting", "First irrigation (if needed)"]},
    {"stage_number": 2, "name": "Vegetative Growth & NPK Application", "description": "Early growth stage with nitrogen top-dressing", "day_start": 16, "day_end": 45, "activities": ["First weeding", "Top dressing - Nitrogen (1st split)", "Gap filling if needed", "Irrigation management", "Pest/disease monitoring"]},
    {"stage_number": 3, "name": "Flowering & Irrigation Window", "description": "Critical flowering stage requiring adequate moisture", "day_start": 46, "day_end": 75, "activities": ["Top dressing - Nitrogen (2nd split)", "Potassium application for grain filling", "Critical irrigation during flowering", "Pest/disease control", "Pollination support (if applicable)"]},
    {"stage_number": 4, "name": "Maturation & Harvest Window", "description": "Grain maturation and harvest preparation", "day_start": 76, "day_end": 120, "activities": ["Stop irrigation (allow drying)", "Monitor grain moisture", "Harvest planning", "Harvesting", "Post-harvest handling and storage"]}
]

CROP_STAGE_OVERRIDES = {
    "Rice": {"stage_1": {"day_end": 20, "activities": ["Puddling", "Transplanting", "Basal fertilizer", "Standing water maintenance"]}, "stage_2": {"day_end": 50, "activities": ["Weeding", "Top dressing N (tillering)", "Water management", "Pest monitoring"]}, "stage_3": {"day_end": 85, "activities": ["Panicle initiation", "Top dressing N (panicle)", "Critical irrigation", "Disease control"]}, "stage_4": {"day_end": 130, "activities": ["Grain filling", "Drain field", "Harvest", "Threshing"]}},
    "Wheat": {"stage_1": {"day_end": 15}, "stage_2": {"day_end": 50}, "stage_3": {"day_end": 85}, "stage_4": {"day_end": 125}},
    "Maize": {"stage_1": {"day_end": 15}, "stage_2": {"day_end": 45}, "stage_3": {"day_end": 75}, "stage_4": {"day_end": 110}},
    "Cotton": {"stage_1": {"day_end": 20}, "stage_2": {"day_end": 60}, "stage_3": {"day_end": 120}, "stage_4": {"day_end": 180}},
    "Sugarcane": {"stage_1": {"day_end": 30}, "stage_2": {"day_end": 120}, "stage_3": {"day_end": 270}, "stage_4": {"day_end": 365}},
}

def get_crop_stages(crop_name: str) -> List[Dict[str, Any]]:
    stages = [dict(stage) for stage in DEFAULT_STAGES]
    if crop_name in CROP_STAGE_OVERRIDES:
        overrides = CROP_STAGE_OVERRIDES[crop_name]
        for i, stage in enumerate(stages):
            override_key = f"stage_{stage['stage_number']}"
            if override_key in overrides:
                override = overrides[override_key]
                for key, value in override.items():
                    stage[key] = value
    return stages

def generate_cultivation_calendar(crop_name: str, planned_start_date: date, crop_duration_days: Optional[int] = None) -> CultivationCalendar:
    stages_def = get_crop_stages(crop_name)
    if crop_duration_days is None:
        crop_duration_days = max(stage["day_end"] for stage in stages_def)
    stages = []
    for stage_def in stages_def:
        start_date = planned_start_date + timedelta(days=stage_def["day_start"])
        end_date = planned_start_date + timedelta(days=stage_def["day_end"])
        max_end = planned_start_date + timedelta(days=crop_duration_days)
        if end_date > max_end:
            end_date = max_end
        stage = CalendarStage(stage_number=stage_def["stage_number"], name=stage_def["name"], description=stage_def["description"], start_date=start_date, end_date=end_date, day_range=f"Day {stage_def['day_start']}-{stage_def['day_end']}", activities=stage_def["activities"])
        stages.append(stage)
    calendar = CultivationCalendar(crop_name=crop_name, planned_start_date=planned_start_date, stages=stages, total_duration_days=crop_duration_days)
    logger.info(f"Generated calendar for {crop_name} starting {planned_start_date}")
    return calendar

def calendar_to_dict(calendar: CultivationCalendar) -> Dict[str, Any]:
    return {"crop_name": calendar.crop_name, "planned_start_date": calendar.planned_start_date.isoformat(), "total_duration_days": calendar.total_duration_days, "stages": [{"stage_number": stage.stage_number, "name": stage.name, "description": stage.description, "start_date": stage.start_date.isoformat(), "end_date": stage.end_date.isoformat(), "day_range": stage.day_range, "activities": stage.activities} for stage in calendar.stages]}

def parse_date(date_str: str) -> date:
    try:
        return date.fromisoformat(date_str)
    except ValueError:
        for fmt in ["%d/%m/%Y", "%d-%m-%Y", "%Y/%m/%d"]:
            try:
                return date.strptime(date_str, fmt)
            except ValueError:
                continue
        raise ValueError(f"Unable to parse date: {date_str}")